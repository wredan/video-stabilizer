pub struct Block {
    pub coord: (i32, i32, i32, i32),
    pub center: (i32, i32),
    pub mv: (i32, i32),
    pub mv_amp: f64,
}

impl Block {
    pub fn new(x: i32, y: i32, w: i32, h: i32) -> Block {
        Block {
            coord: (x, y, w, h),
            center: (x + w / 2, y + h / 2),
            mv: (0, 0),
            mv_amp: 0.0,
        }
    }

    pub fn check_inside_frame(&self, x: i32, y: i32, min: &(i32, i32, i32, i32), max: &(i32, i32, i32, i32)) -> bool {
        x >= min.0 && x <= max.0 && y >= min.1 && y <= max.1
    }

    pub fn calculate_mv_amp(&mut self, max_amp: &mut f64, min: &(i32, i32, i32, i32), max: &(i32, i32, i32, i32)) {
        let amp = ((self.mv.0.pow(2) + self.mv.1.pow(2)) as f64).sqrt();
        if amp > *max_amp {
            *max_amp = amp;
        }
        self.mv_amp = amp;
        if self.check_inside_frame(self.center.0, self.center.1, min, max) && self.mv_amp > *max_amp {
            *max_amp = self.mv_amp;
        }
    }
}
