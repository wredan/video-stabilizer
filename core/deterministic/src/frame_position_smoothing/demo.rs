use kdam::tqdm;
use opencv::{core::{Scalar, Point, CV_8UC1, CV_32FC1}, prelude::{MatTraitConst, Mat}, imgproc::arrowed_line};
use crate::frame_position_smoothing::frame_position_smoothing::{forward_dft, low_pass_filter, inverse_dft, correction_vector};

pub fn demo_global_correction_motion_vectors(global_motion_vector: &(f32, f32), fps: f32, sigma: f32) -> (f32, f32) {
    println!("Global Correction Vector Calculating...");
    let data = Mat::from_slice(&[global_motion_vector.0, global_motion_vector.1]).unwrap().reshape(1, 1).unwrap();
    let mut data_float = Mat::default();
    data.convert_to(&mut data_float, CV_32FC1, 1.0, 0.0).unwrap();    
    let fourier_transform = forward_dft(&data_float);
    let filtered_data = low_pass_filter(&fourier_transform, sigma);
    let inverse_filtered_data = inverse_dft(&filtered_data);
    let correction_vector = correction_vector(&global_motion_vector, &inverse_filtered_data);
    let global_corrected_vector = (
        correction_vector.0 + global_motion_vector.0,
        correction_vector.1 + global_motion_vector.1,
    );

    global_corrected_vector
}

pub fn plot_global_corrected_motion_vector(global_corrected_vector: &Vec<(f32, f32)>, width: i32, height: i32) -> Vec<Option<Mat>> {

    let mut global_corrected_vect_frames: Vec<Option<Mat>> = vec![];
    for corrected_vector in global_corrected_vector.iter() {
        let frame = single_step_plot(corrected_vector, height, width);
        global_corrected_vect_frames.push(Some(frame));
    }
    
    global_corrected_vect_frames
}

pub fn single_step_plot(corrected_vector: &(f32, f32), height: i32, width: i32) -> Mat {
    let scale_factor = 1;
    let frame_res = Mat::new_rows_cols_with_default(height, width, CV_8UC1, Scalar::all(0.));
    if let Ok(mut frame) = frame_res {
        let intensity = 255;
        let (x2, y2) = (corrected_vector.0 as i32 * scale_factor + width / 2 , corrected_vector.1 as i32 * scale_factor + height / 2);
        arrowed_line(
            &mut frame,
            Point::new(width / 2, height / 2),
            Point::new(x2, y2),
            Scalar::new(intensity as f64, intensity as f64, intensity as f64, intensity as f64),
            2,
            8,
            0,
            0.3,
        )
        .unwrap();
        frame

    } else {
        // handle error
        panic!("Failed to create new frame for motion field");
    }
}