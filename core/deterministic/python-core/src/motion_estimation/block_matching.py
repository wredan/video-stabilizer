import numpy as np
import cv2
from typing import List
from .block import Block
from .three_step_search import ThreeStepSearch
from config.config import ConfigParameters

class BlockMatching:
    def __init__(self, config_parameters: ConfigParameters):
        
        # Parameters
        self.config_parameters = config_parameters
        
        # Frames
        self.target = None
        self.anchor_shape = None

        self.anchor_p = None

    def step(self, anchor, target): # Single-step for given frames
        self.anchor_shape  = anchor.shape

        raw_blocks = self.frame2blocks()

        three_step_search = ThreeStepSearch(self.config_parameters.search_range, raw_blocks, anchor, target)
        blocks = three_step_search.run()

        global_motion_vec = self.frame_global_motion_vector(blocks)

        if self.config_parameters.frames_print_debug:
            frame_anchor_p = self.blocks2frame(blocks, anchor)
            frame_motion_field = self.plot_motion_field()
            frame_global_motion_vector = self.plot_global_motion_vector(global_motion_vec)
            return global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector
        else:
            return global_motion_vec, None, None, None

    def frame2blocks(self): # Divides the frame matrix into block objects.
        h, w = self.anchor_shape
        size_h, size_w = self.config_parameters.block_size

        blocks = [Block(x * size_w, y * size_h, size_w, size_h) for y in range(0, h, size_h) for x in range(0, w, size_w)]

        # store the upper-left and bottom-right block coordinates
        # for future check if the searched block inside the frame
        Block.min = blocks[0].coord
        Block.max = blocks[-1].coord
        return blocks

    def blocks2frame(self, blocks: List[Block], anchor): # build up the frame from blocks (predicted frame only use-case)
        frame = np.zeros((self.anchor_shape[0], self.anchor_shape[1]), dtype=np.uint8)

        for block in blocks:
            x, y, w, h = block.coord
            block_a = anchor[y:y+h, x:x+w]
            x, y = x + block.mv[0], y + block.mv[1]
            frame[y:y+h, x:x+w] = block_a

        return frame

    def plot_motion_field(self, blocks: List[Block]): # Construct the motion field from motion-vectors
        frame = np.zeros((self.anchor_shape[0], self.anchor_shape[1]), dtype=np.uint8)
        for block in blocks:
            intensity = int(255. * block.mv_amp / Block.max_mv_amp) if self.motion_intensity else 255
            intensity = 100 if intensity < 100 else intensity
            x2, y2 = block.mv[0] + block.center[0], block.mv[1] + block.center[1]
            cv2.arrowedLine(frame, block.center, (x2, y2), intensity, 1, tipLength=0.3)

        return frame

    def plot_global_motion_vector(self, global_motion_vec):
        frame = np.zeros((self.anchor_shape[0], self.anchor_shape[1]), dtype=np.uint8)
        intensity = 255
        x2, y2 = int(global_motion_vec[0] * 10 + self.anchor_shape[1] / 2), int(global_motion_vec[1] * 10 + self.anchor_shape[0] / 2)
        cv2.arrowedLine(frame, (self.anchor_shape[1] // 2, self.anchor_shape[0] // 2), (x2, y2), intensity, 2, 8, 0, 0.3)

        return frame

    def frame_global_motion_vector(self, blocks: List[Block]):
        sum_x, sum_y = sum(block.mv[0] for block in blocks), sum(block.mv[1] for block in blocks)
        n_blocks = len(blocks)
        return (sum_x / n_blocks, sum_y / n_blocks)
