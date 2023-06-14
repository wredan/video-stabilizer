import itertools
import numpy as np
from typing import List, Tuple
from .block import Block
from src.utils import DFD

class ThreeStepSearch:
    def __init__(self, search_range: int, blocks: List[Block], anchor: np.ndarray, target: np.ndarray):
        """
        Initialize the ThreeStepSearch class with the given parameters.
        """
        self.search_range = search_range // 2
        self.blocks = blocks
        self.anchor = anchor
        self.target = target
    
    def run(self):
        """
        Run the Three-Step Search algorithm to calculate motion vectors for each block.
        """
        for block in self.blocks:
            search_step = self.search_range
            search_coord = block.coord
            first_step = True

            while search_step >= 1:
                # If it's the first step, search 9 points. Otherwise, search 8 points.
                if first_step:
                    search_area = [(dx, dy) for dx in [-search_step, 0, search_step] for dy in [-search_step, 0, search_step]]
                    first_step = False
                else:
                    search_area = [(dx, dy) for dx in [-search_step, 0, search_step] for dy in [-search_step, 0, search_step] if not (dx == 0 and dy == 0)]

                search_coord = self._single_step_search(block, search_coord, search_area)
                search_step //= 2

            # Compute the motion vector for the block and update its mv property
            x, y, _, _ = search_coord
            block.mv = (x - block.coord[0], y - block.coord[1])
            block.calculate_mv_amp()
        
        return self.blocks

    def _single_step_search(self, block: Block, search_coord: Tuple[int, int, int, int], search_area: List[Tuple[int, int]]):
        """
        Perform a single step search for a block.
        """
        # Extract the block from the anchor frame
        x, y, w, h = block.coord
        block_a = self.anchor[y:y+h, x:x+w]

        # Initialize the best match score (DFD) to infinity
        dfd_norm_min = np.inf

        # Initialize the best match coordinates
        coord = (x, y, w, h)

        # Iterate through the search area to find the best match
        for dx, dy in search_area:
            x, y, w, h = search_coord

            # Check if the block is within the frame
            if not block.check_inside_frame(x + dx, y + dy):
                continue

            # Offset the block coordinates
            x += dx
            y += dy

            # Extract the block from the target frame
            block_t = self.target[y:y+h, x:x+w]

            # Compute the DFD using MSE
            dfd_norm = DFD.mse(block_a, block_t)

            # If the DFD is lower than the current minimum, update the minimum and best match coordinates
            if dfd_norm < dfd_norm_min:
                dfd_norm_min = dfd_norm
                coord = (x, y, w, h)

        # Return the best match coordinates
        return coord
