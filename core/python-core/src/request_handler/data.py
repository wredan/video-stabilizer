from dataclasses import dataclass
from typing import Optional

@dataclass
class BlockMatchingParams:
    block_size: Optional[int] = None
    search_range: Optional[int] = None

@dataclass
class LKParams:
    win_size: Optional[int] = None
    max_level: Optional[int] = None

@dataclass
class FeatureParams:
    max_corners: Optional[int] = None
    quality_level: Optional[float] = None
    min_distance: Optional[int] = None
    block_size: Optional[int] = None

@dataclass
class OpticalFlowParams:
    feature_params: FeatureParams
    lk_params: LKParams

@dataclass
class MotionEstimationParams:
    block_matching: BlockMatchingParams
    optical_flow: OpticalFlowParams

@dataclass
class StabilizationParameters:
    motion_estimation: MotionEstimationParams
    filter_intensity: Optional[int] = None
    crop_frames: Optional[bool] = None
    compare_motion: Optional[bool] = None

@dataclass
class Data:
    stabilization_parameters: StabilizationParameters
    filename: Optional[str] = None
    motion_estimation_method: Optional[str] = None

@dataclass
class IncomingData:
    data: Data
    state: Optional[str] = None
