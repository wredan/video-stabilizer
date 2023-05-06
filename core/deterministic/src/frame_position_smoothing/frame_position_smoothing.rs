use kdam::tqdm;
use opencv::{core::{dft, idft, Vec2f, DftFlags, CV_32FC2, Scalar, Point, CV_8UC1, NormTypes, normalize, CV_32FC1}, prelude::{MatTraitConst, MatTrait, Mat}, imgproc::arrowed_line};

fn forward_dft(frame: &Mat) -> Mat {
    // calcola la trasformata di Fourier
    let mut data = Mat::new_rows_cols_with_default(frame.rows(), frame.cols(), CV_32FC2, Scalar::all(0.0)).unwrap();
    // DftFlags::DFT_COMPLEX_OUTPUT = 16;
    dft(frame, &mut data, 16, 0);
    data
}

fn low_pass_filter(data: &Mat, width: &i32, height: &i32, fps: &f32, cutoff: &f32) -> Mat {
    // Applica il filtro passa basso.
    let freq_cutoff = cutoff / fps;
    let mut filtered_data = Mat::new_rows_cols_with_default(*height, *width, CV_32FC2, Scalar::all(0.0)).unwrap();

    for i in 0..*width {
        for j in 0..*height {
            let x = i as f32 / *width as f32 - 0.5;
            let y = j as f32 / *height as f32 - 0.5;
            let distance = (x * x + y * y).sqrt();
            if distance <= freq_cutoff {
                let data_slice = data.at_2d::<Vec2f>(j, i).unwrap();
                let filtered_data_slice = filtered_data.at_2d_mut::<Vec2f>(j, i).unwrap();
                *filtered_data_slice = *data_slice;
            }
        }
    }    
    filtered_data
}

fn inverse_dtf(filtered_data: &Mat) -> Mat {
    let mut inverse_filtered = Mat::new_rows_cols_with_default(filtered_data.rows(), filtered_data.cols(), CV_32FC1, Scalar::all(0.0)).unwrap();
    idft(filtered_data, &mut inverse_filtered, 32, 0);
    let mut inverse_filtered_frame = Mat::default();
    inverse_filtered.convert_to(&mut inverse_filtered_frame, CV_8UC1, 255.0, 0.0);
    inverse_filtered_frame
}


fn correction_vector(frame: &Mat, width: &i32, height: &i32, inverse_filtered_data: &Mat) -> (f32, f32) {
    // calcola la differenza tra la posizione attuale e quella stimata correttamente
    let mut diff_x = 0.0;
    let mut diff_y = 0.0;
    for idx in 0..(*width * *height) {
        let i = idx % *width;
        let j = idx / *width;
        let pixel = frame.at::<u8>(idx).unwrap().clone();
        let filtered_pixel = inverse_filtered_data.at::<u8>(idx).unwrap().clone();
        diff_x += (i as f32 - *width as f32 / 2.0) * (filtered_pixel as f32 - pixel as f32);
        diff_y += (j as f32 - *height as f32 / 2.0) * (filtered_pixel as f32 - pixel as f32);
    }
    (diff_x / (*width * *height) as f32, diff_y / (*width * *height) as f32)
}

pub fn global_correction_motion_vectors(frames: &Vec<Mat>, global_motion_vectors: &Vec<(f32, f32)>, fps: f32, cutoff: f32) -> Vec<(f32, f32)> {
    let mut global_corrected_motion_vectors = vec![];
    println!("Global Correction Vector Calculating...");
    for (frame, global_motion_vector) in tqdm!(frames.iter().zip(global_motion_vectors)) {
        let (width, height) = (frame.cols(), frame.rows());
        let data: Mat = forward_dft(&frame);
        let filtered_data: Mat = low_pass_filter(&data, &width, &height, &fps, &cutoff);
        let inverse_filtered_data: Mat = inverse_dtf(&filtered_data);
        let correction_vector = correction_vector(&frame, &width, &height, &inverse_filtered_data);
        let global_corrected_vector = (
            correction_vector.0 + global_motion_vector.0,
            correction_vector.1 + global_motion_vector.1,
        );
        global_corrected_motion_vectors.push(global_corrected_vector);
    }
    global_corrected_motion_vectors
}

pub fn plot_global_corrected_motion_vector(global_corrected_vector: &Vec<(f32, f32)>, width: i32, height: i32) -> Vec<Mat> {

    let mut global_corrected_vect_frames: Vec<Mat> = vec![];
    for corrected_vector in global_corrected_vector.iter() {
        let frame_res = Mat::new_rows_cols_with_default(height, width, opencv::core::CV_8UC1, Scalar::all(0.));
        if let Ok(mut frame) = frame_res {
            let intensity = 255;
            let (x2, y2) = (corrected_vector.0 as i32 * 20 + width / 2 , corrected_vector.1 as i32 * 20 + height / 2);
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

            global_corrected_vect_frames.push(frame);
        } else {
            // handle error
            panic!("Failed to create new frame for motion field");
        }
    }
    
    global_corrected_vect_frames
}