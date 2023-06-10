import hashlib
import os
from starlette.websockets import WebSocketState
from fastapi import WebSocket, UploadFile, Request, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from src.video_processing import VideoProcessing
from src.request_handler.json_encoder import JsonEncoder
from config.config_video import ConfigVideoParameters
from .utils import create_in_dir_from_client_address, create_out_dir_from_client_address, get_file_ext, get_stabilization_parameters, is_valid_file, is_valid_filename
import json
import shutil
import traceback
import logging

# region

async def upload_file_handler(request: Request, filename: str, file: UploadFile):
    logger = logging.getLogger('logger')

    if not is_valid_file(filename):   
        return JSONResponse(status_code=400, content=JsonEncoder.error_file_JSON(filename))
    
    try:
        ext = get_file_ext(filename)
    except ValueError as e:
        logger.error("Error: " + str(e))
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=400, content=JsonEncoder.error_uploading_file_JSON(str(e))) 
    
    client_address = create_out_dir_from_client_address(request)
    unique_name, input_path = create_in_dir_from_client_address(get_file_ext(filename), client_address)

    try:
        with open(input_path, 'wb') as f:
            f.write(await file.read())
    except Exception as e:
        logger.error("Error: " + str(e))
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content=JsonEncoder.error_uploading_file_JSON())
    logger.info("Uploaded video saved at: " + input_path)
    response = JSONResponse(status_code=200, content=JsonEncoder.file_uploaded_JSON(filename=unique_name + "." + ext))
    return response

def download_file_handler(request: Request, filename: str):
    logger = logging.getLogger('logger')
    try:
        output_path = os.path.join("data", "files", "output", hashlib.sha256(request.client.host.encode()).hexdigest(), filename)
        logger.info("Sending file: " + output_path)
        return FileResponse(path=output_path, filename=filename, media_type="multipart/form-data")
    except FileNotFoundError as e:
        logger.error("Error: " + str(e))
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=404, content={"code" : "file_not_found", "error": "File not found"})
    
def delete_downloaded_file(request: Request):
    logger = logging.getLogger('logger')
    try:
        client_dir = hashlib.sha256(request.client.host.encode()).hexdigest()
        delete_client_dir(client_dir)
        logger.info("Deleted dir: " + client_dir)
        return JSONResponse(status_code=200, content={"code" : "client_dir_deleted"})
    except FileNotFoundError as e:
        logger.error("Error: " + str(e))
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=404, content={"code" : "file_not_found", "error": "File not found"})

def delete_client_dir(client_dir):    
    output_path = os.path.join("data", "files", "output", client_dir)
    input_path = os.path.join("data", "files", "input", client_dir)
    shutil.rmtree(output_path, ignore_errors=True)
    shutil.rmtree(input_path, ignore_errors=True)

# endregion

async def websocket_handler(websocket: WebSocket):
    try:
        logger = logging.getLogger('logger')
        client_dir=None
        data = await websocket.receive_text()
        data = json.loads(data)
        if 'state' in data and data['state'] == 'start_processing':
            logger.info("Got file, start processing...")
            filename = data.get('data', {}).get('filename')
            if(is_valid_filename(filename)):    
                client_dir = hashlib.sha256(websocket.client.host.encode()).hexdigest()
                proc_file_name = await process_video(filename, client_dir, data, websocket)
                response = JsonEncoder.file_processed_JSON(proc_file_name)
                await websocket.send_json(response)
            else:
                response = JsonEncoder.error_filename_JSON(filename)
                logger.info("Filename not valid")
                await websocket.send_json(response)
                await websocket.close()
    except (WebSocketDisconnect, Exception) as e:
        logger.error("Error: " + str(e))
        if client_dir: delete_client_dir(client_dir)
        logger.error(traceback.format_exc())
        logger.info("Client disconnected during video processing.")

async def process_video(video_name: str, client_dir: str, data = None, websocket: WebSocket = None):
    config_parameters = ConfigVideoParameters()
    if data is not None:
        block_size, search_range, filter_intensity, crop_frames, compare_motion = get_stabilization_parameters(data, config_parameters)
        config_parameters.set_stabilization_parameters(block_size= block_size, 
                                                       search_range= search_range, 
                                                       filter_intensity= filter_intensity, 
                                                       crop_frames= crop_frames,
                                                       compare_motion= compare_motion)
        if config_parameters.demo:
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

