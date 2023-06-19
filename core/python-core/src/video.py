import asyncio
import logging
import traceback
import cv2
from fastapi import WebSocket, WebSocketDisconnect
from tqdm import tqdm
from src.request_handler.json_encoder import JsonEncoder

class Video:
    def __init__(self, path):
        self.path = path
        self.frame_inp = []
        self.shape = (0, 0) # H,W
        self.fps = None
        self.video_source = None
        self.total_frame = 0

    async def set_video_source(self):
        logger = logging.getLogger('logger')
        try: 
            self.video_source = cv2.VideoCapture(self.path)
            self.total_frame = int(self.video_source.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.video_source.get(cv2.CAP_PROP_FPS)  # Get the FPS of the video
        except Exception as e:            
            logger.error("Error: " + str(e))
            logger.error(traceback.format_exc())
            return
        
    async def get_video_shape(self,):
        logger = logging.getLogger('logger')
        await self.set_video_source()
        ret, frame = self.video_source.read()
        if not (ret or frame):
            logger.info("Error in Frame Read")
            return self.shape  
        self.shape = (frame.shape[0], frame.shape[1])
        await self.close_video_source()   
        return self.shape
        
    async def close_video_source(self):
        if self.video_source is not None:
            self.video_source.release()
            self.video_source = None

    async def write(self, frames_out, path, websocket: WebSocket= None):
        h, w = frames_out[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
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
        writer.release()

        logger.info("Video Export Completed")

    async def add_audio(self, video_path_without_audio, video_path_with_audio, output_path, websocket: WebSocket= None):
        logger = logging.getLogger('logger')

        # Check if the original video has an audio track
        cmd = f"ffprobe -v error -select_streams a -show_entries stream=codec_type -of default=noprint_wrappers=1:nokey=1 {video_path_with_audio}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        # If no audio track, just copy the video with libx264 without audio
        if stdout.decode().strip() != "audio":
            cmd = f"ffmpeg -i {video_path_without_audio} -c:v libx264 {output_path}"
        else:
            message = "Writing audio..."
            logger.info(message)
            await websocket.send_json(JsonEncoder.init_audio_writing_json(message))
            cmd = f"ffmpeg -i {video_path_without_audio} -i {video_path_with_audio} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 {output_path}"

        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFmpeg failed with exit code {process.returncode}, stderr: {stderr.decode()}")

        logger.info(f"FFmpeg finished with stdout: {stdout.decode()}")


