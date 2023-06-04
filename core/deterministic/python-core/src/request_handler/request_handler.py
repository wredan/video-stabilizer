import hashlib
import os
import re
import uuid
from fastapi import WebSocket, UploadFile, Request
from fastapi.responses import FileResponse, JSONResponse
from starlette.websockets import WebSocketState
from src.video_processing import VideoProcessing
from config.config_video import ConfigVideoParameters
from .json_encoder import cod_error_file_processing_JSON, cod_error_filename_JSON, cod_file_processed_JSON, cod_file_uploaded_JSON, cod_error_uploading_file_JSON
from .utils import get_file_extension
import json
import shutil

# region

async def upload_file_handler(request: Request, filename: str, file: UploadFile):
    try:
        extension = get_file_extension(filename)
    except ValueError as e:
        print(str(e))
        return cod_error_uploading_file_JSON(e)
    
    client_address = create_out_dir_from_client_address(request)
    unique_name, input_path = create_in_dir_from_client_address(extension, client_address)

    with open(input_path, 'wb') as f:
        f.write(await file.read())
    print(" > Uploaded video saved at: " + input_path)
    response = cod_file_uploaded_JSON(filename=unique_name + "." + extension)
    print(" < ", response)
    return response

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

def download_file_handler(request: Request, filename: str):
    try:
        print(" < SENDING FILE: " + filename)
        output_path = os.path.join("data", "files", "output", hashlib.sha256(request.client.host.encode()).hexdigest(), filename)
        print(" < SENDING FILE: " + output_path)
        return FileResponse(path=output_path, filename=filename, media_type="multipart/form-data")
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"code" : "file_not_found", "error": "File not found"})
    
def delete_downloaded_file(request: Request):
    try:
        client_dir = hashlib.sha256(request.client.host.encode()).hexdigest()
        output_path = os.path.join("data", "files", "output", client_dir)
        input_path = os.path.join("data", "files", "input", client_dir)
        shutil.rmtree(output_path, ignore_errors=True)
        shutil.rmtree(input_path, ignore_errors=True)
        print(" < Deleted dir: " + client_dir)
        return JSONResponse(status_code=200, content={"code" : "client_dir_deleted"})
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"code" : "file_not_found", "error": "File not found"})

# endregion

async def websocket_handler(websocket: WebSocket):
    try:
        data = await websocket.receive_text()
        data = json.loads(data)

        if 'code' in data and data['code'] == 'start_processing':
            print("Got File, start processing...")
            filename = data.get('data', {}).get('filename')
            print(f"Filename: {filename}")
            if(is_valid_filename(filename)):    
                client_dir = hashlib.sha256(websocket.client.host.encode()).hexdigest()
                proc_file_name = process_video(filename, client_dir, data)
                response = cod_file_processed_JSON(proc_file_name)
                print(" < ", response)
                await websocket.send_json(response)
            else:
                response = cod_error_filename_JSON(filename)
                print(" < ", response)
                await websocket.send_json(response)
                await websocket.close()
    except Exception as e:
        print("------------------- ERROR --------------------")
        print(e)
        if websocket.application_state != WebSocketState.DISCONNECTED:
            response = cod_error_file_processing_JSON()
            await websocket.send_json(response)
            await websocket.close()

def check_filename(filename: str):
    filename.split('.')


def is_valid_filename(filename):
    pattern = r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\.(avi|mp4|MOV)$'
    return re.match(pattern, filename) is not None

def process_video(video_name: str, client_dir: str, data = None):
    config_parameters = ConfigVideoParameters()
    if data is not None:
        block_size, search_range, filter_intensity, crop_frames = get_stabilization_parameters(data, config_parameters)
        config_parameters.set_stabilization_parameters(block_size= block_size, 
                                                       search_range= search_range, 
                                                       filter_intensity= filter_intensity, 
                                                       crop_frames= crop_frames)
        if config_parameters.debug_mode:
            config_parameters.path_out = config_parameters.generate_path_out()

    video_processing = VideoProcessing(video_name= video_name,
                                       client_dir=client_dir,
                                       config_parameters=config_parameters)
    file_name = video_processing.run()
    return file_name

def get_stabilization_parameters(data, config_parameters: ConfigVideoParameters):
    stabilization_parameters = data.get('data', {}).get('stabilization_parameters', {})
    block_size = stabilization_parameters.get('block_size', config_parameters.block_size)
    search_range = stabilization_parameters.get('search_range', config_parameters.search_range)
    filter_intensity = stabilization_parameters.get('filter_intensity', config_parameters.filter_intensity)
    crop_frames = stabilization_parameters.get('crop_frames', config_parameters.crop_frames)

    return block_size, search_range, filter_intensity, crop_frames

