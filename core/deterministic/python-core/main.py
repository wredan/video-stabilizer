from config.config import ConfigParameters
from src.motion_estimation.motion_estimation import MotionEstimation
import src.frame_position_smoothing.frame_position_smoothing as FramePositionSmoothig
from src.frames_print_debug import FramesPrintDebug
from src.video import Video
from src.utils import single_step_plot

class VideoProcessing:
    def __init__(self):
        self.config_parameters = ConfigParameters()
        self.video = Video(self.config_parameters.path_in)
        self.video.read_frames(self.config_parameters.gray)
        self.motion_estimation = MotionEstimation(self.video, self.config_parameters)

    def run_demo(self):
        global_motion_vector, frame_anchor_p, frame_motion_field, frame_global_motion_vector = self.motion_estimation.demo(72, 73)
        global_correction_vector = FramesPrintDebug.demo_global_correction_motion_vectors(global_motion_vector, 30.0, 200.0)
        global_corrected_vect_frames = single_step_plot(global_correction_vector, self.video.shape[0], self.video.shape[1])
        FramesPrintDebug.show_demo_frame(self.video, 72, frame_global_motion_vector, global_corrected_vect_frames, "motion field", "global motion vector", "Demo")
    
    def process_video(self):
        global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = self.motion_estimation.video_processing()
        global_correct_motion_vectors = FramePositionSmoothig.global_correction_motion_vectors(global_motion_vectors, self.config_parameters.filter_intensity, self.config_parameters.base_path)
        global_corrected_vect_frames = FramePositionSmoothig.plot_global_corrected_motion_vector(global_correct_motion_vectors, self.video.shape[1], self.video.shape[0])
        shifted_frames = FramePositionSmoothig.shift_frames(self.video.frames_inp, global_correct_motion_vectors, self.config_parameters.intensity)
        FramesPrintDebug.write_video(global_correct_motion_vectors, self.video, frame_global_motion_vec, global_corrected_vect_frames, "motion field", "global correction motion vector", "Demo", self.config_parameters.base_path + self.config_parameters.path_out, 60.0, True, shifted_frames)
    
    def run(self):
        if self.config_parameters.demo and self.config_parameters.frames_print_debug:
            self.run_demo()
        else:
            self.process_video()


if __name__ == "__main__":
    video_processing = VideoProcessing()
    video_processing.run()
