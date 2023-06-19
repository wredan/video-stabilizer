import os

from fastapi import WebSocket, WebSocketDisconnect
from config.config_video import ConfigVideoParameters
from src.motion_estimation.motion_estimation import MotionEstimation
from src.frame_position_smoothing.frame_position_smoothing import FramePositionSmoothing
from src.frames_print_debug import FramesPrintDebug
from src.video import Video
import src.utils as utils
from src.post_processing.post_processing import PostProcessing

class VideoProcessing:
    def __init__(self, video_name, client_dir, config_parameters: ConfigVideoParameters, websocket: WebSocket):
        self.video_name = video_name
        self.client_dir = client_dir
        self.config_parameters = config_parameters
        self.websocket = websocket
        self.video_path = os.path.join(config_parameters.path_in, client_dir, video_name)
        self.video = Video(self.video_path)
        self.motion_estimation = MotionEstimation(self.config_parameters)
        self.smoothing = FramePositionSmoothing(self.config_parameters, client_dir=client_dir)
        self.post_processing = PostProcessing()
    
    async def motion_estimation_and_correction(self):
        global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = await self.motion_estimation.video_processing(self.video.frame_inp, websocket=self.websocket)
        global_correct_motion_vectors = await self.smoothing.global_correction_motion_vectors(global_motion_vectors, websocket=self.websocket)
        return global_correct_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec

    async def post_process_frames(self, global_correct_motion_vectors):
        frames = await self.post_processing.shift_frames(self.video.frame_inp, global_correct_motion_vectors, websocket=self.websocket)
        if self.config_parameters.stabilization_parameters.crop_frames:
            frames = await self.post_processing.crop_frames(frames, global_correct_motion_vectors=global_correct_motion_vectors, websocket=self.websocket)
        return frames
    
    async def compare_and_plot(self, frames, global_correct_motion_vectors):

        filtered_cropped_frames = frames
        if not self.config_parameters.stabilization_parameters.crop_frames:
            filtered_cropped_frames = await self.post_processing.crop_frames(frames, global_correct_motion_vectors=global_correct_motion_vectors, websocket= self.websocket, update_crop_id="crop_comp_smot", compare_message="smoothed")
        fil_crop_gmv, _, _, _ = await self.motion_estimation.video_processing(filtered_cropped_frames, websocket=self.websocket, update_step_code="me2", compare_message="smoothed")
        filtered_acc_motion = self.smoothing.get_accumulated_motion_vec(fil_crop_gmv)

        origin_cropped_frames = await self.post_processing.crop_frames(self.video.frame_inp, max_shift=self.post_processing.max_shift, websocket=self.websocket, update_crop_id="crop_comp_origin", compare_message="origin")
        origin_crop_gmv, _, _, _ = await self.motion_estimation.video_processing(origin_cropped_frames, websocket=self.websocket, update_step_code="me1", compare_message="origin")
        origin_acc_motion = self.smoothing.get_accumulated_motion_vec(origin_crop_gmv)
        
        utils.plot_compare_motion(origin_acc_motion,
                                  filtered_acc_motion,
                                  os.path.join(self.config_parameters.base_path,
                                               self.client_dir,
                                               "compare_motion.png"),
                                  self.config_parameters.plot_scale_factor)
                
    async def _process_video_demo(self):
        global_correct_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec = await self.motion_estimation_and_correction()
        global_corrected_vect_frames = utils.plot_global_corrected_motion_vector(global_correct_motion_vectors, self.video.shape[1], self.video.shape[0])
        frames = await self.post_process_frames(global_correct_motion_vectors)

        await FramesPrintDebug(self.config_parameters).write_video(
            global_motion_vectors= global_correct_motion_vectors, 
            video_frames= self.video.frame_inp,
            third_quadrant= frame_motion_field_vec, 
            fourth_quadrant= global_corrected_vect_frames, 
            third_quadrant_title= "motion field", 
            fourth_quadrant_title= "global correction motion vector", 
            window_title= "Demo", 
            path_temp = os.path.join(self.config_parameters.base_path, self.client_dir, "temp.mp4"),
            path= os.path.join(self.config_parameters.base_path, self.client_dir, self.config_parameters.path_out), 
            fps= self.video.fps, 
            second_override= True, 
            second_quadrant= frames,
            websocket= self.websocket)
        
        if self.config_parameters.stabilization_parameters.compare_filtered_result:
            await self.compare_and_plot(frames, global_correct_motion_vectors)
        
        return self.config_parameters.path_out
        
    async def _process_video(self):
        # Step 1 and 2: Motion Estimation and filtering
        global_correct_motion_vectors, _, _, _ = await self.motion_estimation_and_correction()
        
        # Step 3: Post-Processing
        frames = await self.post_process_frames(global_correct_motion_vectors)
        
        if self.config_parameters.stabilization_parameters.compare_filtered_result:
            await self.compare_and_plot(frames, global_correct_motion_vectors)
        
        del global_correct_motion_vectors
        del self.video.frame_inp

        # Saving file
        temp_path = os.path.join(self.config_parameters.base_path, self.client_dir, "temp.mp4")
        
        await self.video.write(frames_out= frames, path= temp_path, websocket= self.websocket)

        file_name = self.video_name.split('.')[0] + ".mp4"
        path = os.path.join(self.config_parameters.base_path, self.client_dir, file_name)

        await self.video.add_audio(
            video_path_without_audio= temp_path,
            video_path_with_audio= self.video_path,
            output_path=path,
            websocket= self.websocket
        )

          
        return file_name
    
    async def run(self):
        await self.video.read_frames(self.websocket)
        try:
            if self.config_parameters.demo:
                return await self._process_video_demo()
            else:
                return await self._process_video()
        except WebSocketDisconnect:
           raise
