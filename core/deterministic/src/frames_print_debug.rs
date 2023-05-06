use kdam::tqdm;
use opencv::{prelude::{Mat, MatTraitConst}, videoio::{self, VideoWriterTrait}, imgproc::{self, LINE_AA}, core::{Point, Scalar, CV_8UC1, Rect}};

use crate::{video::Video, utils};

pub enum TypeVisualize {
    ANCHOR_P,
    GLOBAL_MOTION_VEC,
    CORRECT_VEC
}

pub struct FramesPrintDebug {
    pub motion_field_vec: Option<Vec<Mat>>,
    pub global_motion_vec: Option<Vec<Mat>>,
    pub global_correct_motion_vec: Option<Vec<Mat>>,
    pub anchor_p_vec: Option<Vec<Mat>>,
    pub frames_out: Option<Vec<Mat>>
}

impl FramesPrintDebug {

    pub fn new() -> 
        Self {
            FramesPrintDebug { 
                motion_field_vec: Some(vec![]),
                global_motion_vec: Some(vec![]),
                global_correct_motion_vec: Some(vec![]),
                anchor_p_vec: Some(vec![]),
                frames_out: Some(vec![]),
            }
    }

    pub fn show_demo_frame(&self, type_visualize: TypeVisualize, video: &Video, a: usize, t: usize, window_title: &str) {

        let anchor = video.frames_inp[a].clone();
        let target = video.frames_inp[t].clone();

        let mut third_quadrant: &Mat;
        let mut fourth_quadrant: &Mat;
        let mut third_quadrant_title: &str;
        let mut fourth_quadrant_title: &str;

        self.select_from_enum_for_demo(type_visualize, a,  &mut third_quadrant, &mut fourth_quadrant, third_quadrant_title, fourth_quadrant_title);

        println!("Showing frame with {} and {}...", third_quadrant_title, fourth_quadrant_title);

        let out = self.visualize_single_frame(
            &anchor,
            &target,
            &third_quadrant,
            third_quadrant_title,
            &fourth_quadrant,
            fourth_quadrant_title,
            window_title,
            a,
            t,
        );

        utils::opencv_show_image("Demo frame", &out);

        utils::opencv_imwrite("./out/demo.png", &out);
    }

    fn select_from_enum_for_demo(&self, type_visualize: TypeVisualize, a: usize, mut third_quadrant: &mut Mat, mut fourth_quadrant: &mut Mat, mut third_quadrant_title: &str, mut fourth_quadrant_title: &str) {
        match type_visualize {
            TypeVisualize::ANCHOR_P => {
                third_quadrant = &mut self.motion_field_vec.unwrap()[a];
                fourth_quadrant = &mut self.anchor_p_vec.unwrap()[a];
                third_quadrant_title = "motion field";
                fourth_quadrant_title = "anchor_p";
            }
            TypeVisualize::GLOBAL_MOTION_VEC => {
                third_quadrant = &mut self.motion_field_vec.unwrap()[a];
                fourth_quadrant = &mut self.global_motion_vec.unwrap()[a];
                third_quadrant_title = "motion field";
                fourth_quadrant_title = "global motion vector";
            },
            TypeVisualize::CORRECT_VEC => {
                third_quadrant = &mut self.global_motion_vec.unwrap()[a];
                fourth_quadrant = &mut self.global_correct_motion_vec.unwrap()[a];
                third_quadrant_title = "global motion vector";
                fourth_quadrant_title = "global correct motion vector";
            },
        }
    }

    pub fn write_video(&self, type_visualize: TypeVisualize, video: &Video, window_title: &str, path: &str, fps: f64) {

        let mut third_quadrant: &Vec<Mat>;
        let mut fourth_quadrant: &Vec<Mat>;
        let mut third_quadrant_title: &str;
        let mut fourth_quadrant_title: &str;

        self.select_from_enum_for_write(type_visualize, &mut third_quadrant, &mut fourth_quadrant, third_quadrant_title, fourth_quadrant_title);

        println!("Writing video with {} and {}...", third_quadrant_title, fourth_quadrant_title);

        let mut frames_out = vec![];
        for f in tqdm!(0..video.total_frame.unwrap() - 1) {
            let anchor = video.frames_inp[f as usize].clone();
            let target = video.frames_inp[(f + 1) as usize].clone();
            let out = self.visualize_single_frame(
                &anchor,
                &target,
                &third_quadrant[f as usize],
                third_quadrant_title,
                &fourth_quadrant[f as usize],
                fourth_quadrant_title,
                window_title,
                f as usize,
                (f + 1) as usize,
            );
            frames_out.push(out);
        }

        self.write(frames_out, path, fps);
    }

    fn select_from_enum_for_write(&self, type_visualize: TypeVisualize, mut third_quadrant: &mut Vec<Mat>, mut fourth_quadrant: &mut Vec<Mat>, mut third_quadrant_title: &str, mut fourth_quadrant_title: &str) {
        match type_visualize {
            TypeVisualize::ANCHOR_P => {
                third_quadrant = &mut self.motion_field_vec.unwrap();
                fourth_quadrant = &mut self.anchor_p_vec.unwrap();
                third_quadrant_title = "motion field";
                fourth_quadrant_title = "anchor_p";
            }
            TypeVisualize::GLOBAL_MOTION_VEC => {
                third_quadrant = &mut self.motion_field_vec.unwrap();
                fourth_quadrant = &mut self.global_motion_vec.unwrap();
                third_quadrant_title = "motion field";
                fourth_quadrant_title = "global motion vector";
            },
            TypeVisualize::CORRECT_VEC => {
                third_quadrant = &mut self.global_motion_vec.unwrap();
                fourth_quadrant = &mut self.global_correct_motion_vec.unwrap();
                third_quadrant_title = "global motion vector";
                fourth_quadrant_title = "global correct motion vector";
            },
        }
    }

    fn write(&mut self, frames_out: Vec<Mat>, path: &str, fps: f64) {
        let first_frame = frames_out[0];
        let h = first_frame.rows() as i32;
        let w = first_frame.cols() as i32;
        let fourcc = videoio::VideoWriter::fourcc('H', '2', '6', '4').unwrap();
         //codec determined by the file extension.
        let mut writer = opencv::videoio::VideoWriter::new(path, fourcc, fps, opencv::core::Size::new(w, h), true).unwrap();
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

    fn visualize_single_frame(&self, anchor: &Mat, target: &Mat, third_quadrant: &Mat, third_quadrant_title: &str, fourth_quadrant: &Mat, fourth_quadrant_title: &str, title: &str, a: usize, t: usize) -> Mat {
        let h: i32 = 70;
        let w: i32 = 10;
        let (H, W) = (anchor.rows(), anchor.cols());
        let (HH, WW) = (h + 2 * H + 20, 2 * (W + w));
        let mut frame = Mat::new_rows_cols_with_default(HH as i32, WW as i32, CV_8UC1, Scalar::all(255.0)).unwrap();
    
        imgproc::put_text(&mut frame, title, Point::new(w, 35), imgproc::FONT_HERSHEY_SIMPLEX, 0.9, Scalar::all(0.0), 1, LINE_AA, false);
    
        imgproc::put_text(&mut frame, &format!("anchor-{:03}", a), Point::new(w, h - 6), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
        imgproc::put_text(&mut frame, &format!("target-{:03}", t), Point::new(w + W, h - 6), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
        imgproc::put_text(&mut frame, third_quadrant_title, Point::new(w, h + H + 17), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
        imgproc::put_text(&mut frame, fourth_quadrant_title, Point::new(w + W, h + H + 17), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
    
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