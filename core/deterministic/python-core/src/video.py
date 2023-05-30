import cv2
import numpy as np
from tqdm import tqdm

class Video:
    def __init__(self, path):
        self.path = path
        self.frames_inp = []
        self.frames_out = []
        self.shape = (0, 0) # H,W
        self.gray = False

    def read_frames(self, gray=False):
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
            if gray:
                self.gray = True
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.shape == (0, 0):
                self.shape = (frame.shape[0], frame.shape[1])

            self.frames_inp.append(frame)

        print("[INFO] Video Import Completed")

    def visualize(self, anchor, target, motion_field, anchor_p, title, a, t):
        h, w = 70, 10
        H, W = anchor.shape[:2]
        HH, WW = h + 2 * H + 20, 2 * (W + w)
        frame = np.full((HH, WW), 255, dtype=np.uint8)

        cv2.putText(frame, title, (w, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"anchor-{a:03}", (w, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"target-{t:03}", (w + W, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, "motion field", (w, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, "predicted anchor", (w + W, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)

        frame[h:h+H, :W] = anchor
        frame[h:h+H, W+w:2*W+w] = target
        frame[h+H+20:2*H+20+h, :W] = motion_field
        frame[h+H+20:2*H+20+h, W+w:2*W+w] = anchor_p

        return frame

    def write(self, path, fps):
        h, w = self.frames_out[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        writer = cv2.VideoWriter(path, fourcc, fps, (w, h), True)

        for frame in self.frames_out:
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            writer.write(frame)

        print("[INFO] Video Export Completed")
