import cv2
from fastapi import WebSocket, WebSocketDisconnect
import numpy as np
from tqdm import tqdm
from src.request_handler.json_encoder import JsonEncoder
class FramesPrintDebug:
    def __init__(self):
        pass

    async def write_video(self, 
                    global_motion_vectors, 
                    video_frames, 
                    third_quadrant, 
                    fourth_quadrant, 
                    third_quadrant_title, 
                    fourth_quadrant_title, 
                    window_title, 
                    path, 
                    fps, 
                    second_override, 
                    second_quadrant, 
                    websocket: WebSocket=None):
        
        message = f"Writing video with {third_quadrant_title} and {fourth_quadrant_title}..."
        print(message)
        await websocket.send_json(JsonEncoder.init_video_writing_json(message))

        frames_out = []
        total = len(video_frames)
        for f in tqdm(range(total - 2)):
            anchor = video_frames[f]
            target = second_quadrant[f] if second_override else video_frames
            out = self.visualize_single_color_frame(
                    anchor,
                    target,
                    third_quadrant[f],
                    third_quadrant_title,
                    fourth_quadrant[f],
                    f"{fourth_quadrant_title} - {global_motion_vectors[f]}",
                    window_title,
                    f
                )
            frames_out.append(out)
            await websocket.send_json(JsonEncoder.update_step_json("visualize", f, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        self.write(frames_out, path, fps)

    def write(self, frames_out, path, fps):
        h, w = frames_out[0].shape[:2]
        #fourcc = cv2.VideoWriter_fourcc(*'H264')
        #fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fourcc = -1
        writer = cv2.VideoWriter(path, fourcc, fps, (w, h), True)

        for frame in frames_out:
            writer.write(frame)

        print("[INFO] Video Export Completed")

    def visualize_single_color_frame(self, anchor, target, third_quadrant, third_quadrant_title, fourth_quadrant, fourth_quadrant_title, title, a):
        h, w = 70, 10
        H, W = anchor.shape[:2]
        HH, WW = h + 2 * H + 20, 2 * (W + w)
        frame = np.full((HH, WW, 3), 255, dtype=np.uint8)  # Set this to have 3 color channels 

        cv2.putText(frame, title, (w, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"anchor-{a:03}", (w, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"target-{a+1:03}", (w + W, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, third_quadrant_title, (w, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, fourth_quadrant_title, (w + W, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)

        # reg of interest
        frame[h:h+H, :W, :] = anchor
        frame[h:h+H, W+w:2*W+w, :] = target if anchor.shape == target.shape else self.add_border(target, anchor.shape)
        frame[h+H+20:2*H+h+20, :W, :] = third_quadrant
        frame[h+H+20:2*H+h+20, W+w:2*W+w, :] = fourth_quadrant

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


