import configparser

from src.utils import MotionEstimationMethod
from src.request_handler.data import StabilizationParameters
import cv2

class ConfigVideoParameters:
    class BlockMatchingConfig:
        def __init__(self, config):
            self.block_size = (config.getint("blockmatching", "block_size"), config.getint("blockmatching", "block_size") )
            self.search_range = config.getint("blockmatching", "search_range")

    class LKConfig:
        def __init__(self, config):
            self.win_size = ( config.getint("opticalflow", "win_size"), config.getint("opticalflow", "win_size") )
            self.max_level = config.getint("opticalflow", "max_level")
            self.criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)

    class FeatureConfig:
        def __init__(self, config):
            self.max_corners = config.getint("opticalflow", "max_corners")
            self.quality_level = config.getfloat("opticalflow", "quality_level")
            self.min_distance = config.getint("opticalflow", "min_distance")
            self.block_size = config.getint("opticalflow", "block_size_of")
            self.min_feature_threshold = config.getint("opticalflow", "min_feature_threshold")

    class OpticalFlowConfig:
        def __init__(self, config):
            self.feature_params = ConfigVideoParameters.FeatureConfig(config)
            self.lk_params = ConfigVideoParameters.LKConfig(config)

    class MotionEstimationConfig:
        def __init__(self, config):
            self.block_matching = ConfigVideoParameters.BlockMatchingConfig(config)
            self.optical_flow = ConfigVideoParameters.OpticalFlowConfig(config)
            self.motion_intensity = config.getboolean("default", "motion_intensity")
            self.motion_estimation_method = MotionEstimationMethod[config.get("default", "motion_estimation_method")]

    class StabilizationConfig:
        def __init__(self, config):
            self.motion_estimation = ConfigVideoParameters.MotionEstimationConfig(config)
            self.filter_intensity = config.getfloat("default", "filter_intensity")
            self.crop_frames = config.getboolean("default", "crop_frames")
            self.compare_filtered_result = config.getboolean("default", "compare_filtered_result")

    def __init__(self) -> None:
        config = configparser.ConfigParser()
        config.read("config/config.ini")
        self.set_default_parameters(config)

    def set_default_parameters(self, config):
        self.path_in = config.get("default", "path_in")
        self.base_path = config.get("default", "base_path")
        self.padding_percentage = config.getint("default", "padding_percentage")
        self.demo = config.getboolean("default", "demo")
        self.plot_scale_factor = config.getfloat("default", "plot_scale_factor")
        self.docker = config.getboolean("default", "docker")

        self.stabilization_parameters = self.StabilizationConfig(config)
        self.window_title = self._generate_window_title()
        self.path_out = self.generate_path_out()

    def generate_path_out(self) -> str:
        return "BS{}-SR{}-FI{}.mp4".format(self.stabilization_parameters.motion_estimation.block_matching.block_size, 
                                           self.stabilization_parameters.motion_estimation.block_matching.search_range, 
                                           self.stabilization_parameters.filter_intensity)

    def _generate_window_title(self) -> str:
        return "Block Matching Algorithm - DFD: MSE | {} | Search Range: {}".format(self.stabilization_parameters.motion_estimation.block_matching.block_size, self.stabilization_parameters.motion_estimation.block_matching.search_range)

    def set_stab_parameters(self, motion_estimation_method: str, stab_params: dict):
        if motion_estimation_method:
            self.stabilization_parameters.motion_estimation.motion_estimation_method = MotionEstimationMethod[motion_estimation_method]
        # BM
        if stab_params.get('motion_estimation', {}).get('block_matching', {}).get('block_size') is not None:
            block_size = int(stab_params['motion_estimation']['block_matching']['block_size'])
            self.stabilization_parameters.motion_estimation.block_matching.block_size = (block_size, block_size)
        if stab_params.get('motion_estimation', {}).get('block_matching', {}).get('search_range') is not None:
            self.stabilization_parameters.motion_estimation.block_matching.search_range = stab_params['motion_estimation']['block_matching']['search_range']
        # Feature
        feature_params = stab_params.get('motion_estimation', {}).get('optical_flow', {}).get('feature_params', {})
        if feature_params.get('max_corners') is not None:
            self.stabilization_parameters.motion_estimation.optical_flow.feature_params.max_corners = feature_params['max_corners']
        if feature_params.get('quality_level') is not None:
            self.stabilization_parameters.motion_estimation.optical_flow.feature_params.quality_level = feature_params['quality_level']
        if feature_params.get('min_distance') is not None:
            self.stabilization_parameters.motion_estimation.optical_flow.feature_params.min_distance = feature_params['min_distance']
        if feature_params.get('block_size') is not None:
            self.stabilization_parameters.motion_estimation.optical_flow.feature_params.block_size = feature_params['block_size']
        # LK
        lk_params = stab_params.get('motion_estimation', {}).get('optical_flow', {}).get('lk_params', {})
        if lk_params.get('win_size') is not None:
            win_size = int(lk_params['win_size'])
            self.stabilization_parameters.motion_estimation.optical_flow.lk_params.win_size = (win_size, win_size)
        if lk_params.get('max_level') is not None:
            self.stabilization_parameters.motion_estimation.optical_flow.lk_params.max_level = lk_params['max_level']
        # Filter
        if stab_params.get('filter_intensity') is not None:
            self.stabilization_parameters.filter_intensity = stab_params['filter_intensity']
        # Post proc
        if stab_params.get('crop_frames') is not None:
            self.stabilization_parameters.crop_frames = stab_params['crop_frames']
        if stab_params.get('compare_motion') is not None:
            self.stabilization_parameters.compare_filtered_result = stab_params['compare_motion']

        # Update params
        if self.demo:
            self.window_title = self._generate_window_title()
            self.path_out = self.generate_path_out()
