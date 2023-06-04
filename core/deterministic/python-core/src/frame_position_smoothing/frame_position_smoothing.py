import os
from fastapi import WebSocket
import numpy as np
from scipy import ndimage
from config.config_video import ConfigVideoParameters
import src.utils as utils
from src.request_handler.json_encoder import init_frame_position_smoothing_json
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
        input_x = np.fft.fft(accumulated_motion[:, 0])
        input_y = np.fft.fft(accumulated_motion[:, 1])
        filtered_x = ndimage.fourier_gaussian(input_x, sigma=self.config_parameters.filter_intensity)
        filtered_y = ndimage.fourier_gaussian(input_y, sigma=self.config_parameters.filter_intensity)
        inverse_filtered_data_x = np.real(np.fft.ifft(filtered_x))
        inverse_filtered_data_y = np.real(np.fft.ifft(filtered_y))
        inverse_filtered_data = np.column_stack((inverse_filtered_data_x, inverse_filtered_data_y))
        return inverse_filtered_data

    async def global_correction_motion_vectors(self, global_motion_vectors, websocket: WebSocket):
        message = "Frame Position Smoothing running..."
        print(message)
        await websocket.send_json(init_frame_position_smoothing_json(message))
        # Step 1: Calculate the accumulated motion vectors
        accumulated_motion = self.get_accumulated_motion_vec(global_motion_vectors)

        # Step 2: apply fft, LPF, and inverse fft
        inverse_filtered_data = self._gaussian_filtering(accumulated_motion)
        if self.config_parameters.debug_mode:
            utils.plot_absolute_frame_position(accumulated_motion, 
                                            inverse_filtered_data, 
                                            os.path.join(self.config_parameters.base_path, self.client_dir, "absolute_frame_position.png"),
                                            self.config_parameters.plot_scale_factor)

        # Step 3: Calculate the correction vectors
        global_corrected_motion_vectors = [ self._correction_vector(acc_motion, inv_filtered_data) for acc_motion, inv_filtered_data in zip(accumulated_motion, inverse_filtered_data)]
        if self.config_parameters.debug_mode:
            utils.plot_global_corrected_motion(global_corrected_motion_vectors, 
                                           os.path.join(self.config_parameters.base_path, self.client_dir, "global_corrected_motion_vectors.png"),
                                           self.config_parameters.plot_scale_factor)

        return global_corrected_motion_vectors
    
    def get_accumulated_motion_vec(self, global_motion_vectors):
        global_motion_vectors = np.array(global_motion_vectors, dtype=np.float32)
        accumulated_motion = np.cumsum(global_motion_vectors, axis=0)
        return accumulated_motion