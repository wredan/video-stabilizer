import os
from config.config_video import ConfigVideoParameters
from src.motion_estimation.motion_estimation import MotionEstimation
from src.frame_position_smoothing.frame_position_smoothing import FramePositionSmoothing
from src.frames_print_debug import FramesPrintDebug
from src.video import Video
import src.utils as utils
from src.post_processing.post_processing import PostProcessing

class VideoProcessing:
    def __init__(self, video_name, client_dir, config_parameters: ConfigVideoParameters):
        self.video_name = video_name
        self.client_dir = client_dir
        self.config_parameters = config_parameters
        video_path = os.path.join(config_parameters.path_in, client_dir, video_name)
        self.video = Video(video_path)
        self.video.read_frames()
        self.motion_estimation = MotionEstimation(self.config_parameters)
        self.smoothing = FramePositionSmoothing(self.config_parameters, client_dir=client_dir)
    
    def __process_video_demo(self):
        global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = self.motion_estimation.video_processing(self.video.gray_frame_inp)
        global_correct_motion_vectors = self.smoothing.global_correction_motion_vectors(global_motion_vectors)
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
            path= os.path.join(self.config_parameters.base_path + self.client_dir + self.config_parameters.path_out), 
            fps= self.video.fps, 
            second_override= True, 
            second_quadrant= frames,
            gray= self.config_parameters.gray)
        
        if self.config_parameters.crop_frames and self.config_parameters._compare_filtered_result:
            self._compare_filtered_result(post_processing, frames)
        

    def _compare_filtered_result(self, post_processing: PostProcessing, filtered_cropped_frames):
        origin_cropped_frames = post_processing.crop_frames(self.video.gray_frame_inp, max_shift= post_processing.max_shift)
        origin_crop_gmv, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = self.motion_estimation.video_processing(origin_cropped_frames)
        origin_acc_motion = self.smoothing.get_accumulated_motion_vec(origin_crop_gmv)

        fil_crop_gmv, fil_frame_anchor_p_vec, fil_frame_motion_field_vec, fil_frame_global_motion_vec = self.motion_estimation.video_processing(filtered_cropped_frames)
        filtered_acc_motion = self.smoothing.get_accumulated_motion_vec(fil_crop_gmv)

        utils.plot_compare_motion(origin_acc_motion, filtered_acc_motion, os.path.join(self.config_parameters.base_path + self.client_dir + "compare_motion.png"), self.config_parameters.plot_scale_factor)

        FramesPrintDebug().write_video(
            global_motion_vectors= origin_crop_gmv, 
            video_frames= origin_cropped_frames, 
            third_quadrant= frame_global_motion_vec, 
            fourth_quadrant= fil_frame_global_motion_vec, 
            third_quadrant_title= "Origin motion field", 
            fourth_quadrant_title= "Filtered motion field", 
            window_title= "Demo", 
            path= os.path.join(self.config_parameters.base_path + self.client_dir +"compare.mp4"), 
            fps= self.video.fps, 
            second_override= True, 
            second_quadrant= filtered_cropped_frames,
            gray= self.config_parameters.gray)
        
    def _process_video(self):
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
        if self.config_parameters.debug_mode:
            path =  os.path.join(self.config_parameters.base_path, self.client_dir, self.config_parameters.path_out)
            file_name = self.config_parameters.path_out
        else:
            path = os.path.join(self.config_parameters.base_path, self.client_dir, self.video_name)
            file_name = self.video_name
        
        self.video.write(frames_out= frames, path= path, gray= self.config_parameters.gray)
        return file_name
    
    def run(self):
        if self.config_parameters.demo and self.config_parameters.debug_mode:
            self.__process_video_demo()
        else:
            return self._process_video()
