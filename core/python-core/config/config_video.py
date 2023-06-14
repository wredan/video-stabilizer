import configparser
from src.utils import MotionEstimationMethod
class ConfigVideoParameters:
    def __init__(self, **kwargs) -> None:
        config = configparser.ConfigParser()
        config.read("config/config.ini")
        self.set_default_parameters(kwargs, config)

    def set_stabilization_parameters(self, motion_estimation_method, block_size, search_range, filter_intensity, crop_frames, compare_motion):
        self.motion_estimation_method = motion_estimation_method
        self.block_size = block_size
        self.search_range = search_range
        self.filter_intensity = filter_intensity
        self.crop_frames = crop_frames
        self.compare_filtered_result = compare_motion

    def set_default_parameters(self, kwargs, config):
        default_params = self._parse_default_params(config)

        self.path_in = kwargs.get("path_in", default_params["path_in"])
        self.base_path = kwargs.get("base_path", default_params["base_path"])

        self.block_size = default_params["block_size"]
        self.motion_estimation_method = MotionEstimationMethod[default_params["motion_estimation_method"]]        
        self.search_range = default_params["search_range"]
        self.filter_intensity = default_params["filter_intensity"]
        self.crop_frames = kwargs.get("debug_mode", default_params["crop_frames"])
        self.compare_filtered_result = kwargs.get("compare_filtered_result", default_params["compare_filtered_result"])
        self.padding_percentage = kwargs.get("padding_percentage", default_params["padding_percentage"])

        self.motion_intensity = kwargs.get("motion_intensity", default_params["motion_intensity"])

        self.demo = kwargs.get("demo", default_params["demo"])
        self.plot_scale_factor = float(kwargs.get("plot_scale_factor", default_params["plot_scale_factor"]))
        self.window_title = kwargs.get("window_title", self._generate_window_title())
        self.path_out = kwargs.get("path_out", self.generate_path_out())
        self.docker = default_params["docker"]

    def _parse_default_params(self, config: configparser.ConfigParser) -> dict:
        block_size = tuple(int(size) for size in config.get("default", "block_size").split(","))
        return {
            "path_in": config.get("default", "path_in"),
            "base_path": config.get("default", "base_path"),
            "path_out": "",
            "motion_estimation_method": config.get("default", "motion_estimation_method"),
            "block_size": block_size,
            "search_range": config.getint("default", "search_range"),
            "filter_intensity": config.getfloat("default", "filter_intensity"),
            "motion_intensity": config.getboolean("default", "motion_intensity"),
            "padding_percentage": config.getint("default", "padding_percentage"),
            "demo": config.getboolean("default", "demo"),
            "plot_scale_factor": config.getfloat("default", "plot_scale_factor"),
            "compare_filtered_result": config.getboolean("default", "compare_filtered_result"),
            "crop_frames": config.getboolean("default", "crop_frames"),
            "docker": config.getboolean("default", "docker"),
        }

    def generate_path_out(self) -> str:
        return "BS{}-SR{}-FI{}.mp4".format(self.block_size[0], self.search_range, self.filter_intensity)

    def _generate_window_title(self) -> str:
        return "Block Matching Algorithm - DFD: MSE | {} | Search Range: {}".format(self.block_size, self.search_range)
