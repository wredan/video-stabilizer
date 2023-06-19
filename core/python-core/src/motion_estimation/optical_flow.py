import numpy as np
import cv2
from config.config_video import ConfigVideoParameters

class OpticalFlow:
    def __init__(self, config_parameters: ConfigVideoParameters):
        # Parameters
        self.config_parameters = config_parameters

        params = self.config_parameters.stabilization_parameters.motion_estimation.optical_flow
        self.feature_params = dict(maxCorners=params.feature_params.max_corners,
                           qualityLevel=params.feature_params.quality_level,
                           minDistance=params.feature_params.min_distance,
                           blockSize=params.feature_params.block_size)

        self.lk_params = dict(winSize=params.lk_params.win_size,
                            maxLevel=params.lk_params.max_level,
                            criteria=params.lk_params.criteria)
        
        # Frames
        self.anchor = None
        self.target = None
        self.features = None

    def step(self, anchor, target): 
        self.anchor = anchor
        self.target = target

        if self.features is None:
            self.features = cv2.goodFeaturesToTrack(self.anchor, mask=None, **self.feature_params)

        flow, st, err = cv2.calcOpticalFlowPyrLK(self.anchor, self.target, self.features, None, **self.lk_params)

        if flow is None or np.count_nonzero(st) < self.config_parameters.stabilization_parameters.motion_estimation.optical_flow.feature_params.min_feature_threshold:
            self.features = cv2.goodFeaturesToTrack(self.anchor, mask=None, **self.feature_params)
            flow, st, err = cv2.calcOpticalFlowPyrLK(self.anchor, self.target, self.features, None, **self.lk_params)

        # Select good points
        good_new = flow[st==1]
        good_old = self.features[st==1]

        # Update features for next frame
        self.features = good_new.reshape(-1, 1, 2)

        global_motion_vec = self.frame_global_motion_vector(good_old, good_new)

        if self.config_parameters.demo:
            frame_motion_field = self.plot_motion_field(good_old, good_new)
            frame_global_motion_vector = self.plot_global_motion_vector(global_motion_vec)
            return global_motion_vec, None, frame_motion_field, frame_global_motion_vector
        else:
            return global_motion_vec, None, None, None


    def plot_motion_field(self, good_old, good_new): 
        # Construct the motion field from motion-vectors
        frame = np.zeros_like(self.anchor)
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            frame = cv2.line(frame, (int(a), int(b)), (int(c), int(d)), 255, 2)
            frame = cv2.circle(frame, (int(a), int(b)), 2, 255, -1)
        return frame

    def plot_global_motion_vector(self, global_motion_vec):
        frame = np.zeros_like(self.anchor)
        intensity = 255
        x2, y2 = int(global_motion_vec[0] + frame.shape[1] / 2), int(global_motion_vec[1] + frame.shape[0] / 2)
        cv2.arrowedLine(frame, (frame.shape[1] // 2, frame.shape[0] // 2), (x2, y2), intensity, 2, 8, 0, 0.3)
        return frame

    def frame_global_motion_vector(self, good_old, good_new):
        motion_vectors = good_new - good_old
        avg_motion_vector = np.mean(motion_vectors, axis=0)
        return avg_motion_vector
