use kdam::tqdm;
use opencv::prelude::Mat;

use crate::{
    video::Video, config_parameters::{ConfigParameters},
};

use super::{block_matching::BlockMatching};

pub struct MotionEstimation<'a> {
    pub block_matching: BlockMatching<'a>,
    video: &'a Video<'a>,
    config_parameters: &'a ConfigParameters,
}

impl<'a> MotionEstimation<'a> {
    pub fn new(video: &'a mut Video, config_parameters: &'a ConfigParameters) -> Self {
        Self {
            block_matching: BlockMatching::new(
                config_parameters.dfd.clone(),
                config_parameters.block_size.clone(),
                config_parameters.search_range.clone(),
                config_parameters.motion_intensity.clone(),
                config_parameters,
            ),
            video: video,
            config_parameters: config_parameters,
        }
    }

    pub fn demo(&mut self, anchor_index: usize, target_index: usize) -> (Option<(f32, f32)>, Option<Mat>, Option<Mat>, Option<Mat>) {
        if self.config_parameters.frames_print_debug {
            let anchor_frame = self.video.frames_inp[anchor_index].clone();
            let target_frame = self.video.frames_inp[target_index].clone();

            return self.block_matching.step(anchor_frame.clone(), target_frame.clone());
        }
        (None, None, None, None)
    }

    pub fn video_processing(&mut self) -> (Vec<(f32, f32)>, Vec<Option<Mat>>, Vec<Option<Mat>>, Vec<Option<Mat>>){
        // Video Motion Estimation Processing
        println!("Motion Estimation (Block Matching - Three Step Search) processing...");
        let mut global_motion_vectors: Vec<(f32, f32)> = vec![];
        let mut frame_anchor_p_vec: Vec<Option<Mat>> = vec![];
        let mut frame_motion_field_vec: Vec<Option<Mat>> = vec![];
        let mut frame_global_motion_vec: Vec<Option<Mat>> = vec![];
        for f in tqdm!(0..self.video.total_frame.unwrap() - 1) {
            let anchor =  self.video.frames_inp[f as usize].clone();
            let target = self.video.frames_inp[(f + 1) as usize].clone();

            if self.config_parameters.frames_print_debug {
                let (global_motion_vec, frame_anchor_p, frame_motion_field, frame_global_motion_vector) = self.block_matching.step(anchor.clone(), target.clone());

                global_motion_vectors.push(global_motion_vec.unwrap());
                frame_anchor_p_vec.push(frame_anchor_p);
                frame_motion_field_vec.push(frame_motion_field);
                frame_global_motion_vec.push(frame_global_motion_vector);
            } else {
                let (global_motion_vec, _, _, _) = self.block_matching.step(anchor.clone(), target.clone());
                global_motion_vectors.push(global_motion_vec.unwrap());

            }
        }
        (global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec)
    }
}
