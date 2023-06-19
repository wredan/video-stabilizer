
import hashlib
import os
import re
import uuid

from src.request_handler.data import IncomingData
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
