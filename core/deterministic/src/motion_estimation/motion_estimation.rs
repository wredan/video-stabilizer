use std::time::Instant;

use kdam::tqdm;
use opencv::prelude::Mat;

use crate::{utils::{DFD, self}, video::Video};

use super::block_matching::BlockMatching;

pub struct MotionEstimation<'a> {
    block_matching: BlockMatching,
    video: &'a mut Video,
    path_out: String,
    title: String,
    predict_from_prev: bool, // temporaneo
}

impl<'a> MotionEstimation<'a> {
    pub fn new(video: &'a mut Video) -> Self {
        // Block Matching Parameters
        let dfd: DFD = DFD::MSE; // Displaced frame difference
        let block_size: (i32, i32) = (128, 128);
        let search_range: i32 = 20;
        let predict_from_prev: bool = false;
        let motion_intensity: bool = true;

        let path_out: String = format!("./out/test_airplane_seat-{}-Size{}-{}-{}.mp4", 
            if matches!(dfd, DFD::MSE) { "MSE" } else { "MAD" }, block_size.0, search_range, if predict_from_prev { "prev" } else { "orig" });

        let title = format!("Block Matching Algorithm - DFD: {} | {:?} | Search Range: {}", if matches!(dfd, DFD::MSE) { "MSE" } else { "MAD" }, block_size, search_range);
        println!("{}", title);

        Self {
            block_matching: BlockMatching::new(dfd.clone(), block_size, search_range, motion_intensity),
            video: video,
            path_out: path_out,
            title: title,
            predict_from_prev: predict_from_prev
        }
    }

    pub fn demo(&mut self, anchor_index: usize, target_index: usize) {            
        let start_time = Instant::now();

        let anchor_frame = self.video.frames_inp[anchor_index].clone();
        let target_frame = self.video.frames_inp[target_index].clone();
    
        self.block_matching.step(anchor_frame.clone(), target_frame.clone());
    
        let anchor_p: &Mat = self.block_matching.anchor_p.as_ref().unwrap();
        let motion_field: &Mat = self.block_matching.motion_field.as_ref().unwrap();
    
        let out = self.video.visualize(&anchor_frame, &target_frame, &motion_field, &anchor_p, &self.title, anchor_index, target_index);
    
        let elapsed_time = start_time.elapsed().as_secs_f32();
        println!("Elapsed time: {:.3} secs", elapsed_time);
    
        utils::opencv_show_image("Demo 2 frames", &out);
    
        utils::opencv_imwrite("demo.png", &out);
    }
    
    pub fn video_processing(&mut self) {
        // Video Motion Estimation Processing
        let start_time = Instant::now();
        let N = 5;

        print!("Motion Estimation (Block Matching - Three Step Search) processing...");
    
        let mut prev_prediction = None;
        for f in tqdm!(0..self.video.total_frame.unwrap() - 1) {
            let anchor = if self.predict_from_prev {
                if f % N == 0 {
                    self.video.frames_inp[f as usize].clone()
                } else {
                    prev_prediction.clone().unwrap()
                }
            } else {
                self.video.frames_inp[f as usize].clone()
            };
            let target = self.video.frames_inp[(f + 1) as usize].clone();
    
            self.block_matching.step(anchor.clone(), target.clone());
    
            let anchor_p = self.block_matching.anchor_p.as_ref().unwrap();
            let motion_field = self.block_matching.motion_field.as_ref().unwrap();
    
            let out = self.video.visualize(
                &anchor,
                &target,
                &motion_field,
                &anchor_p,
                &self.title,
                f as usize,
                (f + 1) as usize,
            );
            self.video.frames_out.push(out);
    
            if self.predict_from_prev {
                prev_prediction = Some(anchor_p.clone());
            }
        }
    
        let elapsed_time = start_time.elapsed();
        println!("Elapsed time: {:.3} secs", elapsed_time.as_secs_f64());
        self.video.write(&self.path_out, 30.0);
        println!("{}", self.path_out);
    }
}
