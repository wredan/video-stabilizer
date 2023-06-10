import logging
import traceback
import cv2
from fastapi import WebSocket, WebSocketDisconnect
from tqdm import tqdm
from src.request_handler.json_encoder import JsonEncoder
from moviepy.editor import VideoFileClip

class Video:
    def __init__(self, path):
        self.path = path
        self.frame_inp = []
        self.shape = (0, 0) # H,W
        self.fps = None

    async def read_frames(self, websocket: WebSocket= None):
        logger = logging.getLogger('logger')
        try: 
            source = cv2.VideoCapture(self.path)
            total_frame = int(source.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = source.get(cv2.CAP_PROP_FPS)  # Get the FPS of the video
        except Exception as e:            
            logger.error("Error: " + str(e))
            logger.error(traceback.format_exc())
            return
        
        message = "Reading frames..."
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_reading_frames(message))
        for i in tqdm(range(total_frame)):
            ret, frame = source.read()
            if not (ret or frame):
                logger.info("Error in Frame Read")
                break
            self.frame_inp.append(frame)
            if self.shape == (0, 0):
                self.shape = (frame.shape[0], frame.shape[1])
            await websocket.send_json(JsonEncoder.update_step_json("reading", i, total_frame))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        logger.info("Video Import Completed")

    async def write(self, frames_out, path, websocket: WebSocket= None):
        h, w = frames_out[0].shape[:2]
        # fourcc = cv2.VideoWriter_fourcc(*'H264')
        fourcc = -1
        writer = cv2.VideoWriter(path, fourcc, self.fps, (w, h), True)

        logger = logging.getLogger('logger')
        message = "Writing frames..."
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_video_writing_json(message))
        total = len(frames_out)
        for i, frame in enumerate(frames_out):          
            writer.write(frame)
            await websocket.send_json(JsonEncoder.update_step_json("writing", i, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        logger.info("Video Export Completed")

    async def add_audio(self, video_path_without_audio, video_path_with_audio, output_path, websocket: WebSocket= None):
        logger = logging.getLogger('logger')
        message = "Writing audio..."
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_audio_writing_json(message))
        clip_without_audio = VideoFileClip(video_path_without_audio)
        clip_with_audio = VideoFileClip(video_path_with_audio)
        clip_with_audio = clip_with_audio.subclip(0, clip_without_audio.duration)
        final_clip = clip_without_audio.set_audio(clip_with_audio.audio)
        final_clip.write_videofile(output_path, codec='libx264')
