use opencv::{
    highgui, imgcodecs,
};

pub fn opencv_test(img_path: &str) {
    let win_name: &str = "Test OpenCV";
    // Carica un'immagine dalla directory corrente
    let img = imgcodecs::imread(img_path, imgcodecs::IMREAD_COLOR).unwrap();

    // Crea una finestra per visualizzare l'immagine
    highgui::named_window(win_name, highgui::WINDOW_AUTOSIZE).unwrap();

    // Visualizza l'immagine nella finestra
    highgui::imshow(win_name, &img).unwrap();

    // Attendi finché l'utente non preme un tasto
    highgui::wait_key(0).unwrap();

    // Chiudi la finestra
    highgui::destroy_window(win_name).unwrap();
}