import json

#region HTTP
def cod_file_uploaded_JSON(filename = None):
    json_string = {
        "code": "file_uploaded",
        "data": {
            "message": "File uploaded successfully! Use http://.../download/{} to request the processed file when it's done.".format(filename),
            "filename": filename
        }
    }
    return json_string

def cod_error_uploading_file_JSON(error = ""):
    json_string = {
        "code": "error_uploading_file",
        "data": {
            "message": "Error while uploading or saving the file, try again please.",
            "error": error
        }
    }
    return json_string

def cod_error_file_JSON(filename):
    json_string = {
        "code": "error_file",
        "data": {
            "message": "File {} is not recognized. Provide a valid file please (avi|mp4|MOV).".format(filename),
        }
    }
    return json_string

#endregion

#region websocket

def cod_error_filename_JSON(filename):
    json_string = {
        "code": "error_filename",
        "data": {
            "message": "Filename {} is not recognized. Provide a valid filename please. Valid: video_uuid.(avi|mp4|MOV).".format(filename),
        }
    }
    return json_string

def cod_file_processed_JSON(filename):
    json_string = {
        "code": "file_processed_success",
        "data": {
            "message": "Filename {} has been processed successfully.".format(filename),
            "filename": filename
        }
    }
    return json_string

def cod_error_file_processing_JSON():
    json_string = {
        "code": "file_error_processing",
        "data": {
            "message": "Internal Error: error during file processing",
        }
    }
    return json_string

# STEPS

def init_reading_frames(message):
    json_string = {
        "code": "init_reading_frames",
        "data": {
            "message": message,
        }
    }
    return json_string

def init_motion_estimation_json(message):
    json_string = {
        "code": "init_motion_estimation",
        "data": {
            "message": message,
        }
    }
    return json_string

def init_frame_position_smoothing_json(message):
    json_string = {
        "code": "init_frame_position_smoothing",
        "data": {
            "message": message,
        }
    }
    return json_string

def init_frames_shift_json(message):
    json_string = {
        "code": "init_frames_shift",
        "data": {
            "message": message,
        }
    }
    return json_string

def init_frames_cropping_json(message):
    json_string = {
        "code": "init_frames_cropping",
        "data": {
            "message": message,
        }
    }
    return json_string

def init_video_writing_json(message):
    json_string = {
        "code": "init_video_writing",
        "data": {
            "message": message,
        }
    }
    return json_string

def update_step_json(step, total):
    json_string = {
        "code": "update_step",
        "data": {
            "step": str(step),
            "total": str(total)
        }
    }
    return json_string
#endregion
