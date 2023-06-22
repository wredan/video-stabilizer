import logging
import os
from fastapi import WebSocket
import numpy as np
from scipy import ndimage
from config.config_video import ConfigVideoParameters
import src.utils as utils
from src.request_handler.json_encoder import JsonEncoder
class FramePositionSmoothing:

    def __init__(self, config_parameters: ConfigVideoParameters, client_dir: str) -> None:
        self.client_dir = client_dir
        self.config_parameters = config_parameters

    def _correction_vector(self, global_motion_vector, inverse_filtered_data):
        # Calculate the correction vector
        delta_x, delta_y = global_motion_vector
        estimated_delta_x, estimated_delta_y = inverse_filtered_data
        return (estimated_delta_x - delta_x, estimated_delta_y - delta_y)

    def _gaussian_filtering(self, accumulated_motion):
        # Calculate the length of padding, which might be a percentage of the signal length
        pad_len = int(self.config_parameters.padding_percentage * len(accumulated_motion))

        # Create padding values
        start_pad = np.ones((pad_len, 2)) * accumulated_motion[0]
        end_pad = np.ones((pad_len, 2)) * accumulated_motion[-1]

        # Add padding values to the beginning and end of the signal
        accumulated_motion_padded = np.vstack((start_pad, accumulated_motion, end_pad))

        # Proceed with the Fourier transform as before
        input_x = np.fft.fft(accumulated_motion_padded[:, 0])
        input_y = np.fft.fft(accumulated_motion_padded[:, 1])
        
        # Calculate the Interquartile Range (IQR) for each set of data
        # input_x_IQR = np.percentile(input_x.real, 75) - np.percentile(input_x.real, 25)
        # input_y_IQR = np.percentile(input_y.real, 75) - np.percentile(input_y.real, 25)
        # sigmaX = self.config_parameters.stabilization_parameters.filter_intensity / 100 * input_x_IQR
        # sigmaY = self.config_parameters.stabilization_parameters.filter_intensity / 100 * input_y_IQR

        # Calculate sigma based on std
        # input_x_std_dev = np.std(input_x.real)
        # input_y_std_dev = np.std(input_y.real)
        # sigmaX = self.config_parameters.stabilization_parameters.filter_intensity / 100 * input_x_std_dev
        # sigmaY = self.config_parameters.stabilization_parameters.filter_intensity / 100 * input_y_std_dev

        # Give straight value of filter intensity to sigma
        sigmaX = self.config_parameters.stabilization_parameters.filter_intensity
        sigmaY = self.config_parameters.stabilization_parameters.filter_intensity

        filtered_x = ndimage.fourier_gaussian(input_x, sigma=sigmaX)
        filtered_y = ndimage.fourier_gaussian(input_y, sigma=sigmaY)

        inverse_filtered_data_x = np.real(np.fft.ifft(filtered_x))
        inverse_filtered_data_y = np.real(np.fft.ifft(filtered_y))

        # Remove padding values from the filtered signal
        inverse_filtered_data_x = inverse_filtered_data_x[pad_len:-pad_len]
        inverse_filtered_data_y = inverse_filtered_data_y[pad_len:-pad_len]

        inverse_filtered_data = np.column_stack((inverse_filtered_data_x, inverse_filtered_data_y))
        return inverse_filtered_data

    async def global_correction_motion_vectors(self, global_motion_vectors, websocket: WebSocket):
        message = "Frame Position Smoothing running..."
        logger = logging.getLogger('logger')
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_frame_position_smoothing_json(message))
        # Step 1: Calculate the accumulated motion vectors
        accumulated_motion = self.get_accumulated_motion_vec(global_motion_vectors)

        # Step 2: apply fft, LPF, and inverse fft
        inverse_filtered_data = self._gaussian_filtering(accumulated_motion)
        utils.plot_absolute_frame_position(accumulated_motion, 
                                            inverse_filtered_data, 
                                            os.path.join(self.config_parameters.base_path, self.client_dir, "absolute_frame_position.png"),
                                            self.config_parameters.plot_scale_factor)

        # Step 3: Calculate the correction vectors
        global_corrected_motion_vectors = [ self._correction_vector(acc_motion, inv_filtered_data) for acc_motion, inv_filtered_data in zip(accumulated_motion, inverse_filtered_data)]
        utils.plot_global_corrected_motion(global_corrected_motion_vectors, 
                                           os.path.join(self.config_parameters.base_path, self.client_dir, "global_corrected_motion_vectors.png"),
                                           self.config_parameters.plot_scale_factor)

        return global_corrected_motion_vectors
    
    def get_accumulated_motion_vec(self, global_motion_vectors):
        global_motion_vectors = np.array(global_motion_vectors, dtype=np.float32)
        accumulated_motion = np.cumsum(global_motion_vectors, axis=0)
        return accumulated_motion