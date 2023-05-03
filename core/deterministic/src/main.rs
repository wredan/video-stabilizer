mod motion_estimation;
mod utils;
use utils::DFD;

use crate::motion_estimation::block_matching::*;

mod video;
use crate::video::*; 

use std::time::Instant;

mod opencv_test;
use crate::opencv_test::opencv_test;
use std::env;
use kdam::tqdm;
fn main() {
    env::set_var("RUST_BACKTRACE", "1");
    // OpenCV Test
    // opencv_test("./assets/lena.png");

    // Block Matching Parameters
    let dfd: DFD = DFD::MSE; // Displaced frame difference
    let block_size: (i32, i32) = (128, 128);
    let search_range: i32 = 20;
    let predict_from_prev: bool = false;
    let motion_intensity: bool = true;

    let mut bm: BlockMatching = BlockMatching::new(dfd.clone(), block_size, search_range, motion_intensity);

    // Title and Parameters Info
    let title = &format!("Block Matching Algorithm - DFD: {} | {:?} | Search Range: {}", if matches!(dfd, DFD::MSE) { "MSE" } else { "MAD" }, block_size, search_range);
    println!("{}", title);

    // Import Video Sequence
    let gray: bool = true;
    let predict: &str = if predict_from_prev { "prev" } else { "orig" };
    let path_in: String =  "assets/test_airplane_seat.MOV".to_string();
    let path_out: String = format!("./out/test_airplane_seat-{}-Size{}-{}-{}.mp4", if matches!(dfd, DFD::MSE) { "MSE" } else { "MAD" }, block_size.0, search_range, predict);

    let mut video = Video::new(path_in);
    video.read_frames(gray);

    let (h, w) = video.shape;

    let demo: bool = false;
   
    if demo {
    // Demo
        let a: usize = 72;
        let t: usize = 73;
    
        let start_time = Instant::now();
        let anchor = video.frames_inp[a].clone();
        let target = video.frames_inp[t].clone();
    
        bm.step(anchor.clone(), target.clone());
    
        let anchor_p = bm.anchor_p.unwrap().clone();
        let motion_field = bm.motion_field.unwrap().clone();
    
        let out = video.visualize(&anchor, &target, &motion_field, &anchor_p, title, a, t);
    
        let elapsed_time = start_time.elapsed().as_secs_f32();
        println!("Elapsed time: {:.3} secs", elapsed_time);
    
        utils::opencv_show_image("Demo 2 frames", &out);
    
        utils::opencv_imwrite("demo.png", &out);
    } else {
    // Video Processing
        let start_time = Instant::now();
        let N = 5;

        let mut prev_prediction = None;
        for f in tqdm!(0..video.total_frame.unwrap()-1) {

            let anchor = if predict_from_prev {
                if f % N == 0 {
                    video.frames_inp[f as usize].clone()
                } else {
                    prev_prediction.clone().unwrap()
                }
            } else {
                video.frames_inp[f as usize].clone()
            };
            let target = video.frames_inp[ (f + 1) as usize].clone();

            bm.step(anchor.clone(), target.clone());

            let anchor_p = bm.anchor_p.as_ref().unwrap();
            let motion_field = bm.motion_field.as_ref().unwrap();

            let out = video.visualize(&anchor, &target, &motion_field, &anchor_p, title, f as usize, (f+1) as usize);
            video.frames_out.push(out);

            if predict_from_prev {
                prev_prediction = Some(anchor_p.clone());
            }
        }

        let elapsed_time = start_time.elapsed();
        println!("Elapsed time: {:.3} secs", elapsed_time.as_secs_f64());
        video.write(&path_out, 30.0);
        println!("{}", path_out);
    }

}
