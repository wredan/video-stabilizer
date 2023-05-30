use opencv::{
    core::*,
    highgui,
    imgcodecs::{self, imwrite},
    prelude::Mat,
};

#[derive(Clone)]
pub enum DFD {
    MSE,
    MAD,
}

impl DFD {
    pub fn mad(&mut self, img1: &Mat, img2: &Mat) -> f64 {
        let mut diff = Mat::default();
        absdiff(&img1, &img2, &mut diff);
        *mean(&diff, &no_array()).unwrap().get(0).unwrap()
    }

    pub fn mse(&mut self, img1: &Mat, img2: &Mat) -> f64 {
        let mut diff = Mat::default();
        absdiff(&img1, &img2, &mut diff);
        let mut diff_squared = Mat::default();
        pow(&diff, 2.0, &mut diff_squared);
        *mean(&diff_squared, &no_array()).unwrap().get(0).unwrap()
    }

}

pub fn opencv_show_image(win_name: &str, img: &Mat) {
    // Crea una finestra per visualizzare l'immagine
    highgui::named_window(win_name, highgui::WINDOW_AUTOSIZE).unwrap();

    // Visualizza l'immagine nella finestra
    highgui::imshow(win_name, img).unwrap();

    // Attendi finché l'utente non preme un tasto
    highgui::wait_key(0).unwrap();

    // Chiudi la finestra
    highgui::destroy_window(win_name).unwrap();
}

pub fn opencv_imwrite(filename: &str, img: &Mat) {
    let mut params = Vector::new();
    params.push(imgcodecs::IMWRITE_PNG_COMPRESSION);
    params.push(9); // highest compression

    imwrite(filename, img, &params).unwrap();
}
