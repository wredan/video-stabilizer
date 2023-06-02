import configparser
from enum import Enum

class DFD(Enum):
    MSE = 1
    MAD = 2

class ConfigVideoParameters:
    def __init__(
        self,
        **kwargs,
    ) -> None:
        config = configparser.ConfigParser()
        config.read("config/config.ini")
        self.set_default_parameters(kwargs, config)

    def set_stabilization_parameters(self, block_size, search_range, filter_intensity, fps, crop_frames):
        self.block_size = block_size
        self.search_range = search_range
        self.filter_intensity = filter_intensity
        self.fps = fps
        self.crop_frames = crop_frames
    
    def set_default_parameters(self, kwargs, config):
        default_params = self._parse_default_params(config)
        
        self.gray = kwargs.get("gray", default_params["gray"])
        self.path_in = kwargs.get("path_in", default_params["path_in"])
        self.dfd = kwargs.get("dfd", default_params["dfd"])
        self.block_size = default_params["block_size"]
        self.search_range = default_params["search_range"]
        self.filter_intensity = default_params["filter_intensity"]
        self.fps = default_params["fps"]
        self.intensity = kwargs.get("intensity", default_params["intensity"])
        self.predict_from_prev = kwargs.get("predict_from_prev", default_params["predict_from_prev"])
        self.motion_intensity = kwargs.get("motion_intensity", default_params["motion_intensity"])
        self.base_path = kwargs.get("base_path", default_params["base_path"])
        self.path_out = kwargs.get("path_out", self._generate_path_out())
        self.plot_scale_factor = float(kwargs.get("plot_scale_factor", default_params["plot_scale_factor"]))
        self.window_title = kwargs.get("window_title", self._generate_window_title())
        self.demo = kwargs.get("demo", default_params["demo"])
        self.frames_print_debug = kwargs.get("frames_print_debug", default_params["frames_print_debug"])
        self.crop_frames = kwargs.get("frames_print_debug", default_params["crop_frames"])

        self.base_Server_path = self._generate_base_server_path(config)

    def _parse_default_params(self, config: configparser.ConfigParser) -> dict:
        block_size = tuple(
            int(size) for size in config.get("default", "block_size").split(",")
        )
        return {
            "gray": config.getboolean("default", "gray"),
            "path_in": config.get("default", "path_in"),
            "dfd": DFD[config.get("default", "dfd")],
            "block_size": block_size,
            "search_range": config.getint("default", "search_range"),
            "filter_intensity": config.getfloat("default", "filter_intensity"),
            "fps": config.getfloat("default", "fps"),
            "intensity": config.getfloat("default", "intensity"),
            "predict_from_prev": config.getboolean("default", "predict_from_prev"),
            "motion_intensity": config.getboolean("default", "motion_intensity"),
            "base_path": config.get("default", "base_path"),
            "plot_scale_factor": config.getfloat("default", "plot_scale_factor"),
            "demo": config.getboolean("default", "demo"),
            "frames_print_debug": config.getboolean("default", "frames_print_debug"),
            "crop_frames": config.getboolean("default", "crop_frames"),
        }
    
    def _generate_base_server_path(self, config) -> str:
        return "http://{}:{}/".format(
            config.get("connection", "server_address"), 
            config.get("connection", "http_port"))
    
    def _generate_path_out(self) -> str:
        return "/Bs{}-Sr{}-FI{}-I{}.mp4".format(
            self.block_size[0],
            self.search_range,
            self.filter_intensity,
            self.intensity
        )

    def _generate_window_title(self) -> str:
        dfd_str = "MSE" if self.dfd == DFD.MSE else "MAD"
        return "Block Matching Algorithm - DFD: {} | {} | Search Range: {}".format(
            dfd_str,
            self.block_size,
            self.search_range
        )