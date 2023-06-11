# Video Stabilizer
A video stabilizer using Three Step Search, Frame Position Smoothing and Cropping.


![Demo](docs/demo.gif)

## Features

- **Three Step Search**: Efficiently searches for the best matching block in a reference frame to stabilize the motion.
- **Frame Position Smoothing**: Smoothens irregular movements in video frames for a more stabilized output.
- **Gaussian Filtering with Static Padding**: Reduces edge effects on the motion signal through Gaussian filtering and static padding, ensuring smoother transitions at the beginning and end of the video.
- **Cropping**: Adjusts the frame size to ensure that the stabilized video does not have any blank borders due to the movement adjustment.

## Installation

Clone the repository and navigate to the root project folder, then run:

```bash
$ docker-compose up -d
```

This command will build the Docker containers and start the services in the background.

To shut it down, run:

```bash
$ docker-compose down
```

## Usage

Once the containers are up and running, visit http://localhost:4200 in your web browser. Here, you can choose and customize the parameters to optimally stabilize your video.

**Note**: The performance of stabilization may vary depending on the video. Experiment with different parameters for optimal results.

## About

This Video Stabilizer is designed to mitigate the shakiness and unintended movements in videos, making them smoother and more visually appealing. It utilizes a Three Step Search algorithm for motion estimation, Frame Position Smoothing to remove irregularities in motion, and Cropping to ensure the video frames are consistently sized. Additionally, Gaussian Filtering with Static Padding is employed to reduce edge effects on the motion signal, ensuring smoother transitions at the beginning and end of the video.

