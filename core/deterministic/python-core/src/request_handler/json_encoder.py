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

def cod_error_uploading_file_JSON(error = None):
    json_string = {
        "code": "error_uploading_file",
        "data": {
            "message": "Error while uploading or saving the file, try again please.",
            "error": error
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
#endregion
