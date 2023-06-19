import logging
import cv2
from fastapi import WebSocket, WebSocketDisconnect
from tqdm import tqdm
from .block_matching import BlockMatching
from .optical_flow import OpticalFlow
from config.config_video import ConfigVideoParameters
from src.request_handler.json_encoder import JsonEncoder
from  src.utils import MotionEstimationMethod
from src.video import Video
class MotionEstimation:
    def __init__(self, config_parameters: ConfigVideoParameters):
        self.config_parameters = config_parameters

    async def _process_frame(self, motion_estimation, anchor, target, plot):
        if self.config_parameters.demo:
            global_motion_vec, frame_motion_field, frame_global_motion_vector = motion_estimation.step(anchor, target, plot)
            return global_motion_vec, frame_motion_field, frame_global_motion_vector
        else:
            global_motion_vec, _, _ = motion_estimation.step(anchor, target)
            return global_motion_vec, None, None

    def _update_vectors(self, global_motion_vectors, frame_motion_field_vec, frame_global_motion_vec, result):
        global_motion_vec, frame_motion_field, frame_global_motion_vector = result
        global_motion_vectors.append(global_motion_vec)
        if frame_motion_field_vec is not None:
            frame_motion_field_vec.append(frame_motion_field)
            frame_global_motion_vec.append(frame_global_motion_vector)

    async def _process_frames(self, motion_estimation, frames, websocket, update_step_code, plot):
        global_motion_vectors = []
        frame_motion_field_vec = []
        frame_global_motion_vec = []

        _range = range(len(frames) - 1)
        total = _range[-1]
        for f in tqdm(_range):
            anchor =  cv2.cvtColor(frames[f], cv2.COLOR_BGR2GRAY)
            target = cv2.cvtColor(frames[f + 1], cv2.COLOR_BGR2GRAY)
            result = await self._process_frame(motion_estimation, anchor, target, plot)
            self._update_vectors(global_motion_vectors, frame_motion_field_vec, frame_global_motion_vec, result)
            await self.update_progress(f, total, websocket, update_step_code)

        return global_motion_vectors, frame_motion_field_vec, frame_global_motion_vec

    async def _process_video(self, motion_estimation, video: Video, websocket: WebSocket, update_step_code, plot):
        logger = logging.getLogger('logger')
        global_motion_vectors = []
        frame_motion_field_vec = []
        frame_global_motion_vec = []

        await video.set_video_source()

        total = video.total_frame - 1
        ret, anchor = video.video_source.read()  # Read the first frame
        if not ret:
            logger.error("Error in Frame Read")
            return

        anchor = cv2.cvtColor(anchor, cv2.COLOR_BGR2GRAY)

        for f in tqdm(range(total)):
            ret, target = video.video_source.read()
            if not ret:
                logger.error("Error in Frame Read")
                break
            target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

            result = await self._process_frame(motion_estimation, anchor, target, plot)
            self._update_vectors(global_motion_vectors, frame_motion_field_vec, frame_global_motion_vec, result)

            anchor = target  # Use the target frame as the anchor frame for the next iteration

            await self.update_progress(f, total, websocket, update_step_code)

        await video.close_video_source()
        
        return global_motion_vectors, frame_motion_field_vec, frame_global_motion_vec


    async def update_progress(self, current, total, websocket: WebSocket, update_step_code):
        await websocket.send_json(JsonEncoder.update_step_json(update_step_code, current, total))
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:              
            raise

    async def update_progress(self, current, total, websocket: WebSocket, update_step_code):
        await websocket.send_json(JsonEncoder.update_step_json(update_step_code, current, total))
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:              
            raise

    async def video_processing(self, video: Video, websocket: WebSocket, update_step_code = 'me', compare_message = "", frames= None, plot = False):
        logger = logging.getLogger('logger')
        motion_estimation = None

        if self.config_parameters.stabilization_parameters.motion_estimation.motion_estimation_method == MotionEstimationMethod.BLOCK_MATCHING:
            motion_estimation = BlockMatching(self.config_parameters)
            message = "Motion Estimation (Block Matching - Three Step Search) processing " + compare_message + "..."

        elif self.config_parameters.stabilization_parameters.motion_estimation.motion_estimation_method == MotionEstimationMethod.OPTICAL_FLOW:
            message = "Motion Estimation (Sparse Optical Flow) processing " + compare_message + "..."
            motion_estimation = OpticalFlow(self.config_parameters)

        logger.info(message)
        await websocket.send_json(JsonEncoder.init_motion_estimation_json(message, state=update_step_code))

        if frames is not None:
            return await self._process_frames(motion_estimation, frames, websocket, update_step_code, plot)
        return await self._process_video(motion_estimation, video, websocket, update_step_code, plot)
