mod motion_estimation;
mod utils;
use motion_estimation::motion_estimation::MotionEstimation;
use utils::DFD;

mod video;
use crate::video::*; 

mod opencv_test;
use crate::opencv_test::opencv_test;

use std::env;
fn main() {
    env::set_var("RUST_BACKTRACE", "1");
    // OpenCV Test
    // opencv_test("./assets/lena.png");

    // Import Video Sequence
    let gray: bool = true;
    let path_in: String =  "assets/test_airplane_seat.MOV".to_string();

    let mut video = Video::new(path_in);
    video.read_frames(gray);

    let demo: bool = true;
    let mut motion_estimation = MotionEstimation::new(&mut video);
   
    if demo {
        motion_estimation.demo(72, 73);
    } else {
        motion_estimation.video_processing();
    }

}
