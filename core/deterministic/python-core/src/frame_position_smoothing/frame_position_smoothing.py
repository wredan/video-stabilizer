import numpy as np
import cv2
from config.config import ConfigParameters
import src.utils as utils
class FramePositionSmoothing:

    def __init__(self, configParameters: ConfigParameters) -> None:
        self.configParameters = configParameters


    def _forward_dft(self, global_motion_vector):
        # Calcola la trasformata di Fourier
        rows, cols = global_motion_vector.shape[:2]
        data = np.zeros((rows, cols, 2), np.float32)
        data = cv2.dft(global_motion_vector, flags=cv2.DFT_COMPLEX_OUTPUT)
        return data

    def _calculate_sigma(self, data, filter_intensity):
        rows, cols = data.shape[:2]

        # Convert Mat to Vec<f32>
        frequencies = np.zeros((rows * cols), np.float32)
        for i in range(rows):
            for j in range(cols):
                v = data[i, j]
                frequencies[i * cols + j] = np.sqrt(v[0]**2 + v[1]**2)

        # Calculate mean
        mean = np.mean(frequencies)

        # Calculate standard deviation
        std_dev = np.std(frequencies)

        # Calculate sigma based on filter_intensity
        sigma = std_dev * (100.0 - filter_intensity) / 100.0

        return sigma


    def _gaussian_low_pass(self, sigma, rows, cols):
        # create x and y ranges
        x = cv2.getGaussianKernel(cols, sigma)
        y = cv2.getGaussianKernel(rows, sigma)
        
        # create 2d filter
        filter = np.outer(y, x)
        
        # convert filter to complex for compatibility with dft output
        filter_complex = np.zeros((rows, cols, 2), np.float32)
        filter_complex[:, :, 0] = filter

        return filter_complex


    def _low_pass_filter(self, data, sigma):
        # Apply the gaussian filter
        rows, cols = data.shape[:2]
        filter = self._gaussian_low_pass(sigma, rows, cols)
        filtered_data = cv2.mulSpectrums(data, filter, flags=0)
        return filtered_data


    def _inverse_dft(self, filtered_data):
        # Calculate the inverse DFT
        rows, cols = filtered_data.shape[:2]
        inverse_filtered = np.zeros((rows, cols, 2), np.float32)
        inverse_filtered = cv2.idft(filtered_data, flags=cv2.DFT_COMPLEX_OUTPUT)
        return inverse_filtered

    def _correction_vector(self, global_motion_vector, inverse_filtered_data):
        # Calculate the correction vector
        delta_x, delta_y = global_motion_vector
        # print(inverse_filtered_data[0, 0])
        estimated_delta_x = inverse_filtered_data[0, 0]
        estimated_delta_y = inverse_filtered_data[1, 0]
        return (estimated_delta_x - delta_x, estimated_delta_y - delta_y)


    def global_correction_motion_vectors(self, global_motion_vectors, filter_intensity):
        # Step 1: Calculate the accumulated motion vectors
        accumulated_motion = np.zeros((len(global_motion_vectors), 2), dtype=np.float32)
        for i, global_motion_vector in enumerate(global_motion_vectors):
            if i == 0:
                accumulated_motion[i] = global_motion_vector
            else:
                accumulated_motion[i] = accumulated_motion[i - 1] + global_motion_vector

        # Step 2: Convert the accumulated motion vectors to a Mat and apply DFT, LPF, and inverse DFT

        fourier_transform = self._forward_dft(accumulated_motion)
        print(accumulated_motion.shape)
        print(fourier_transform.shape)

        sigma = self._calculate_sigma(fourier_transform, filter_intensity)
        print("SIGMA: ", sigma)

        filtered_data = self._low_pass_filter(fourier_transform, sigma)

        inverse_filtered_data = self._inverse_dft(filtered_data)

        utils.plot_complex_mat(fourier_transform, self.configParameters.base_path + "/Fourier Transform.png")
        utils.plot_complex_mat(filtered_data, self.configParameters.base_path + "/Filtered Data.png")
        
        # Step 3: Calculate the correction vectors
        global_corrected_motion_vectors = []
        for i in range(len(accumulated_motion)):
            correction_vector = self._correction_vector(accumulated_motion[i], inverse_filtered_data[i])
            global_corrected_motion_vectors.append(correction_vector)
        
        return global_corrected_motion_vectors



    def shift_frames(self, frames, global_correct_motion_vectors, intensity):
        """
        Shifts each frame according to the corresponding global motion correction vector and intensity.
        Uses the OpenCV function cv2.warpAffine for the actual shifting.
        """
        shifted_frames = []
        for frame, correction_vector in zip(frames, global_correct_motion_vectors):
            M = np.float32([[1, 0, correction_vector[0]*intensity], [0, 1, correction_vector[1]*intensity]])
            shifted_frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
            shifted_frames.append(shifted_frame)
        return shifted_frames
