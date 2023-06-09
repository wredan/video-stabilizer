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

    async def read_frames(self, websocket: WebSocket= None):
        try: 
            source = cv2.VideoCapture(self.path)
            total_frame = int(source.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = source.get(cv2.CAP_PROP_FPS)  # Get the FPS of the video
        except:
            print("Error in Path or Frame Count")
            exit()
        
        message = "Reading frames..."
        print(message)
        await websocket.send_json(JsonEncoder.init_reading_frames(message))
        for i in tqdm(range(total_frame)):
            ret, frame = source.read()
            if not (ret or frame):
                print("Error in Frame Read")
                break
            self.frame_inp.append(frame)
            if self.shape == (0, 0):
                self.shape = (frame.shape[0], frame.shape[1])
            await websocket.send_json(JsonEncoder.update_step_json("reading", i, total_frame))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        print("[INFO] Video Import Completed")

    async def write(self, frames_out, path, websocket: WebSocket= None):
        h, w = frames_out[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        # fourcc = -1
        writer = cv2.VideoWriter(path, fourcc, self.fps, (w, h), True)

        message = "Writing frames..."
        print(message)
        await websocket.send_json(JsonEncoder.init_video_writing_json(message))
        total = len(frames_out)
        for i, frame in enumerate(frames_out):          
            writer.write(frame)
            await websocket.send_json(JsonEncoder.update_step_json("writing", i, total))
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:              
                raise

        print("[INFO] Video Export Completed")
