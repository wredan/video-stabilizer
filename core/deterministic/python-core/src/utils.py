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
    complex_data = data.ravel()
    x_values = complex_data.real
    y_values = complex_data.imag

    x_mean = np.mean(x_values)
    y_mean = np.mean(y_values)

    x_std_dev = np.std(x_values)
    y_std_dev = np.std(y_values)

    x_min = x_mean - 2.0 * x_std_dev
    x_max = x_mean + 2.0 * x_std_dev
    y_min = y_mean - 2.0 * y_std_dev
    y_max = y_mean + 2.0 * y_std_dev

    plt.figure(figsize=(6.4, 4.8))
    plt.title(path)
    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])
    plt.xlabel("Frequency")
    plt.ylabel("Amplitude")
    plt.scatter(x_values, y_values, color='b', s=1)
    plt.savefig(path)
    plt.close()