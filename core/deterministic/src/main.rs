pub mod config_parameters;
mod motion_estimation;
mod utils;
mod video;
mod opencv_test;
mod frame_position_smoothing;
mod frames_print_debug;

use config_parameters::ConfigParameters;
use motion_estimation::motion_estimation::MotionEstimation;
use frame_position_smoothing::{
    demo::{
        demo_global_correction_motion_vectors, plot_global_corrected_motion_vector,
        single_step_plot,
    },
    frame_position_smoothing::{shift_frames, global_correction_motion_vectors, crop_frames},
};
use frames_print_debug::FramesPrintDebug;
use utils::DFD;
use video::*;
use opencv_test::opencv_test;

use std::env;

fn run_demo(
    config_parameters: &ConfigParameters,
    video: &Video,
    motion_estimation: &mut MotionEstimation,
) {
    let (global_motion_vector, frame_anchor_p, frame_motion_field, frame_global_motion_vector) =
        motion_estimation.demo(72, 73);

    let global_correction_vector: (f32, f32) =
        demo_global_correction_motion_vectors(&global_motion_vector.unwrap(), 30.0, 200.0);

    let global_corrected_vect_frames = single_step_plot(
        &global_correction_vector,
        video.shape.0.clone(),
        video.shape.1.clone(),
    );

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
}

fn process_video(config_parameters: &ConfigParameters, video: &Video, motion_estimation: &mut MotionEstimation) {
    let (
        global_motion_vectors,
        frame_anchor_p_vec,
        frame_motion_field_vec,
        frame_global_motion_vec,
    ) = motion_estimation.video_processing();

    let global_correct_motion_vectors: Vec<(f32, f32)> =
        global_correction_motion_vectors(&global_motion_vectors, config_parameters.filter_intensity, &config_parameters.base_path);

    let global_corrected_vect_frames = plot_global_corrected_motion_vector(
        &global_correct_motion_vectors,
        video.shape.1.clone(),
        video.shape.0.clone(),
    );

    let shifted_frames = shift_frames(&video.frames_inp, &global_correct_motion_vectors, config_parameters.intensity);
    // let cropped_frames = crop_frames(&shifted_frames, &global_correct_motion_vectors).unwrap();

    // FramesPrintDebug::write(&mut FramesPrintDebug::CORRECT_VEC, shifted_frames, "./out/2/test.mp4", 30.0);
    
    FramesPrintDebug::write_video(
        &mut FramesPrintDebug::GLOBAL_MOTION_VEC,
        &global_correct_motion_vectors,
        &video,
        &frame_global_motion_vec,
        &global_corrected_vect_frames,
        "motion field",
        "global correction motion vector",
        "Demo",
        &format!("{}{}", &config_parameters.base_path, &config_parameters.path_out),
        30.0,
        true,
        &shifted_frames,            
    );
}

fn main() {
    env::set_var("RUST_BACKTRACE", "1");
    // opencv_test("./assets/lena.png");

    let config_parameters = ConfigParameters::default();

    let mut video = Video::new(&config_parameters.path_in);
    video.read_frames(config_parameters.gray);

    let mut motion_estimation = MotionEstimation::new(&video, &config_parameters);

    if config_parameters.demo && config_parameters.frames_print_debug {
        run_demo(&config_parameters, &video, &mut motion_estimation);
    } else {
        process_video(&config_parameters, &video, &mut motion_estimation);
    }
}
