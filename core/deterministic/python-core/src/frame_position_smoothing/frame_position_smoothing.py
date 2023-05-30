import numpy as np
import cv2


def forward_dft(global_motion_vector):
    """Computes the Fourier Transform of the input."""
    return cv2.dft(global_motion_vector, flags=cv2.DFT_COMPLEX_OUTPUT)


def gaussian_low_pass(sigma, rows, cols):
    """
    Creates a 2D Gaussian low pass filter.
    The intensity of the filter decreases with the distance from the center.
    """
    filter = np.zeros((rows, cols, 2), dtype=np.float32)
    total = 0.0
    d = 2.0 * sigma * sigma

    center_x = cols // 2
    center_y = rows // 2

    for y in range(rows):
        for x in range(cols):
            dx = x - center_x
            dy = y - center_y
            value = np.exp(-(dx*dx + dy*dy) / d)
            filter[y, x] = [value, 0.0]
            total += value

    # Normalize filter so it sums to 1
    filter[:, :, 0] /= total

    print("Gaussian filter: ", filter)

    return filter


def low_pass_filter(data, sigma):
    """Applies the Gaussian low pass filter to the input data."""
    filter = gaussian_low_pass(sigma, data.shape[0], data.shape[1])
    return cv2.mulSpectrums(data, np.dstack([filter]*2), flags=0)


def inverse_dft(filtered_data):
    """Computes the inverse Fourier Transform of the input."""
    return cv2.idft(filtered_data)


def correction_vector(global_motion_vector, inverse_filtered_data, i):
    """Calculates the correction vector for the global motion."""
    estimated_delta = inverse_filtered_data[i, 0]
    return estimated_delta[0] - global_motion_vector[0], estimated_delta[1] - global_motion_vector[1]


def calculate_sigma(data, filter_intensity):
    """
    Calculates sigma for the Gaussian filter based on the input data and filter intensity.
    The formula used is the same as in your original Rust code.
    """
    frequencies = np.abs(data)
    std_dev = np.std(frequencies)
    sigma = std_dev * (100.0 - filter_intensity) / 100.0
    return sigma


def global_correction_motion_vectors(global_motion_vectors, filter_intensity):
    """Applies Fourier Transform, low pass filter and inverse Fourier Transform to the accumulated global motion vectors."""
    accumulated_motion = np.cumsum(global_motion_vectors, axis=0)
    data = accumulated_motion.astype(np.float32)
    fourier_transform = forward_dft(data)
    sigma = calculate_sigma(fourier_transform, filter_intensity)
    filtered_data = low_pass_filter(fourier_transform, sigma)
    inverse_filtered_data = inverse_dft(filtered_data)
    corrected_motion_vectors = [correction_vector(acc, inverse_filtered_data, i)
                                for i, acc in enumerate(accumulated_motion)]
    return corrected_motion_vectors


def shift_frames(frames, global_correct_motion_vectors, intensity):
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
