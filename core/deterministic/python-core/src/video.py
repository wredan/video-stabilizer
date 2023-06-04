import cv2
from fastapi import WebSocket, WebSocketDisconnect
from tqdm import tqdm
from src.request_handler.json_encoder import init_video_writing_json, update_step_json

class Video:
    def __init__(self, path):
        self.path = path
        self.frame_inp = []
        self.gray_frame_inp = []
        self.shape = (0, 0) # H,W
        self.fps = None

    def read_frames(self):
        try: 
            source = cv2.VideoCapture(self.path)
            total_frame = int(source.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = source.get(cv2.CAP_PROP_FPS)  # Get the FPS of the video
        except:
            print("Error in Path or Frame Count")
            exit()
        
        print("[INFO] Reading frames...", total_frame)
        gray_frames_inp = []
        for _ in tqdm(range(total_frame)):
            ret, frame = source.read()
            if not (ret or frame):
                print("Error in Frame Read")
                break
            self.frame_inp.append(frame)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.shape == (0, 0):
                self.shape = (gray_frame.shape[0], gray_frame.shape[1])

            gray_frames_inp.append(gray_frame)
        
        self.gray_frame_inp = gray_frames_inp

        print("[INFO] Video Import Completed")

    async def write(self, frames_out, path, gray = False, websocket: WebSocket= None):
        h, w = frames_out[0].shape[:2]
        # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fourcc = -1
        writer = cv2.VideoWriter(path, fourcc, self.fps, (w, h), True)

        message = "Writing frames..."
        print(message)
        await websocket.send_json(init_video_writing_json(message))
        total = len(frames_out)
        for i, frame in enumerate(frames_out):          
            writer.write(frame)
            await websocket.send_json(update_step_json(i, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        print("[INFO] Video Export Completed")
