use crate::utils::DFD;

pub struct ConfigParameters {
    pub gray: bool,
    pub path_in: String,
    pub dfd: crate::DFD,
    pub block_size: (i32, i32),
    pub search_range: i32,
    pub filter_intensity: f32,
    pub intensity: f32,
    pub predict_from_prev: bool,
    pub motion_intensity: bool,
    pub base_path: String,
    pub path_out: String,
    pub window_title: String,
    pub demo: bool,
    pub frames_print_debug: bool,
}

impl ConfigParameters {
    pub fn new(
        gray: bool,
        path_in: String,
        dfd: crate::DFD,
        block_size: (i32, i32),
        search_range: i32,
        filter_intensity: f32,
        intensity: f32,
        predict_from_prev: bool,
        motion_intensity: bool,
        base_path: String,
        path_out: String,
        window_title: String,
        demo: bool,
        frames_print_debug: bool,
    ) -> Self {
        ConfigParameters {
            gray: gray,
            path_in: path_in,
            dfd: dfd,
            block_size: block_size,
            search_range: search_range,
            filter_intensity: filter_intensity,
            intensity: intensity,
            predict_from_prev: predict_from_prev,
            motion_intensity: motion_intensity,
            base_path: base_path,
            path_out: path_out,
            window_title: window_title,
            demo: demo,
            frames_print_debug,
        }
    }

    pub fn default() -> ConfigParameters {
        let block_size = (1024, 1024);
        let search_range = 16;
        let filter_intensity = 70.0;
        let intensity = 1.0;
        let dfd = DFD::MSE;
        let frames_print_debug_flag = true;
        Self {
            gray: true,
            path_in: "assets/test_airplane_seat.MOV".to_string(),
            dfd: DFD::MSE,
            block_size: block_size,
            search_range: search_range,
            filter_intensity: filter_intensity, 
            intensity: intensity,
            predict_from_prev: false,
            motion_intensity: true,
            base_path: "./out/test_airplane_seat".to_string(),
            path_out: format!(
                "/Bs{}-Sr{}-FI{}-I{}.mp4",
                block_size.0,
                search_range,
                filter_intensity, 
                intensity
            ),
            window_title: format!(
                "Block Matching Algorithm - DFD: {} | {:?} | Search Range: {}",
                if matches!(dfd, DFD::MSE) {
                    "MSE"
                } else {
                    "MAD"
                },
                block_size,
                search_range,
            ),
            demo: false,
            frames_print_debug: true,
        }
    }
}
