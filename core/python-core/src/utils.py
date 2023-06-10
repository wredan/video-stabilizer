import cv2
import numpy as np
import matplotlib.pyplot as plt

class DFD:
    def __init__(self):
        pass
    
    # def mad(m1,m2):
    #     return np.absolute(np.subtract(m1,m2)).mean()

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

def plot_absolute_frame_position(accumulated_motion, accumulated_filtered_motion, path, scale_factor = 0.0):
    Xx_values = accumulated_motion[:, 0]
    Xy_values = accumulated_motion[:, 1]
    Xx_filtered_values = accumulated_filtered_motion[:, 0]
    Xy_filtered_values = accumulated_filtered_motion[:, 1]

    min_value = min(min(Xx_values), min(Xy_values), min(Xx_filtered_values), min(Xy_filtered_values))
    max_value = max(max(Xx_values), max(Xy_values), max(Xx_filtered_values), max(Xy_filtered_values))

    plt.plot(Xx_values, label='Xx')
    plt.plot(Xy_values, label='Xy')
    plt.plot(Xx_filtered_values, label='Xx_fil')
    plt.plot(Xy_filtered_values, label='Xy_fil')
    
    plt.ylim(min_value - scale_factor * abs(min_value), max_value + scale_factor * abs(max_value))
    plt.legend()
    plt.xlabel('Frame number')
    plt.ylabel('Position')
    plt.title('Original and DFT domain low-pass filtered absolute frame positions')

    plt.savefig(path)
    plt.close()

def plot_compare_motion(origin_accumulated_motion, filtered_accumulated_motion, path, scale_factor = 0.0):
    Xx_values = origin_accumulated_motion[:, 0]
    Xy_values = origin_accumulated_motion[:, 1]
    Xx_filtered_values = filtered_accumulated_motion[:, 0]
    Xy_filtered_values = filtered_accumulated_motion[:, 1]

    min_value = min(min(Xx_values), min(Xy_values), min(Xx_filtered_values), min(Xy_filtered_values))
    max_value = max(max(Xx_values), max(Xy_values), max(Xx_filtered_values), max(Xy_filtered_values))

    plt.plot(Xx_values, label='Xx_cropped_origin')
    plt.plot(Xy_values, label='Xy_cropped_origin')
    plt.plot(Xx_filtered_values, label='Xx_cropped_filtered')
    plt.plot(Xy_filtered_values, label='Xy_cropped_filtered')
    
    plt.ylim(min_value - scale_factor * abs(min_value), max_value + scale_factor * abs(max_value))
    plt.legend()
    plt.xlabel('Frame number')
    plt.ylabel('Position')
    plt.title('Cropped original and Cropped Filtered absolute frame positions')

    plt.savefig(path)
    plt.close()

def plot_global_corrected_motion(global_corrected_motion_vectors, path, scale_factor = 0.0):
    x_motion_vectors = [vector[0] for vector in global_corrected_motion_vectors]
    y_motion_vectors = [vector[1] for vector in global_corrected_motion_vectors]

    min_value = min(min(x_motion_vectors), min(y_motion_vectors))
    max_value = max(max(x_motion_vectors), max(y_motion_vectors))

    plt.plot(x_motion_vectors, label='Vxc')
    plt.plot(y_motion_vectors, label='Vyc')
    plt.ylim(min_value - scale_factor * abs(min_value), max_value + scale_factor * abs(max_value))
    plt.legend()
    plt.xlabel('Frame number')
    plt.ylabel('Motion vector')
    plt.title('Motion vectors for FPS stabilised')

    plt.savefig(path)
    plt.close()