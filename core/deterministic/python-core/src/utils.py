import cv2
import numpy as np
import matplotlib.pyplot as plt

class DFD:
    def __init__(self):
        pass
    
    def mad(m1,m2):
        return np.absolute(np.subtract(m1,m2)).mean()

    def mse(m1,m2):
        return np.square(np.subtract(m1,m2)).mean()

def opencv_show_image(win_name, img):
    cv2.namedWindow(win_name, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(win_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def opencv_imwrite(filename, img):
    cv2.imwrite(filename, img, [cv2.IMWRITE_PNG_COMPRESSION, 9])


def plot_global_corrected_motion_vector(global_corrected_vector, width, height):
    global_corrected_vect_frames = []
    for corrected_vector in global_corrected_vector:
        frame = single_step_plot(corrected_vector, height, width)
        global_corrected_vect_frames.append(frame)
    
    return global_corrected_vect_frames

def single_step_plot(corrected_vector, height, width):
    scale_factor = 1
    frame = np.zeros((height, width), np.uint8)
    intensity = 255
    x2, y2 = int(corrected_vector[0] * scale_factor + width / 2), int(corrected_vector[1] * scale_factor + height / 2)
    cv2.arrowedLine(frame, (width // 2, height // 2), (x2, y2), intensity, 1,tipLength=0.3)
    return frame

def plot_complex_mat(data, path):
    x_values = data[:, 0, 0]  # Real part of x motion
    y_values = data[:, 1, 0]  # Real part of y motion

    # Compute the magnitude (Amplitude) of the motion
    magnitude = np.sqrt(x_values**2 + y_values**2)

    # Compute the phase (angle) of the motion
    phase = np.arctan2(y_values, x_values)

    fig, axs = plt.subplots(2)

    # Plot the amplitude
    axs[0].plot(magnitude, label='Amplitude')
    axs[0].set_title('Amplitude')
    axs[0].legend()

    # Plot the phase
    axs[1].plot(phase, label='Phase', color='r')
    axs[1].set_title('Phase')
    axs[1].legend()

    fig.tight_layout()

    plt.savefig(path)
    plt.close()
