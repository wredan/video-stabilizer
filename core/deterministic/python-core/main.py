import numpy as np
from config.config import ConfigParameters
from src.motion_estimation.motion_estimation import MotionEstimation
from src.frame_position_smoothing.frame_position_smoothing import FramePositionSmoothing
from src.frames_print_debug import FramesPrintDebug
from src.video import Video
import src.utils as utils
from src.post_processing.post_processing import PostProcessing
class VideoProcessing:
    def __init__(self):
        self.config_parameters = ConfigParameters()
        self.video = Video(self.config_parameters.path_in)
        self.video.read_frames()
        self.motion_estimation = MotionEstimation(self.config_parameters)
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
    
    def process_video_demo(self):
        global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = self.motion_estimation.video_processing(self.video.gray_frame_inp)
        # utils.plot_time_position(global_motion_vectors, self.config_parameters.base_path + "/global_motion_vectors.png", self.config_parameters.plot_scale_factor)
        global_correct_motion_vectors = self.smoothing.global_correction_motion_vectors(global_motion_vectors)
        # utils.plot_time_position(global_correct_motion_vectors, self.config_parameters.base_path + "/global_correct_motion_vectors.png", self.config_parameters.plot_scale_factor)
        global_corrected_vect_frames = utils.plot_global_corrected_motion_vector(global_correct_motion_vectors, self.video.shape[1], self.video.shape[0])
        frames = self.video.gray_frame_inp if self.config_parameters.gray else self.video.frame_inp

        post_processing = PostProcessing()
        frames = post_processing.shift_frames(frames, global_correct_motion_vectors)
        if self.config_parameters.crop_frames:
            frames = post_processing.crop_frames(frames, global_correct_motion_vectors=global_correct_motion_vectors)

        FramesPrintDebug().write_video(
            global_motion_vectors= global_correct_motion_vectors, 
            video_frames= self.video.gray_frame_inp if self.config_parameters.gray else self.video.frame_inp, 
            third_quadrant= frame_global_motion_vec, 
            fourth_quadrant= global_corrected_vect_frames, 
            third_quadrant_title= "motion field", 
            fourth_quadrant_title= "global correction motion vector", 
            window_title= "Demo", 
            path= self.config_parameters.base_path + self.config_parameters.path_out, 
            fps= 30.0, 
            second_override= True, 
            second_quadrant= frames,
            gray= self.config_parameters.gray)
        
        if self.config_parameters.crop_frames:
            self.compare_filtered_result(post_processing, frames)
        

    def compare_filtered_result(self, post_processing: PostProcessing, filtered_cropped_frames):
        origin_cropped_frames = post_processing.crop_frames(self.video.gray_frame_inp, max_shift= post_processing.max_shift)
        origin_crop_gmv, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = self.motion_estimation.video_processing(origin_cropped_frames)
        origin_acc_motion = self.smoothing.get_accumulated_motion_vec(origin_crop_gmv)

        fil_crop_gmv, fil_frame_anchor_p_vec, fil_frame_motion_field_vec, fil_frame_global_motion_vec = self.motion_estimation.video_processing(filtered_cropped_frames)
        filtered_acc_motion = self.smoothing.get_accumulated_motion_vec(fil_crop_gmv)

        utils.plot_compare_motion(origin_acc_motion, filtered_acc_motion, self.config_parameters.base_path + "/compare_motion.png", self.config_parameters.plot_scale_factor)

        FramesPrintDebug().write_video(
            global_motion_vectors= origin_crop_gmv, 
            video_frames= origin_cropped_frames, 
            third_quadrant= frame_global_motion_vec, 
            fourth_quadrant= fil_frame_global_motion_vec, 
            third_quadrant_title= "Origin motion field", 
            fourth_quadrant_title= "Filtered motion field", 
            window_title= "Demo", 
            path= self.config_parameters.base_path + "/compare.mp4", 
            fps= 30.0, 
            second_override= True, 
            second_quadrant= filtered_cropped_frames,
            gray= self.config_parameters.gray)
        
    def process_video(self):
        # Step 1: Motion Estimation
        global_motion_vectors, _, _, _ = self.motion_estimation.video_processing(self.video.gray_frame_inp)

        # Step 2: Motion filtering
        global_correct_motion_vectors = self.smoothing.global_correction_motion_vectors(global_motion_vectors)

        # Step 3: Post-Processing
        post_processing = PostProcessing()
        frames = self.video.gray_frame_inp if self.config_parameters.gray else self.video.frame_inp
        frames = post_processing.shift_frames(frames, global_correct_motion_vectors)
        if self.config_parameters.crop_frames:
            frames = post_processing.crop_frames(frames, global_correct_motion_vectors=global_correct_motion_vectors)

        # Saving file
        self.video.write(frames_out= frames, path= "data/output/test.mp4", fps= 30, gray= self.config_parameters.gray)
    
    def run(self):
        if self.config_parameters.demo and self.config_parameters.frames_print_debug:
            self.run_demo()
        elif self.config_parameters.frames_print_debug:
            self.process_video_demo()
        else:
            self.process_video()


if __name__ == "__main__":
    video_processing = VideoProcessing()
    video_processing.run()
