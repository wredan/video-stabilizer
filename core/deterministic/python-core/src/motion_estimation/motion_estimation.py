from tqdm import tqdm
from .block_matching import BlockMatching
from config.config_video import ConfigVideoParameters

class MotionEstimation:
    def __init__(self, config_parameters: ConfigVideoParameters):
        self.config_parameters = config_parameters

    def demo(self, frames, anchor_index: int, target_index: int):
        if self.config_parameters.frames_print_debug:
            anchor_frame = frames[anchor_index].copy()
            target_frame = frames[target_index].copy()

            return self.block_matching.step(anchor_frame, target_frame)
        
        return None, None, None, None

    def video_processing(self, frames):
        print("Motion Estimation (Block Matching - Three Step Search) processing...")
        
        global_motion_vectors = []
        frame_anchor_p_vec = []
        frame_motion_field_vec = []
        frame_global_motion_vec = []
        block_matching = BlockMatching(self.config_parameters)
        
        for f in tqdm(range(len(frames) - 1)):
            anchor =  frames[f]
            target = frames[f + 1]

            if self.config_parameters.debug_mode:
                global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector = block_matching.step(anchor, target)
                
                global_motion_vectors.append(global_motion_vec)
                frame_anchor_p_vec.append(frame_anchor_p)
                frame_motion_field_vec.append(frame_motion_field)
                frame_global_motion_vec.append(frame_global_motion_vector)
                
            else:
                global_motion_vec, _, _, _ = block_matching.step(anchor, target)
                global_motion_vectors.append(global_motion_vec)

        return global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec
