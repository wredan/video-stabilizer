pub mod config_parameters;
mod motion_estimation;
use config_parameters::ConfigParameters;
use frame_position_smoothing::{
    demo::{
        demo_global_correction_motion_vectors, plot_global_corrected_motion_vector,
        single_step_plot,
    },
    frame_position_smoothing::{shift_frames},
};
use frames_print_debug::FramesPrintDebug;
use motion_estimation::motion_estimation::MotionEstimation;

mod utils;
use utils::DFD;

mod video;
use crate::video::*;

mod opencv_test;
use crate::opencv_test::opencv_test;

use std::env;

mod frame_position_smoothing;
use frame_position_smoothing::frame_position_smoothing::global_correction_motion_vectors;

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
        let (global_motion_vector, frame_anchor_p, frame_motion_field, frame_global_motion_vector) =
            motion_estimation.demo(72, 73);

        let global_correction_vector: (f32, f32) =
            demo_global_correction_motion_vectors(&global_motion_vector.unwrap(), 30.0, 200.0);

        let global_corrected_vect_frames = single_step_plot(
            &global_correction_vector,
            video.shape.0.clone(),
            video.shape.1.clone(),
        );

        //FramesPrintDebug::show_demo_frame(&mut FramesPrintDebug::GLOBAL_MOTION_VEC, &video, 72, &frame_motion_field, &global_motion_vector, "motion field", "global motion vector", "Demo");
        FramesPrintDebug::show_demo_frame(
            &mut FramesPrintDebug::CORRECT_VEC,
            &video,
            72,
            &frame_global_motion_vector,
            &Some(global_corrected_vect_frames),
            "motion field",
            "global motion vector",
            "Demo",
        );
    } else {
        let (
            global_motion_vectors,
            frame_anchor_p_vec,
            frame_motion_field_vec,
            frame_global_motion_vec,
        ) = motion_estimation.video_processing();

        let global_correct_motion_vectors: Vec<(f32, f32)> =
            global_correction_motion_vectors(&global_motion_vectors, config_parameters.sigma);


        let global_corrected_vect_frames = plot_global_corrected_motion_vector(
            &global_correct_motion_vectors,
            video.shape.1.clone(),
            video.shape.0.clone(),
        );

        let shifted_frames = shift_frames(&video.frames_inp, &global_correct_motion_vectors, config_parameters.intensity);

        // let cropped_frames = crop_frames(&shifted_frames, &global_correct_motion_vectors);
        //FramesPrintDebug::write_video(&mut FramesPrintDebug::GLOBAL_MOTION_VEC, &video, &frame_motion_field_vec, &frame_global_motion_vec, "motion field", "global motion vector", "Demo", "./out/test.mp4", 30.0);
        FramesPrintDebug::write_video(
            &mut FramesPrintDebug::GLOBAL_MOTION_VEC,
            &global_correct_motion_vectors,
            &video,
            &frame_global_motion_vec,
            &global_corrected_vect_frames,
            "motion field",
            "global correction motion vector",
            "Demo",
            &config_parameters.path_out,
            30.0,
            true,
            &shifted_frames,            
        );

        // FramesPrintDebug::write_video(
        //     &mut FramesPrintDebug::CORRECT_VEC,
        //     &global_motion_vectors,
        //     &video,
        //     &frame_motion_field_vec,
        //     &frame_global_motion_vec,
        //     "motion field",
        //     "global correction motion vector",
        //     "Demo",
        //     &format!("./out/test_sigma_{}_intensity_{}_motion.mp4", sigma, intensity),
        //     30.0,
        //     false,
        //     &shifted_frames,  
        // );
    }
}
