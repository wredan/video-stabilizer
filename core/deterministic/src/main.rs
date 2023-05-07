pub mod config_parameters;
mod motion_estimation;
use config_parameters::ConfigParameters;
use frames_print_debug::FramesPrintDebug;
use kdam::tqdm;
use motion_estimation::motion_estimation::MotionEstimation;
use opencv::core::{Point, Scalar};
use opencv::imgproc::arrowed_line;
use opencv::prelude::Mat;

mod utils;
use utils::DFD;

mod video;
use crate::video::*;

mod opencv_test;
use crate::opencv_test::opencv_test;

use std::env;

mod frame_position_smoothing;
use frame_position_smoothing::frame_position_smoothing::{
    global_correction_motion_vectors,
};

mod frames_print_debug;

fn main() {
    env::set_var("RUST_BACKTRACE", "1");
    // OpenCV Test
    // opencv_test("./assets/lena.png");

    // Config
    let config_parameters = ConfigParameters::default();

    // Import Video Sequence
    let mut video = Video::new(&config_parameters.path_in);
    video.read_frames(config_parameters.gray);

    let mut motion_estimation = MotionEstimation::new(&mut video, &config_parameters);

    if config_parameters.demo && config_parameters.frames_print_debug {
        let (_, frame_anchor_p, frame_motion_field, global_motion_vector) =
            motion_estimation.demo(72, 73);
        FramesPrintDebug::show_demo_frame(&mut FramesPrintDebug::GLOBAL_MOTION_VEC, &video, 72, &frame_motion_field, &global_motion_vector, "motion field", "global motion vector", "Demo");
        
    } else {
        let (global_motion_vectors, frame_anchor_p_vec, frame_motion_field_vec, frame_global_motion_vec) = motion_estimation.video_processing();
        let global_correction_vector: Vec<(f32, f32)> =
            global_correction_motion_vectors(&video.frames_inp, &global_motion_vectors, 30.0, 15.0);

        let global_corrected_vect_frames = frame_position_smoothing::frame_position_smoothing::plot_global_corrected_motion_vector(&global_correction_vector, video.shape.1.clone(), video.shape.0.clone());

        //FramesPrintDebug::write_video(&mut FramesPrintDebug::GLOBAL_MOTION_VEC, &video, &frame_motion_field_vec, &frame_global_motion_vec, "motion field", "global motion vector", "Demo", "./out/test.mp4", 30.0);
        FramesPrintDebug::write_video(&mut FramesPrintDebug::CORRECT_VEC, &video, &frame_global_motion_vec, &global_corrected_vect_frames, "motion field", "global correction motion vector", "Demo", "./out/test.mp4", 30.0);

    }
}
