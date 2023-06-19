export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  webSocketUrl: 'ws://localhost:8000/ws',
  defaultFormValues: {
    // Default form values
    motionEstimationMethod: 'BLOCK_MATCHING',
    ofMotionType: '0',
    blockSize: '64',
    searchRange: 16,
    filterIntensity: 40,
    cropFrames: false,
    compareMotion: false,
  },
  opticalFlowParams: {
    0: {
      // Optical flow for slow and detailed movements
      feature_params: {
        max_corners: 1000,
        quality_level: 0.01,
        min_distance: 10,
        block_size: 7,
      },
      lk_params: {
        win_size: 25,
        max_level: 3,
      },
    },
    1: {
      // Optical flow for fast movements
      feature_params: {
        max_corners: 500,
        quality_level: 0.1,
        min_distance: 20,
        block_size: 7,
      },
      lk_params: {
        win_size: 15,
        max_level: 3,
      },
    },
  },
};
