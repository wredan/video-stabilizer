import asyncio
import cv2
from fastapi import WebSocket, WebSocketDisconnect
import numpy as np
from tqdm import tqdm
from src.request_handler.json_encoder import JsonEncoder
import logging
from config.config_video import ConfigVideoParameters
from src.video import Video
class FramesPrintDebug:
    def __init__(self, config_parameters: ConfigVideoParameters):
        self.config_parameters = config_parameters

    async def write_video(self, 
                    global_motion_vectors, 
                    video: Video, 
                    third_quadrant, 
                    fourth_quadrant, 
                    third_quadrant_title, 
                    fourth_quadrant_title, 
                    window_title, 
                    path_temp,
                    path, 
                    fps, 
                    second_quadrant, 
                    websocket: WebSocket=None):
        
        logger = logging.getLogger('logger')
        message = f"Writing video with {third_quadrant_title} and {fourth_quadrant_title}..."
        logger.info(message)
        await websocket.send_json(JsonEncoder.init_video_writing_json(message))

        await video.set_video_source()
       
        for f in tqdm(range(video.total_frame - 2)):
            ret, anchor = video.video_source.read()  # Read the first frame
            if not ret:
                logger.error("Error in Frame Read")
                return
            
            out = self.visualize_single_color_frame(
                    anchor,
                    second_quadrant[f],
                    third_quadrant[f],
                    third_quadrant_title,
                    fourth_quadrant[f],
                    f"{fourth_quadrant_title}",
                    window_title,
                    f
                )
            
            if f == 0:
                h, w = out.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(path_temp, fourcc, fps, (w, h), True) if self.config_parameters.docker else cv2.VideoWriter(path, -1, fps, (w, h), True)
            
            writer.write(out)
            del out
            await websocket.send_json(JsonEncoder.update_step_json("visualize", f, video.total_frame))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise
        writer.release()
        await video.close_video_source()

        logger = logging.getLogger('logger')
        if self.config_parameters.docker:
            await self.parseTolibx264(path_temp, path)
        logger.info("Video Export Completed")       

    async def parseTolibx264(self, video_path, output_path):
        logger = logging.getLogger('logger')

        cmd = f"ffmpeg -i {video_path} -c:v libx264 {output_path}"
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"FFmpeg failed with exit code {process.returncode}, stderr: {stderr.decode()}")

        logger.info(f"FFmpeg finished with stdout: {stdout.decode()}")

    def visualize_single_color_frame(self, anchor, target, third_quadrant, third_quadrant_title, fourth_quadrant, fourth_quadrant_title, title, a):
        h, w = 70, 10
        H, W = anchor.shape[:2]
        HH, WW = h + 2 * H + 20, 2 * (W + w)
        frame = np.full((HH, WW, 3), 255, dtype=np.uint8)  # Set this to have 3 color channels 

        cv2.putText(frame, title, (w, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"anchor-{a:03}", (w, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"target-{a:03}", (w + W, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, third_quadrant_title, (w, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, fourth_quadrant_title, (w + W, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)

        # reg of interest
        frame[h:h+H, :W, :] = anchor
        frame[h:h+H, W+w:2*W+w, :] = target if anchor.shape == target.shape else self.add_border(target, anchor.shape)

        third_quadrant_bgr = cv2.cvtColor(third_quadrant, cv2.COLOR_GRAY2BGR)
        frame[h+H+20:2*H+h+20, :W, :] = third_quadrant_bgr

        fourth_quadrant_bgr = cv2.cvtColor(fourth_quadrant, cv2.COLOR_GRAY2BGR)
        frame[h+H+20:2*H+h+20, W+w:2*W+w, :] = fourth_quadrant_bgr

        return frame

    def add_border(self, frame, original_shape):
        """
        Adds a black border to the frame to match the original shape, keeping the frame in the center.
        """
        # calculate the borders to be added
        top = (original_shape[0] - frame.shape[0]) // 2
        bottom = original_shape[0] - frame.shape[0] - top
        left = (original_shape[1] - frame.shape[1]) // 2
        right = original_shape[1] - frame.shape[1] - left

        # add the borders
        frame_with_border = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        return frame_with_border


