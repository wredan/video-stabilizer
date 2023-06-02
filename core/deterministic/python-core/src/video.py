import cv2
import numpy as np
from tqdm import tqdm

class Video:
    def __init__(self, path):
        self.path = path
        self.frame_inp = []
        self.gray_frame_inp = []
        self.shape = (0, 0) # H,W

    def read_frames(self):
        try: 
            source = cv2.VideoCapture(self.path)
            total_frame = int(source.get(cv2.CAP_PROP_FRAME_COUNT))
        except:
            print("Error in Path or Frame Count")
            exit()
        
        print("[INFO] Reading frames...", total_frame)
        for i in tqdm(range(total_frame)):
            ret, frame = source.read()
            if not (ret or frame):
                print("Error in Frame Read")
                break
            self.frame_inp.append(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.shape == (0, 0):
                self.shape = (frame.shape[0], frame.shape[1])

            self.gray_frame_inp.append(frame)

        print("[INFO] Video Import Completed")

    def write(self, frames_out, path, fps, gray = False):
        h, w = frames_out[0].shape[:2]
        # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fourcc = -1
        writer = cv2.VideoWriter(path, fourcc, fps, (w, h), True)

        for frame in frames_out:          
            writer.write(frame)

        print("[INFO] Video Export Completed")
