import cv2
from fastapi import WebSocket, WebSocketDisconnect
from tqdm import tqdm
from .block_matching import BlockMatching
from config.config_video import ConfigVideoParameters
from src.request_handler.json_encoder import JsonEncoder
class MotionEstimation:
    def __init__(self, config_parameters: ConfigVideoParameters):
        self.config_parameters = config_parameters
        
    async def video_processing(self, frames, websocket: WebSocket, update_step_code = 'me', compare_message = ""):
        message = "Motion Estimation (Block Matching - Three Step Search) processing " + compare_message + "..."
        print(message)
        await websocket.send_json(JsonEncoder.init_motion_estimation_json(message, state=update_step_code))

        global_motion_vectors = []
        frame_anchor_p_vec = []
        frame_motion_field_vec = []
        frame_global_motion_vec = []
        block_matching = BlockMatching(self.config_parameters)
        
        _range = range(len(frames) - 1)
        total = _range[-1]
        for f in tqdm(_range):
            anchor =  cv2.cvtColor(frames[f], cv2.COLOR_BGR2GRAY)
            target = cv2.cvtColor(frames[f + 1], cv2.COLOR_BGR2GRAY)

            if self.config_parameters.demo:
                global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector = block_matching.step(anchor, target)
                
                global_motion_vectors.append(global_motion_vec)
                frame_anchor_p_vec.append(frame_anchor_p)
                frame_motion_field_vec.append(frame_motion_field)
                frame_global_motion_vec.append(frame_global_motion_vector)
                
            else:
                global_motion_vec, _, _, _ = block_matching.step(anchor, target)
                global_motion_vectors.append(global_motion_vec)
        
            await websocket.send_json(JsonEncoder.update_step_json(update_step_code, f, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        return global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec
