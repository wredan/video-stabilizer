use kdam::tqdm;
use opencv::{
    core::{Scalar, Point, Rect, CV_8UC1},
    imgproc::{self, LINE_AA},
    prelude::*,
    videoio,
};

pub struct Video<'a> {
    path: &'a str,
    pub frames_inp: Vec<Mat>,
    pub frames_out: Vec<Mat>,
    pub shape: (i32, i32), // H,W
    gray: bool,
}

impl<'a> Video<'a> {
    pub fn new(path: &'a str) -> Self {
        Self {
            path: path,
            frames_inp: vec![],
            frames_out: vec![],
            shape: (0, 0),
            gray: false,
        }
    }

    pub fn read_frames(&mut self, gray: bool) {
        /*
         * stores all the frames in the given video source in
         * self.frames_inp (list) as [frame0, frame1, ...]
         * where frame# is Mat
         */
        let mut source: videoio::VideoCapture = match videoio::VideoCapture::from_file(&self.path, videoio::CAP_ANY) {
            Ok(source) => source,
            Err(_) => {
                panic!("Error in Path");
            }
        };

        let total_frame = source.get(videoio::CAP_PROP_FRAME_COUNT)
            .unwrap_or_else(|e| panic!("Error getting total frame count: {:?}", e)) as i32;        

        let mut frame: Mat = Mat::default();
        println!("[INFO] Reading frames...");
        for _ in tqdm!(0..total_frame) {
            let ret: Result<bool, opencv::Error> = source.read(&mut frame);
            if !ret.unwrap_or(false) {
                println!("Error in Frame Read");
                break;
            }
            if gray {
                self.gray = true;
                imgproc::cvt_color(&frame.clone(), &mut frame, imgproc::COLOR_BGR2GRAY, 0).unwrap();
            }
            if self.shape.0 == 0 {
                self.shape = (frame.size().unwrap().height, frame.size().unwrap().width);
            }

            self.frames_inp.push(frame.clone());
        }

        println!("[INFO] Video Import Completed");
    }


    pub fn visualize(&self, anchor: &Mat, target: &Mat, motion_field: &Mat, anchor_p: &Mat, title: &str, a: usize, t: usize) -> Mat {
        let h: i32 = 70;
        let w: i32 = 10;
        let (H, W) = (anchor.rows(), anchor.cols());
        let (HH, WW) = (h + 2 * H + 20, 2 * (W + w));
        let mut frame = Mat::new_rows_cols_with_default(HH as i32, WW as i32, CV_8UC1, Scalar::all(255.0)).unwrap();
    
        imgproc::put_text(&mut frame, title, Point::new(w, 35), imgproc::FONT_HERSHEY_SIMPLEX, 0.9, Scalar::all(0.0), 1, LINE_AA, false);
    
        imgproc::put_text(&mut frame, &format!("anchor-{:03}", a), Point::new(w, h - 6), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
        imgproc::put_text(&mut frame, &format!("target-{:03}", t), Point::new(w + W, h - 6), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
        imgproc::put_text(&mut frame, "motion field", Point::new(w, h + H + 17), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
        imgproc::put_text(&mut frame, "predicted anchor", Point::new(w + W, h + H + 17), imgproc::FONT_HERSHEY_SIMPLEX, 0.7, Scalar::all(0.0), 1, LINE_AA, false);
    
        // regiorn of interest
        let roi_anchor = Rect::new(0, h as i32, W, H);
        let roi_target = Rect::new(W + w, h as i32, W, H);
        let roi_motion = Rect::new(0, (h + H + 20) as i32, W, H);
        let roi_anchor_p = Rect::new(W + w, (h + H + 20) as i32, W, H);
        
        anchor.copy_to(&mut Mat::roi(&mut frame, roi_anchor).unwrap());
        target.copy_to(&mut Mat::roi(&mut frame, roi_target).unwrap());
        motion_field.copy_to(&mut Mat::roi(&mut frame, roi_motion).unwrap());
        anchor_p.copy_to(&mut Mat::roi(&mut frame, roi_anchor_p).unwrap());
    
        frame
    }
    
    pub fn write(&mut self, path: &str, fps: f64) {
        let first_frame = &self.frames_out[0];
        let h = first_frame.rows() as i32;
        let w = first_frame.cols() as i32;
        let fourcc = videoio::VideoWriter::fourcc('H', '2', '6', '4').unwrap();
         //codec determined by the file extension.
        let mut writer = opencv::videoio::VideoWriter::new(path, fourcc, fps, opencv::core::Size::new(w, h), true).unwrap();
        let mut color_frame = Mat::default();
        for frame in &self.frames_out {
            if frame.channels() == 1 {
                imgproc::cvt_color(&frame, &mut color_frame, imgproc::COLOR_GRAY2RGB, 0).unwrap();
                writer.write(&color_frame).unwrap();
            } else {
                writer.write(&frame).unwrap();
            }
        }
        println!("[INFO] Video Export Completed");
    }

}
