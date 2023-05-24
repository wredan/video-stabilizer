use kdam::tqdm;
use opencv::{
    core::{Point, Rect, Scalar, CV_8UC1},
    imgproc::{self, LINE_AA},
    prelude::{Mat, MatTraitConst},
    videoio::{self, VideoWriterTrait},
};

use crate::{utils, video::Video};

pub enum FramesPrintDebug {
    ANCHOR_P,
    GLOBAL_MOTION_VEC,
    CORRECT_VEC,
}

impl FramesPrintDebug {
    pub fn show_demo_frame(
        &self,
        video: &Video,
        a: usize,
        third_quadrant: &Option<Mat>,
        fourth_quadrant: &Option<Mat>,
        third_quadrant_title: &str,
        fourth_quadrant_title: &str,
        window_title: &str,
    ) {
        let anchor = video.frames_inp[a].clone();
        let target = video.frames_inp[a + 1].clone();

        println!(
            "Showing frame with {} and {}...",
            third_quadrant_title, fourth_quadrant_title
        );

        let out = self.visualize_single_frame(
            &anchor,
            &target,
            &third_quadrant.as_ref().unwrap(),
            third_quadrant_title,
            &fourth_quadrant.as_ref().unwrap(),
            fourth_quadrant_title,
            window_title,
            a,
        );

        utils::opencv_show_image("Demo frame", &out);

        utils::opencv_imwrite("./out/demo.png", &out);
    }

    pub fn write_video(
        &mut self,
        global_motion_vectors: &Vec<(f32, f32)>,
        video: &Video,
        third_quadrant: &Vec<Option<Mat>>,
        fourth_quadrant: &Vec<Option<Mat>>,
        third_quadrant_title: &str,
        fourth_quadrant_title: &str,
        window_title: &str,
        path: &str,
        fps: f64,
        second_override: bool,
        second_quadrant: &Vec<Mat>,
    ) {

        println!(
            "Writing video with {} and {}...",
            third_quadrant_title, fourth_quadrant_title
        );

        let mut frames_out = vec![];
        for f in tqdm!(0..video.frames_inp.len() - 1) {
            let anchor = video.frames_inp[f as usize].clone();
            let target = if second_override {
                &second_quadrant[f as usize]
            } else {
                &video.frames_inp[(f + 1) as usize]
            };            
            let out = self.visualize_single_frame(
                &anchor,
                &target,
                &third_quadrant[f as usize].as_ref().unwrap(),
                third_quadrant_title,
                &fourth_quadrant[f as usize].as_ref().unwrap(),
                &format!("{} - {:?}", fourth_quadrant_title, global_motion_vectors[f as usize]),
                window_title,
                f as usize,
            );
            frames_out.push(out);
        }

        self.write(frames_out, path, fps);
    }

    pub fn write(&mut self, frames_out: Vec<Mat>, path: &str, fps: f64) {
        let first_frame = frames_out[0].clone();
        let h = first_frame.rows() as i32;
        let w = first_frame.cols() as i32;
        let fourcc = videoio::VideoWriter::fourcc('H', '2', '6', '4').unwrap();
        //codec determined by the file extension.
        let mut writer = opencv::videoio::VideoWriter::new(
            path,
            fourcc,
            fps,
            opencv::core::Size::new(w, h),
            true,
        )
        .unwrap();
        let mut color_frame = Mat::default();
        for frame in &frames_out {
            if frame.channels() == 1 {
                imgproc::cvt_color(&frame, &mut color_frame, imgproc::COLOR_GRAY2RGB, 0).unwrap();
                writer.write(&color_frame).unwrap();
            } else {
                writer.write(&frame).unwrap();
            }
        }
        println!("[INFO] Video Export Completed");
    }

    fn visualize_single_frame(
        &self,
        anchor: &Mat,
        target: &Mat,
        third_quadrant: &Mat,
        third_quadrant_title: &str,
        fourth_quadrant: &Mat,
        fourth_quadrant_title: &str,
        title: &str,
        a: usize,
    ) -> Mat {
        let h: i32 = 70;
        let w: i32 = 10;
        let (H, W) = (anchor.rows(), anchor.cols());
        let (HH, WW) = (h + 2 * H + 20, 2 * (W + w));
        let mut frame =
            Mat::new_rows_cols_with_default(HH as i32, WW as i32, CV_8UC1, Scalar::all(255.0))
                .unwrap();

        imgproc::put_text(
            &mut frame,
            title,
            Point::new(w, 35),
            imgproc::FONT_HERSHEY_SIMPLEX,
            0.9,
            Scalar::all(0.0),
            1,
            LINE_AA,
            false,
        );

        imgproc::put_text(
            &mut frame,
            &format!("anchor-{:03}", a),
            Point::new(w, h - 6),
            imgproc::FONT_HERSHEY_SIMPLEX,
            0.7,
            Scalar::all(0.0),
            1,
            LINE_AA,
            false,
        );
        imgproc::put_text(
            &mut frame,
            &format!("target-{:03}", a + 1),
            Point::new(w + W, h - 6),
            imgproc::FONT_HERSHEY_SIMPLEX,
            0.7,
            Scalar::all(0.0),
            1,
            LINE_AA,
            false,
        );
        imgproc::put_text(
            &mut frame,
            third_quadrant_title,
            Point::new(w, h + H + 17),
            imgproc::FONT_HERSHEY_SIMPLEX,
            0.7,
            Scalar::all(0.0),
            1,
            LINE_AA,
            false,
        );
        imgproc::put_text(
            &mut frame,
            fourth_quadrant_title,
            Point::new(w + W, h + H + 17),
            imgproc::FONT_HERSHEY_SIMPLEX,
            0.7,
            Scalar::all(0.0),
            1,
            LINE_AA,
            false,
        );

        // regiorn of interest
        let roi_anchor = Rect::new(0, h as i32, W, H);
        let roi_target = Rect::new(W + w, h as i32, W, H);
        let roi_third_quadrant = Rect::new(0, (h + H + 20) as i32, W, H);
        let roi_fourth_quadrant = Rect::new(W + w, (h + H + 20) as i32, W, H);

        anchor.copy_to(&mut Mat::roi(&mut frame, roi_anchor).unwrap());
        target.copy_to(&mut Mat::roi(&mut frame, roi_target).unwrap());
        third_quadrant.copy_to(&mut Mat::roi(&mut frame, roi_third_quadrant).unwrap());
        fourth_quadrant.copy_to(&mut Mat::roi(&mut frame, roi_fourth_quadrant).unwrap());

        frame
    }
}
