
import hashlib
import os
import re
import uuid
from config.config_video import ConfigVideoParameters
from fastapi import Request
from src.utils import MotionEstimationMethod

def get_file_ext(path):
    name_parts = path.split("/")[-1].split(".")

    if len(name_parts) == 2:
        return name_parts[1]
    
    raise ValueError("Invalid filename: no extension or incorrect one")

def create_in_dir_from_client_address(extension, client_address):
    unique_name = str(uuid.uuid4())
    path = os.path.join("data", "files", "input", client_address, unique_name + "." + extension)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return unique_name,path

def create_out_dir_from_client_address(request: Request):
    client_address = hashlib.sha256(request.client.host.encode()).hexdigest()
    output_dir_path = os.path.join("data", "files", "output", client_address)
    os.makedirs(output_dir_path, exist_ok=True)
    return client_address

def is_valid_file(filename):
    pattern = r'^(avi|mp4|MOV)$'
    return re.match(pattern, filename.split('.')[-1]) is not None

def is_valid_filename(filename):
    pattern = r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\.(avi|mp4|MOV)$'
    return re.match(pattern, filename) is not None

def get_stabilization_parameters(data, config_parameters: ConfigVideoParameters):
    data = data.get("data", {})
    stabilization_parameters = data.get('stabilization_parameters', {})
    motion_estimation_method = MotionEstimationMethod[stabilization_parameters.get('motion_estimation_method', config_parameters.motion_estimation_method)]
    print(motion_estimation_method)
    block_size = int(stabilization_parameters.get('block_size', config_parameters.block_size))
    search_range = int(stabilization_parameters.get('search_range', config_parameters.search_range))
    filter_intensity = int(stabilization_parameters.get('filter_intensity', config_parameters.filter_intensity))
    crop_frames = bool(stabilization_parameters.get('crop_frames', config_parameters.crop_frames))
    compare_motion = bool(stabilization_parameters.get('compare_motion', config_parameters.crop_frames))

    return motion_estimation_method, (block_size, block_size) , search_range, filter_intensity, crop_frames, compare_motion
