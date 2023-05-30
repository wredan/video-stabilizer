from tqdm import tqdm
from src.video import Video
from .block_matching import BlockMatching
from config.config import ConfigParameters

class MotionEstimation:
    def __init__(self, video: Video, config_parameters: ConfigParameters):
        self.block_matching = BlockMatching(config_parameters)
        self.video = video
        self.config_parameters = config_parameters

    def demo(self, anchor_index: int, target_index: int):
        if self.config_parameters.frames_print_debug:
            anchor_frame = self.video.frames_inp[anchor_index].copy()
            target_frame = self.video.frames_inp[target_index].copy()

            return self.block_matching.step(anchor_frame, target_frame)
        
        return None, None, None, None

    def video_processing(self):
        print("Motion Estimation (Block Matching - Three Step Search) processing...")
        
        global_motion_vectors = []
        frame_anchor_p_vec = []
        frame_motion_field_vec = []
        frame_global_motion_vec = []
        
        for f in tqdm(range(len(self.video.frames_inp) - 1)):
            anchor =  self.video.frames_inp[f]
            target = self.video.frames_inp[f + 1]

            if self.config_parameters.frames_print_debug:
                global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector = self.block_matching.step(anchor, target)
                
                global_motion_vectors.append(global_motion_vec)
                frame_anchor_p_vec.append(frame_anchor_p)
                frame_motion_field_vec.append(frame_motion_field)
                frame_global_motion_vec.append(frame_global_motion_vector)
                
            else:
                global_motion_vec, _, _, _ = self.block_matching.step(anchor, target)
                global_motion_vectors.append(global_motion_vec)

        return global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec
