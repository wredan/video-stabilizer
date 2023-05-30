import cv2
import numpy as np
from tqdm import tqdm

class FramesPrintDebug:
    def __init__(self):
        pass

    def show_demo_frame(self, video, a, third_quadrant, fourth_quadrant, third_quadrant_title, fourth_quadrant_title, window_title):
        anchor = video.frames_inp[a]
        target = video.frames_inp[a + 1]

        print(f"Showing frame with {third_quadrant_title} and {fourth_quadrant_title}...")

        out = self.visualize_single_frame(
            anchor,
            target,
            third_quadrant,
            third_quadrant_title,
            fourth_quadrant,
            fourth_quadrant_title,
            window_title,
            a
        )

        cv2.imshow("Demo frame", out)
        cv2.imwrite("./out/demo.png", out)

    def write_video(self, global_motion_vectors, video, third_quadrant, fourth_quadrant, third_quadrant_title, fourth_quadrant_title, window_title, path, fps, second_override, second_quadrant):
        print(f"Writing video with {third_quadrant_title} and {fourth_quadrant_title}...")

        frames_out = []
        for f in tqdm(range(len(video.frames_inp) - 1)):
            anchor = video.frames_inp[f]
            target = second_quadrant[f] if second_override else video.frames_inp[f + 1]
            out = self.visualize_single_frame(
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

        self.write(frames_out, path, fps)

    def write(self, frames_out, path, fps):
        h, w = frames_out[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        writer = cv2.VideoWriter(path, fourcc, fps, (w, h), True)

        for frame in frames_out:
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            writer.write(frame)

        print("[INFO] Video Export Completed")

    def visualize_single_frame(self, anchor, target, third_quadrant, third_quadrant_title, fourth_quadrant, fourth_quadrant_title, title, a):
        h, w = 70, 10
        H, W = anchor.shape[:2]
        HH, WW = h + 2 * H + 20, 2 * (W + w)
        frame = np.full((HH, WW), 255, dtype=np.uint8)

        cv2.putText(frame, title, (w, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"anchor-{a:03}", (w, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, f"target-{a+1:03}", (w + W, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, third_quadrant_title, (w, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)
        cv2.putText(frame, fourth_quadrant_title, (w + W, h + H + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 1, cv2.LINE_AA)

        # reg of interest
        frame[h:h+H, :W] = anchor
        frame[h:h+H, W+w:2*W+w] = target
        frame[h+H+20:2*H+h+20, :W] = third_quadrant
        frame[h+H+20:2*H+h+20, W+w:2*W+w] = fourth_quadrant

        return frame
