import logging
import cv2
from fastapi import WebSocket, WebSocketDisconnect
from tqdm import tqdm
from .block_matching import BlockMatching
from .optical_flow import OpticalFlow
from config.config_video import ConfigVideoParameters
from src.request_handler.json_encoder import JsonEncoder
from  src.utils import MotionEstimationMethod
class MotionEstimation:
    def __init__(self, config_parameters: ConfigVideoParameters):
        self.config_parameters = config_parameters
        
    async def _process_frames(self, motion_estimation, frames, websocket: WebSocket, update_step_code):
        global_motion_vectors = []
        frame_anchor_p_vec = []
        frame_motion_field_vec = []
        frame_global_motion_vec = []
        
        _range = range(len(frames) - 1)
        total = _range[-1]
        for f in tqdm(_range):
            anchor =  cv2.cvtColor(frames[f], cv2.COLOR_BGR2GRAY)
            target = cv2.cvtColor(frames[f + 1], cv2.COLOR_BGR2GRAY)

            if self.config_parameters.demo:
                global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector = motion_estimation.step(anchor, target)

                global_motion_vectors.append(global_motion_vec)
                frame_anchor_p_vec.append(frame_anchor_p)
                frame_motion_field_vec.append(frame_motion_field)
                frame_global_motion_vec.append(frame_global_motion_vector)

            else:
                global_motion_vec, _, _, _ = motion_estimation.step(anchor, target)
                global_motion_vectors.append(global_motion_vec)

            await self.update_progress(f, total, websocket, update_step_code)

        return global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec

    async def update_progress(self, current, total, websocket: WebSocket, update_step_code):
        await websocket.send_json(JsonEncoder.update_step_json(update_step_code, current, total))
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:              
            raise

    async def video_processing(self, frames, websocket: WebSocket, update_step_code = 'me', compare_message = ""):
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

        return await self._process_frames(motion_estimation, frames, websocket, update_step_code)
