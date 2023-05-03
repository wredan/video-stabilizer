use crate::DFD;

use opencv::prelude::Mat;

use opencv::core::Rect;

use super::block::Block;

pub struct ThreeStepSearch {}

impl ThreeStepSearch {
    pub fn new() -> Self {
        Self {}
    }

    pub fn run(
        &mut self,
        search_range: i32,
        blocks: &mut Vec<Block>,
        min: &(i32, i32, i32, i32),
        max: &(i32, i32, i32, i32),
        max_mv_amp: &mut f64,
        anchor: &Mat,
        target: &Mat,
        dfd: &mut DFD,
    ) {
        // define search step and search area
        let search_step: Vec<i32> = vec![search_range / 2, search_range / 3, search_range / 6];
        let mut search_areas: Vec<Vec<(i32, i32)>> = vec![];
        for step in search_step {
            let dx: [i32; 3] = [-step, 0, step];
            let dy: [i32; 3] = [-step, 0, step];
            let mut search_area: Vec<(i32, i32)> = vec![];
            for x in &dx {
                for y in &dy {
                    search_area.push((*x, *y));
                }
            }
            search_areas.push(search_area);
        }

        // search for motion vectors for each block
        for block in blocks {
            let mut step_coord: (i32, i32, i32, i32) = block.coord;
            for i in 0..2 {
                step_coord = self.single_step_search(
                    block,
                    step_coord,
                    &search_areas[i],
                    min,
                    max,
                    anchor,
                    target,
                    dfd,
                );
            }
            // get best-match coordinates
            let (x, y, _, _) = step_coord;
            // set the difference as motion-vector
            block.mv = (x - block.coord.0, y - block.coord.1);
            block.calculate_mv_amp(max_mv_amp, min, max);
        }
    }

    fn single_step_search(
        &mut self,
        block: &Block,
        search_coord: (i32, i32, i32, i32),
        search_area: &[(i32, i32)],
        min: &(i32, i32, i32, i32),
        max: &(i32, i32, i32, i32),
        anchor: &Mat,
        target: &Mat,
        dfd: &mut DFD,
    ) -> (i32, i32, i32, i32) {
        // get block coordinates for anchor frame
        let (x, y, w, h) = block.coord;

        // extract the block from anchor frame
        let roi_anchor = Rect::new(x, y, w, h);
        let block_a = Mat::roi(anchor, roi_anchor).unwrap();

        // displaced frame difference := initially infinity
        let mut dfd_norm_min = f64::INFINITY;

        // best-match coordinates
        let mut coord = (x, y, w, h);

        // search the matched block in target frame in search area
        for (dx, dy) in search_area {
            let (mut x, mut y, w, h) = search_coord;
            // check if the searched box inside the target frame
            if !block.check_inside_frame(x + dx, y + dy, min, max) {
                continue;
            }
            x += dx;
            y += dy;

            // extract the block from target frame
            let roi_target = Rect::new(x, y, w, h);
            let block_t = Mat::roi(target, roi_target).unwrap();

            // calculate displaced frame distance
            let dfd_norm = match dfd {
                DFD::MAD => dfd.mad(&block_a, &block_t),
                DFD::MSE => dfd.mse(&block_a, &block_t),
            };

            // update best-match coordinates
            if dfd_norm < dfd_norm_min {
                dfd_norm_min = dfd_norm;
                coord = (x, y, w, h);
            }
        }

        coord
    }
}
