from collections import defaultdict
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
        
        # for block in raw_blocks:
        #     print(block)

        three_step_search = ThreeStepSearch(self.config_parameters.search_range, raw_blocks, anchor, target)
        blocks = three_step_search.run()

        global_motion_vec = self.frame_global_motion_vector(blocks)

        if self.config_parameters.frames_print_debug:
            frame_anchor_p = self.blocks2frame(blocks, anchor)
            frame_motion_field = self.plot_motion_field(blocks)
            frame_global_motion_vector = self.plot_global_motion_vector(global_motion_vec)
            return global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector
        else:
            return global_motion_vec, None, None, None

    def frame2blocks(self):
        """Divides the frame matrix into block objects."""

        (H,W) = self.anchor_shape 
        (sizeH,sizeW) = self.config_parameters.block_size

        blocks = [Block(w*sizeW, h*sizeH, sizeW, sizeH) for h in range(H//sizeH) for w in range(W//sizeW)]

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
            intensity = int(255. * block.mv_amp / Block.max_mv_amp) if self.config_parameters.motion_intensity and Block.max_mv_amp != 0 else 100
            x2, y2 = block.mv[0] + block.center[0], block.mv[1] + block.center[1]
            cv2.arrowedLine(frame, block.center, (x2, y2), intensity, 1, tipLength=0.3)
        return frame

    def plot_global_motion_vector(self, global_motion_vec):
        frame = np.zeros((self.anchor_shape[0], self.anchor_shape[1]), dtype=np.uint8)
        intensity = 255
        x2, y2 = int(global_motion_vec[0] + self.anchor_shape[1] / 2), int(global_motion_vec[1] + self.anchor_shape[0] / 2)
        cv2.arrowedLine(frame, (self.anchor_shape[1] // 2, self.anchor_shape[0] // 2), (x2, y2), intensity, 2, 8, 0, 0.3)

        return frame

    def frame_global_motion_vector(self, blocks: List[Block]):
        # Count the number of blocks moving in each direction
        count = defaultdict(int)
        for block in blocks:
            direction = (round(block.mv[0]), round(block.mv[1]))
            count[direction] += 1

        # Calculate the weighted sum of the motion vectors
        sum_x, sum_y = 0, 0
        total_weight = 0
        for block in blocks:
            direction = (round(block.mv[0]), round(block.mv[1]))
            weight = count[direction]
            sum_x += block.mv[0] * weight
            sum_y += block.mv[1] * weight
            total_weight += weight

        # Calculate the weighted average
        return (sum_x / total_weight, sum_y / total_weight)

