import hashlib
import os
import re
import uuid
from fastapi import WebSocket, UploadFile, Request, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from starlette.websockets import WebSocketState
from src.video_processing import VideoProcessing
from config.config_video import ConfigVideoParameters
from .json_encoder import cod_error_file_JSON, cod_error_file_processing_JSON, cod_error_filename_JSON, cod_error_uploading_file_JSON, cod_file_processed_JSON, cod_file_uploaded_JSON
from .utils import create_in_dir_from_client_address, create_out_dir_from_client_address, get_file_ext, get_stabilization_parameters, is_valid_file, is_valid_filename
import json
import shutil

# region

async def upload_file_handler(request: Request, filename: str, file: UploadFile):
    
    if not is_valid_file(filename):   
        return JSONResponse(status_code=400, content=cod_error_file_JSON(filename))
    
    try:
        ext = get_file_ext(filename)
    except ValueError as e:
        print(str(e))
        return JSONResponse(status_code=400, content=cod_error_uploading_file_JSON(str(e))) 
    
    client_address = create_out_dir_from_client_address(request)
    unique_name, input_path = create_in_dir_from_client_address(get_file_ext(filename), client_address)

    try:
        with open(input_path, 'wb') as f:
            f.write(await file.read())
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content=cod_error_uploading_file_JSON())
    print(" > Uploaded video saved at: " + input_path)
    response = JSONResponse(status_code=200, content=cod_file_uploaded_JSON(filename=unique_name + "." + ext))
    print(" < ", response.body)
    return response

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
        delete_client_dir(client_dir)
        print(" < Deleted dir: " + client_dir)
        return JSONResponse(status_code=200, content={"code" : "client_dir_deleted"})
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"code" : "file_not_found", "error": "File not found"})

def delete_client_dir(client_dir):    
    output_path = os.path.join("data", "files", "output", client_dir)
    input_path = os.path.join("data", "files", "input", client_dir)
    shutil.rmtree(output_path, ignore_errors=True)
    shutil.rmtree(input_path, ignore_errors=True)

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
                proc_file_name = await process_video(filename, client_dir, data, websocket)
                response = cod_file_processed_JSON(proc_file_name)
                print(" < ", response)
                await websocket.send_json(response)
            else:
                response = cod_error_filename_JSON(filename)
                print(" < ", response)
                await websocket.send_json(response)
                await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected during video processing.")
        delete_client_dir(client_dir)
    # except Exception as e:
    #     print("------------------- ERROR --------------------")
    #     print(e)
    #     delete_client_dir(client_dir)

async def process_video(video_name: str, client_dir: str, data = None, websocket: WebSocket = None):
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
                                       config_parameters=config_parameters,
                                       websocket= websocket)
    
    try:
        file_name = await video_processing.run()
    except WebSocketDisconnect:
       raise
    return file_name

