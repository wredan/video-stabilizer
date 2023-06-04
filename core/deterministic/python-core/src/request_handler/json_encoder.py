import json

def cod_file_uploaded_JSON(filename = None):
    data = {
        "code": "file_uploaded",
        "data": {
            "message": "File uploaded successfully! Use http://.../donwload/{filename}.mp4 to request the compouted file when it's done.".format(filename),
            "filename": filename + ".mp4"
        }
    }
    json_string = json.dumps(data)
    return json_string

def cod_error_uploading_file_JSON(error = None):
    data = {
        "code": "error_uploading_file",
        "data": {
            "message": "Error while uploading or saving the file, try again please.",
            "error": error
        }
    }
    json_string = json.dumps(data)
    return json_string

def cod_JSON(code, complete_elab_value = None, file_path = None, filename = None):
    data = {
        "code": code,
        "data": {
            "complete_elab_value": complete_elab_value,
            "file_path": file_path,
            "filename": filename
        }
    }
    json_string = json.dumps(data)
    return json_string

def decod_JSON(json_string):
    data = json.loads(json_string)
    code = data["code"]
    complete_elab_value = data["data"]["complete_elab_value"]
    file_path = data["data"]["file_path"]
    filename = data["data"]["filename"]
    return code, complete_elab_value, file_path, filename
