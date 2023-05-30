import itertools
import numpy as np
from typing import List, Tuple
from .block import Block
from utils import DFD

class ThreeStepSearch:
    def __init__(self, search_range: int, blocks: List[Block], anchor: np.ndarray, target: np.ndarray):
        """
        Initialize the ThreeStepSearch class with the given parameters.
        - search_range: the range within which we search for motion vectors.
        - blocks: a list of Block objects, representing the blocks in the anchor frame.
        - anchor: the anchor frame as a 2D NumPy array.
        - target: the target frame as a 2D NumPy array.
        """
        self.search_range = search_range
        self.blocks = blocks
        self.anchor = anchor
        self.target = target
        self.search_step = [search_range // 2, search_range // 3, search_range // 6]  # Define the search steps
        self.search_areas = self._get_search_areas() 
    
    def _get_search_areas(self):
        """
        Generate the search areas based on the search steps.
        """
        search_areas = []
        for step in self.search_step:
            dx = dy = [-step, 0, step]
            search_areas.append([r for r in itertools.product(dx, dy)])
        return search_areas

    def run(self):
        """
        Run the Three-Step Search algorithm to calculate motion vectors for each block.
        """
        for block in self.blocks:
            # For each block, perform a three-step search to find the motion vector
            step1 = self._single_step_search(block, block.coord, self.search_areas[0])
            step2 = self._single_step_search(block, step1, self.search_areas[1])
            step3 = self._single_step_search(block, step2, self.search_areas[2])

            # Compute the motion vector for the block and update its mv property
            x, y, _, _ = step3
            block.mv = (x - block.coord[0], y - block.coord[1])
            block.calculate_mv_amp()
        
        return self.blocks

    def _single_step_search(self, block: Block, search_coord: Tuple[int, int, int, int], search_area: List[Tuple[int, int]]):
        """
        Perform a single step search for a block.
        - block: a Block object for which we're searching the motion vector.
        - search_coord: the starting coordinate for the search.
        - search_area: the area within which we perform the search.
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
