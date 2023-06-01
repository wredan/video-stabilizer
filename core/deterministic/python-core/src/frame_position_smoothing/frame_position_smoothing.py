import numpy as np
import cv2
from config.config import ConfigParameters
import src.utils as utils
class FramePositionSmoothing:

    def __init__(self, config_parameters: ConfigParameters) -> None:
        self.config_parameters = config_parameters

    def _forward_dft(self, global_motion_vector):
        # Calcola la trasformata di Fourier
        data = cv2.dft(global_motion_vector, flags=cv2.DFT_REAL_OUTPUT)
        return data

    def _calculate_sigma(self, data, filter_intensity):
        # Calculate standard deviation
        std_dev = np.std(data)

        # Calculate sigma based on filter_intensity
        sigma = std_dev * (100.0 - filter_intensity) / 100.0

        return sigma


    def _gaussian_low_pass(self, sigma, rows, cols):
        # create x and y ranges
        x = cv2.getGaussianKernel(cols, sigma)
        y = cv2.getGaussianKernel(rows, sigma)
        
        # create 2d filter
        filter = np.outer(y, x)

        return filter

    def _low_pass_filter(self, data, sigma):
        # Apply the gaussian filter
        rows, cols = data.shape
        filter = self._gaussian_low_pass(sigma, rows, cols)
        print("data", data.shape)
        print("filter", filter.shape)
        filtered_data = data * filter
        return filtered_data


    def _inverse_dft(self, filtered_data):
        # Calculate the inverse DFT
        inverse_filtered = cv2.idft(filtered_data, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        return inverse_filtered


    def _correction_vector(self, global_motion_vector, inverse_filtered_data):
        # Calculate the correction vector
        delta_x, delta_y = global_motion_vector
        estimated_delta_x, estimated_delta_y = inverse_filtered_data
        return (estimated_delta_x - delta_x, estimated_delta_y - delta_y)

    def global_correction_motion_vectors(self, global_motion_vectors, filter_intensity):
        # Step 1: Calculate the accumulated motion vectors
        global_motion_vectors = np.array(global_motion_vectors, dtype=np.float32)
        accumulated_motion = np.cumsum(global_motion_vectors, axis=0)

        # Step 2: Convert the accumulated motion vectors to a Mat and apply DFT, LPF, and inverse DFT

        fourier_transform = self._forward_dft(accumulated_motion)
        print("accumulated_motion: ", accumulated_motion.shape)
        print("fourier_transform: ", fourier_transform.shape)

        sigma = self._calculate_sigma(fourier_transform, filter_intensity)
        print("SIGMA: ", sigma)

        filtered_data = self._low_pass_filter(fourier_transform, sigma)
        print("filtered_data: ", filtered_data.shape)

        inverse_filtered_data = self._inverse_dft(filtered_data)
        print("inverse_filtered_data: ", inverse_filtered_data.shape)

        # utils.plot_complex_mat(fourier_transform, self.config_parameters.base_path + "/Fourier Transform.html")
        # utils.plot_complex_mat(filtered_data, self.config_parameters.base_path + "/Filtered Data.html")
        
        # Step 3: Calculate the correction vectors
        accumulated_inverse_filtered_data = np.cumsum(inverse_filtered_data, axis=0)
        utils.plot_absolute_frame_position(accumulated_motion, inverse_filtered_data, self.config_parameters.base_path + "/absolute_frame_position.png", self.config_parameters.plot_scale_factor)

        global_corrected_motion_vectors = []
        for i in range(len(accumulated_motion)):
            correction_vector = self._correction_vector(accumulated_motion[i], inverse_filtered_data[i])
            global_corrected_motion_vectors.append(correction_vector)

        
        utils.plot_global_corrected_motion(global_corrected_motion_vectors, self.config_parameters.base_path + "/global_corrected_motion_vectors.png", self.config_parameters.plot_scale_factor)

        return global_corrected_motion_vectors