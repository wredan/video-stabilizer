import numpy as np
import cv2
from scipy import ndimage
from config.config import ConfigParameters
import src.utils as utils
class FramePositionSmoothing:

    def __init__(self, config_parameters: ConfigParameters) -> None:
        self.config_parameters = config_parameters

    def _correction_vector(self, global_motion_vector, inverse_filtered_data):
        # Calculate the correction vector
        delta_x, delta_y = global_motion_vector
        estimated_delta_x, estimated_delta_y = inverse_filtered_data
        return (estimated_delta_x - delta_x, estimated_delta_y - delta_y)

    def _filtering(self, accumulated_motion):
        input_x = np.fft.fft(accumulated_motion[:, 0])
        input_y = np.fft.fft(accumulated_motion[:, 1])
        filtered_x = ndimage.fourier_gaussian(input_x, sigma=self.config_parameters.filter_intensity)
        filtered_y = ndimage.fourier_gaussian(input_y, sigma=self.config_parameters.filter_intensity)
        inverse_filtered_data_x = np.real(np.fft.ifft(filtered_x))
        inverse_filtered_data_y = np.real(np.fft.ifft(filtered_y))
        inverse_filtered_data = np.column_stack((inverse_filtered_data_x, inverse_filtered_data_y))
        return inverse_filtered_data
    
    def global_correction_motion_vectors(self, global_motion_vectors):
        # Step 1: Calculate the accumulated motion vectors
        global_motion_vectors = np.array(global_motion_vectors, dtype=np.float32)
        accumulated_motion = np.cumsum(global_motion_vectors, axis=0)

        # Step 2: apply fft, LPF, and inverse fft
        inverse_filtered_data = self._filtering(accumulated_motion)
        utils.plot_absolute_frame_position(accumulated_motion, inverse_filtered_data, self.config_parameters.base_path + "/absolute_frame_position.png", self.config_parameters.plot_scale_factor)

        # Step 3: Calculate the correction vectors
        global_corrected_motion_vectors = [ self._correction_vector(acc_motion, inv_filtered_data) for acc_motion, inv_filtered_data in zip(accumulated_motion, inverse_filtered_data)]
        utils.plot_global_corrected_motion(global_corrected_motion_vectors, self.config_parameters.base_path + "/global_corrected_motion_vectors.png", self.config_parameters.plot_scale_factor)

        return global_corrected_motion_vectors