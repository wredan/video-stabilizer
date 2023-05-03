use crate::DFD;

use super::{block::Block, three_step_search};
use opencv::{
  prelude::{Mat, MatTraitConst, MatTraitConstManual}, core::{Scalar, Rect, Point, CV_8UC1}, imgproc::arrowed_line
};
pub struct BlockMatching {
    dfd: DFD,
    block_size: (i32, i32),
    search_range: i32,
    motion_intensity: bool,
    anchor: Option<Mat>,
    target: Option<Mat>,
    shape: Option<(i32, i32)>,
    blocks: Vec<Block>,
    pub anchor_p: Option<Mat>,
    pub motion_field: Option<Mat>,
    min: (i32, i32, i32, i32), // coordinate minime
    max: (i32, i32, i32, i32), // coordinate massime
    max_mv_amp: f64, // ampiezza massima tra tutti i blocchi
}

impl BlockMatching {
    pub fn new(dfd: DFD, block_size: (i32, i32), search_range: i32, motion_intensity: bool) -> Self {
        Self {
            dfd,
            block_size,
            search_range,
            motion_intensity,
            anchor: None,
            target: None,
            shape: None,
            blocks: Vec::new(),
            anchor_p: None,
            motion_field: None,
            min: (0, 0, 0, 0),
            max: (i32::MAX, i32::MAX, 0, 0),
            max_mv_amp: 0.0,
        }
    }

    pub fn step(&mut self, anchor: Mat, target: Mat) {
        self.anchor = Some(anchor.clone());
        self.target = Some(target);
        let anchor_size: opencv::core::Size_<i32> = anchor.size().unwrap();
        self.shape = Some((anchor_size.height, anchor_size.width));
    
        self.frame2blocks();
    
        three_step_search::run(self.search_range, &mut self.blocks, &self.min, &self.max, &mut self.max_mv_amp, &self.anchor.as_ref().unwrap(), &self.target.as_ref().unwrap(), &mut self.dfd);

        self.plot_motion_field();
        self.blocks2frame();
    }    

    fn frame2blocks(&mut self) {
        // extract frame dimensions and block size
        let (h, w) = match self.shape {
            Some((h, w)) => (h, w),
            None => panic!("Cannot get shape of video frame"),
        };
        let (size_h,size_w) = self.block_size;

        // initialize block objects
        self.blocks = Vec::new();
        for h in 0..h / size_h {
            for w in 0..w / size_w {
                // initialize Block() objects with 
                // upper-left coordinates and block size
                let x = w * size_w;
                let y = h * size_h;
                let block = Block::new(x, y, size_w, size_h);
                self.blocks.push(block);
            }
        }

        // store the upper-left and bottom-right block coordinates
        // for future check if the searched block inside the frame
        self.min = self.blocks[0].coord;
        self.max = self.blocks[self.blocks.len() - 1].coord;
    }

    fn blocks2frame(&mut self) {
        // Construct the predicted frame
        let frame = Mat::new_rows_cols_with_default(self.shape.unwrap().0 as i32, self.shape.unwrap().1 as i32, CV_8UC1, Scalar::all(0.0)).unwrap();
    
        for block in &self.blocks {
            // get block coordinates for anchor frame
            let (x, y, w, h) = block.coord;
            // extract the block from anchor frame
            let block_a = Mat::roi(&self.anchor.as_ref().unwrap(), Rect::new(x, y, w, h)).unwrap();
            // append motion-vector to prediction coordinates 
            let (x, y) = (x + block.mv.0, y + block.mv.1);
            // shift the block to new coordinates
            let mut block_shifted = Mat::roi(&frame, Rect::new(x, y, w, h)).unwrap();
            block_a.copy_to(&mut block_shifted);
        }
    
        self.anchor_p = Some(frame);
    }

    fn plot_motion_field(&mut self) {
        let frame_res = Mat::new_rows_cols_with_default(self.shape.unwrap().0, self.shape.unwrap().1, opencv::core::CV_8UC1, Scalar::all(0.));
        if let Ok(mut frame) = frame_res {
            for block in &self.blocks {
                let intensity = if self.motion_intensity {
                    (255. * block.mv_amp / self.max_mv_amp) as i32
                } else {
                    255
                };
                let intensity = if intensity < 100 { 100 } else { intensity };
                let (x2, y2) = (block.mv.0 + block.center.0, block.mv.1 + block.center.1);
                arrowed_line(
                    &mut frame,
                    Point::new(block.center.0, block.center.1),
                    Point::new(x2, y2),
                    Scalar::new(intensity as f64, intensity as f64, intensity as f64, intensity as f64),
                    1,
                    8,
                    0,
                    0.3,
                )
                .unwrap();
            }
    
            self.motion_field = Some(frame);
        } else {
            // handle error
            panic!("Failed to create new frame for motion field");
        }
    }
    
    
    

    
}

