pub struct ConfigParameters {
    pub gray: bool,
    pub path_in: String,
    pub dfd: crate::DFD,
    pub block_size: (i32, i32),
    pub search_range: i32,
    pub predict_from_prev: bool,
    pub motion_intensity: bool,
    pub path_out: String,
    pub window_title: String,
    pub frames_print_debug: bool
}

impl ConfigParameters {
    pub fn new(
        gray: bool,
        path_in: String,
        dfd: crate::DFD,
        block_size: (i32, i32),
        search_range: i32,
        predict_from_prev: bool,
        motion_intensity: bool,
        path_out: String,
        window_title: String,
        frames_print_debug: bool
    ) -> 
        Self {
            ConfigParameters { 
                gray: gray,
                path_in: path_in,
                dfd: dfd,
                block_size: block_size,
                search_range: search_range,
                predict_from_prev: predict_from_prev,
                motion_intensity: motion_intensity,
                path_out: path_out,
                window_title: window_title,
                frames_print_debug
            }
    }
}

