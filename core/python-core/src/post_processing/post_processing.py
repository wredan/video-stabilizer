import logging
import cv2
from fastapi import WebSocket, WebSocketDisconnect
import numpy as np
from tqdm import tqdm
from src.request_handler.json_encoder import JsonEncoder
from src.video import Video
class PostProcessing:

    def __init__(self) -> None:
        pass

    async def shift_frames(self, video: Video, global_correct_motion_vectors, websocket: WebSocket, update_shift_id="shifting", compare_message=""):
        """
        Shifts each frame according to the corresponding global motion correction vector.
        Uses the OpenCV function cv2.warpAffine for the actual shifting.
        """
        message = "Shifting frames " + compare_message + "..."
        logger = logging.getLogger('logger')
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_frames_shift_json(message, state=update_shift_id))
        shifted_frames = []
        
        await video.set_video_source()
        total = video.total_frame
        for i, correction_vector in tqdm(enumerate(global_correct_motion_vectors)):
            ret, frame = video.video_source.read()
            if not ret:
                logger.error("Error in Frame Read")
                break
            M = np.float32([[1, 0, correction_vector[0]], [0, 1, correction_vector[1]]])
            shifted_frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
            shifted_frames.append(shifted_frame)
            del frame
            await websocket.send_json(JsonEncoder.update_step_json(update_shift_id, i, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise
        await video.close_video_source()
        return shifted_frames


    async def crop_frames(self, frames, max_shift = None, global_correct_motion_vectors = None, websocket: WebSocket = None, update_crop_id="cropping", compare_message=""):
        """
        Crops each frame to remove the black borders created due to shifting.
        """
        cropped_frames = []

        if max_shift is None:
            max_shift = max(max(abs(correction_vector[0]), abs(correction_vector[1])) 
                            for correction_vector in global_correct_motion_vectors)            
            self.max_shift = max_shift

        message = "Cropping frames " + compare_message + "..."
        logger = logging.getLogger('logger')
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_frames_cropping_json(message, state=update_crop_id))

        total = len(frames)
        for i, frame in tqdm(enumerate(frames)):
            start_x = int(max_shift)
            start_y = int(max_shift)
            end_x = frame.shape[1] - int(max_shift)
            end_y = frame.shape[0] - int(max_shift)
            cropped_frame = frame[start_y:end_y, start_x:end_x]

            cropped_frames.append(cropped_frame)

            await websocket.send_json(JsonEncoder.update_step_json(update_crop_id, i, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        return cropped_frames
    

    async def crop_video(self, video: Video, max_shift = None, global_correct_motion_vectors = None, websocket: WebSocket = None, update_crop_id="cropping", compare_message=""):
        """
        Crops each frame to remove the black borders created due to shifting.
        """
        cropped_frames = []

        if max_shift is None:
            max_shift = max(max(abs(correction_vector[0]), abs(correction_vector[1])) 
                            for correction_vector in global_correct_motion_vectors)            
            self.max_shift = max_shift

        message = "Cropping frames " + compare_message + "..."
        logger = logging.getLogger('logger')
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_frames_cropping_json(message, state=update_crop_id))

        await video.set_video_source()
        for i in tqdm(range(video.total_frame)):
            ret, frame = video.video_source.read()
            if not ret:
                logger.error("Error in Frame Read")
                break
            start_x = int(max_shift)
            start_y = int(max_shift)
            end_x = frame.shape[1] - int(max_shift)
            end_y = frame.shape[0] - int(max_shift)
            cropped_frame = frame[start_y:end_y, start_x:end_x]

            cropped_frames.append(cropped_frame)

            await websocket.send_json(JsonEncoder.update_step_json(update_crop_id, i, video.total_frame))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise
        await video.close_video_source()
        return cropped_frames
