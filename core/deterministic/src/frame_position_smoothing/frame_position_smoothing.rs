use kdam::tqdm;
use opencv::{
    core::{
        dft, idft, mul_spectrums, DftFlags, Matx23f, Rect, Scalar, Size, Vec2f, CV_32F, CV_32FC1,
        CV_32FC2,
    },
    imgproc::warp_affine,
    prelude::{Mat, MatTrait, MatTraitConst, MatTraitConstManual},
};

pub fn forward_dft(global_motion_vector: &Mat) -> Mat {
    // Calcola la trasformata di Fourier
    let mut data = Mat::new_rows_cols_with_default(1, 2, CV_32FC2, Scalar::all(0.0)).unwrap();
    dft(
        global_motion_vector,
        &mut data,
        DftFlags::DFT_COMPLEX_OUTPUT as i32,
        0,
    );
    data
}

// funzione per calcolare il filtro gaussiano, più è grande sigma, più frequenze passano
fn gaussian_low_pass(sigma: f32, rows: i32, cols: i32) -> Mat {
    let mut filter =
        Mat::new_rows_cols_with_default(rows, cols, CV_32FC2, Scalar::new(0.0, 0.0, 0.0, 0.0))
            .unwrap();
    let mut total: f32 = 0.0;
    let d = 2.0 * sigma * sigma;

    let center_x = cols / 2;
    let center_y = rows / 2;

    for y in 0..rows {
        for x in 0..cols {
            let dx = (x - center_x) as f32;
            let dy = (y - center_y) as f32;
            let value = (-(dx * dx + dy * dy) / d).exp();
            *filter.at_2d_mut::<Vec2f>(y, x).unwrap() = Vec2f::from([value, 0.0]);
            total += value;
        }
    }

    // normalize filter so it sums to 1
    for y in 0..rows {
        for x in 0..cols {
            let value = filter.at_2d::<Vec2f>(y, x).unwrap()[0] / total;
            *filter.at_2d_mut::<Vec2f>(y, x).unwrap() = Vec2f::from([value, 0.0]);
        }
    }

    filter
}

// funzione per applicare il filtro gaussiano
pub fn low_pass_filter(data: &Mat, sigma: f32) -> Mat {
    let filter = gaussian_low_pass(sigma, data.rows(), data.cols());
    let mut filtered_data = Mat::default();
    mul_spectrums(data, &filter, &mut filtered_data, 0, false).unwrap();
    filtered_data
}

pub fn inverse_dft(filtered_data: &Mat) -> Mat {
    let mut inverse_filtered = Mat::new_rows_cols_with_default(
        filtered_data.rows(),
        filtered_data.cols(),
        CV_32FC1,
        Scalar::all(0.0),
    )
    .unwrap();
    idft(
        filtered_data,
        &mut inverse_filtered,
        DftFlags::DFT_REAL_OUTPUT as i32,
        0,
    );
    inverse_filtered
}

pub fn correction_vector(
    global_motion_vector: &(f32, f32),
    inverse_filtered_data: &Mat,
) -> (f32, f32) {
    let (delta_x, delta_y) = global_motion_vector;
    let estimated_delta_x = inverse_filtered_data.at::<f32>(0).unwrap();
    let estimated_delta_y = inverse_filtered_data.at::<f32>(1).unwrap();

    (estimated_delta_x - delta_x, estimated_delta_y - delta_y)
}

pub fn global_correction_motion_vectors(
    global_motion_vectors: &Vec<(f32, f32)>,
    sigma: f32,
) -> Vec<(f32, f32)> {
    let mut global_corrected_motion_vectors: Vec<(f32, f32)> = vec![];
    let mut accumulated_motion: Vec<(f32, f32)> = vec![];

    println!("Global Correction Vector Calculating...");

    for (i, global_motion_vector) in tqdm!(global_motion_vectors.iter().enumerate()) {
        accumulated_motion.push(if i == 0 {
            *global_motion_vector
        } else {
            (
                accumulated_motion[i - 1].0 + global_motion_vector.0,
                accumulated_motion[i - 1].1 + global_motion_vector.1,
            )
        });
        println!("\nITERAZIONE: {}", i);
        let data = Mat::from_slice(&[accumulated_motion[i].0, accumulated_motion[i].1])
            .unwrap()
            .reshape(1, 1)
            .unwrap();
        let mut data_float = Mat::default();
        data.convert_to(&mut data_float, CV_32FC1, 1.0, 0.0)
            .unwrap();
        println!(
            "global_float: ({}, {})",
            data_float.at::<f32>(0).unwrap(),
            data_float.at::<f32>(1).unwrap()
        );

        let fourier_transform = forward_dft(&data_float);
        println!(
            "fourier_transform: ({}, {}) - ({}, {})",
            fourier_transform.at_2d::<Vec2f>(0, 0).unwrap()[0],
            fourier_transform.at_2d::<Vec2f>(0, 0).unwrap()[1],
            fourier_transform.at_2d::<Vec2f>(0, 1).unwrap()[0],
            fourier_transform.at_2d::<Vec2f>(0, 1).unwrap()[1]
        );

        let filtered_data = low_pass_filter(&fourier_transform, sigma);
        println!(
            "filtered_data: ({}, {}) - ({}, {})",
            filtered_data.at_2d::<Vec2f>(0, 0).unwrap()[0],
            filtered_data.at_2d::<Vec2f>(0, 0).unwrap()[1],
            filtered_data.at_2d::<Vec2f>(0, 1).unwrap()[0],
            filtered_data.at_2d::<Vec2f>(0, 1).unwrap()[1]
        );

        let inverse_filtered_data = inverse_dft(&filtered_data);

        let correction_vector = correction_vector(&accumulated_motion[i], &inverse_filtered_data);
        println!(
            "inverse_filtered_data: ({}, {})",
            inverse_filtered_data.at::<f32>(0).unwrap(),
            inverse_filtered_data.at::<f32>(1).unwrap()
        );
        println!("correction_vector: {:?}", correction_vector);

        global_corrected_motion_vectors.push(correction_vector);
    }

    global_corrected_motion_vectors
}

pub fn print_mat(mat: &Mat) -> opencv::Result<()> {
    for i in 0..2 {
        // Nota: si assume che la matrice sia di tipo CV_32FC2 per i numeri complessi.
        // Se la tua matrice è di un tipo diverso, potrebbe essere necessario modificare il tipo di dati qui.
        let value = mat.at_2d::<Vec2f>(0, i).unwrap();
        println!("({}, {}): {:?}", 0, i, value);
    }

    Ok(())
}

pub fn shift_frames(
    frames: &Vec<Mat>,
    global_correct_motion_vectors: &Vec<(f32, f32)>,
    intensity: f32,
) -> Vec<Mat> {
    let mut shifted_frames: Vec<Mat> = vec![];
    for (frame, correction_vector) in frames.iter().zip(global_correct_motion_vectors.iter()) {
        let shifted_frame: Result<Mat, opencv::Error> = shift_frame(
            &frame,
            correction_vector.0 * intensity,
            correction_vector.1 * intensity,
        );
        shifted_frames.push(shifted_frame.unwrap());
    }
    shifted_frames
}

fn shift_frame(frame: &Mat, shift_x: f32, shift_y: f32) -> Result<Mat, opencv::Error> {
    let mut shifted_frame =
        Mat::new_rows_cols_with_default(frame.rows(), frame.cols(), frame.typ(), Scalar::all(0.0))?;

    let translation_matrix_data: [f32; 6] = [1.0, 0.0, shift_x, 0.0, 1.0, shift_y];
    let translation_matrix = Mat::from_slice(&translation_matrix_data)?.reshape(1, 2)?;

    let shifted_frame_size = shifted_frame.size().unwrap();

    warp_affine(
        &frame,
        &mut shifted_frame,
        &translation_matrix,
        shifted_frame_size,
        1,
        0,
        Scalar::all(0.0),
    )?;

    Ok(shifted_frame)
}

// pub fn crop_frames(frames: &Vec<Mat>, global_correct_motion_vectors: &Vec<(f32, f32)>) -> Result<Vec<Mat>, opencv::Error> {
//     let (max_shift_x, max_shift_y) = global_correct_motion_vectors.iter().fold((0.0, 0.0), |acc, &vec| {
//         (f32::max(acc.0, vec.0.abs()), f32::max(acc.1, vec.1.abs()))
//     });

//     let cropped_frames: Result<Vec<Mat>, opencv::Error> = frames.iter().map(|frame| {
//         let roi = Rect::new(
//             max_shift_x as i32,
//             max_shift_y as i32,
//             frame.cols() - 2 * max_shift_x as i32,
//             frame.rows() - 2 * max_shift_y as i32,
//         );

//         if roi.x >= 0 && roi.y >= 0 && roi.x + roi.width <= frame.cols() && roi.y + roi.height <= frame.rows() {
//             let mask = Mat::new_rows_cols(roi.height, roi.width, CV_8UC1);
//             mask.set_to(Scalar::all(255))?;
//             let mut cropped_frame = Mat::new_rows_cols(roi.height, roi.width, frame.typ())?;
//             frame.copy_to_with_mask(&mut cropped_frame, &mask, &roi)?;
//             Ok(cropped_frame)
//         } else {
//             // Gestisci l'errore (ad esempio, restituisci un'immagine vuota o un errore)
//             Err(opencv::Error::new(-1, "Invalid ROI dimensions".to_string()))
//         }
//     }).collect();

//     cropped_frames
// }
