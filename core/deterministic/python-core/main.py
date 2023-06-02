import numpy as np
from config.config import ConfigParameters
from src.motion_estimation.motion_estimation import MotionEstimation
from src.frame_position_smoothing.frame_position_smoothing import FramePositionSmoothing
from src.frames_print_debug import FramesPrintDebug
from src.video import Video
import src.utils as utils
import src.post_processing.post_processing as PostProcessing
class VideoProcessing:
    def __init__(self):
        self.config_parameters = ConfigParameters()
        self.video = Video(self.config_parameters.path_in)
        self.video.read_frames(self.config_parameters.gray)
        self.motion_estimation = MotionEstimation(self.video, self.config_parameters)
        self.smoothing = FramePositionSmoothing(self.config_parameters)

    def run_demo(self):
        global_motion_vector, frame_anchor_p, frame_motion_field, frame_global_motion_vector = self.motion_estimation.demo(72, 73)
        # global_correction_vector = FramesPrintDebug.demo_global_correction_motion_vectors(global_motion_vector, 30.0, 200.0)
        # global_corrected_vect_frames = utils.single_step_plot(global_correction_vector, self.video.shape[0], self.video.shape[1])
        FramesPrintDebug().show_demo_frame(
            video= self.video, 
            a= 72, 
            third_quadrant= frame_motion_field, 
            fourth_quadrant= frame_global_motion_vector, 
            third_quadrant_title= "motion field", 
            fourth_quadrant_title= "global motion vector", 
            window_title= "Demo")
    
    def process_video(self):
        global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = self.motion_estimation.video_processing()
        # utils.plot_time_position(global_motion_vectors, self.config_parameters.base_path + "/global_motion_vectors.png", self.config_parameters.plot_scale_factor)
        global_correct_motion_vectors = self.smoothing.global_correction_motion_vectors(global_motion_vectors)
        # utils.plot_time_position(global_correct_motion_vectors, self.config_parameters.base_path + "/global_correct_motion_vectors.png", self.config_parameters.plot_scale_factor)
        global_corrected_vect_frames = utils.plot_global_corrected_motion_vector(global_correct_motion_vectors, self.video.shape[1], self.video.shape[0])
        shifted_frames = PostProcessing.shift_frames(self.video.frames_inp, global_correct_motion_vectors)
        cropped_frames = PostProcessing.crop_frames(shifted_frames, global_correct_motion_vectors)
        FramesPrintDebug().write_video(
            global_motion_vectors= global_correct_motion_vectors, 
            video= self.video, 
            third_quadrant= frame_global_motion_vec, 
            fourth_quadrant= global_corrected_vect_frames, 
            third_quadrant_title= "motion field", 
            fourth_quadrant_title= "global correction motion vector", 
            window_title= "Demo", 
            path= self.config_parameters.base_path + self.config_parameters.path_out, 
            fps= 30.0, 
            second_override= True, 
            second_quadrant= cropped_frames)
    
    def run(self):
        if self.config_parameters.demo and self.config_parameters.frames_print_debug:
            self.run_demo()
        else:
            self.process_video()


if __name__ == "__main__":
    video_processing = VideoProcessing()
    video_processing.run()
