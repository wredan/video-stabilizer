import cv2
import numpy as np

class PostProcessing:

    def __init__(self) -> None:
        pass

    def shift_frames(self, frames, global_correct_motion_vectors):
        """
        Shifts each frame according to the corresponding global motion correction vector and intensity.
        Uses the OpenCV function cv2.warpAffine for the actual shifting.
        """
        shifted_frames = []
        for frame, correction_vector in zip(frames, global_correct_motion_vectors):
            M = np.float32([[1, 0, correction_vector[0]], [0, 1, correction_vector[1]]])
            shifted_frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
            shifted_frames.append(shifted_frame)
        return shifted_frames


    def crop_frames(self, frames, max_shift = None, global_correct_motion_vectors = None):
        """
        Crops each frame to remove the black borders created due to shifting.
        """
        cropped_frames = []

        if max_shift is None:
            max_shift = max(max(abs(correction_vector[0]), abs(correction_vector[1])) 
                            for correction_vector in global_correct_motion_vectors)            
            self.max_shift = max_shift

        for frame in frames:
            start_x = int(max_shift)
            start_y = int(max_shift)
            end_x = frame.shape[1] - int(max_shift)
            end_y = frame.shape[0] - int(max_shift)
            cropped_frame = frame[start_y:end_y, start_x:end_x]

            cropped_frames.append(cropped_frame)

        return cropped_frames
