class JsonEncoder:
    STATE_FILE_UPLOADED = "file_uploaded"
    STATE_ERROR_UPLOADING_FILE = "error_uploading_file"
    STATE_ERROR_FILE = "error_file"
    STATE_ERROR_FILENAME = "error_filename"
    STATE_FILE_PROCESSED = "file_processed_success"
    STATE_ERROR_FILE_PROCESSING = "file_error_processing"
    STATE_INIT_READING_FRAMES = "init_reading_frames"
    STATE_INIT_MOTION_ESTIMATION = "init_motion_estimation"
    STATE_INIT_FRAME_POSITION_SMOOTHING = "init_frame_position_smoothing"
    STATE_INIT_FRAMES_SHIFT = "init_frames_shift"
    STATE_INIT_FRAMES_CROPPING = "init_frames_cropping"
    STATE_INIT_VIDEO_WRITING = "init_video_writing"
    STATE_UPDATE_STEP = "update_step"

    @staticmethod
    def generate_json(state, message, **kwargs):
        json_string = {
            "state": state,
            "data": {
                "message": message,
                **kwargs
            }
        }
        return json_string

    @classmethod
    def file_uploaded_JSON(cls, filename=None):
        message = "File uploaded successfully! Use http://.../download/{} to request the processed file when it's done.".format(filename)
        return cls.generate_json(cls.STATE_FILE_UPLOADED, message, filename=filename)

    @classmethod
    def error_uploading_file_JSON(cls, error=""):
        message = "Error while uploading or saving the file, try again please."
        return cls.generate_json(cls.STATE_ERROR_UPLOADING_FILE, message, error=error)

    @classmethod
    def error_file_JSON(cls, filename):
        message = "File {} is not recognized. Provide a valid file please (avi|mp4|MOV).".format(filename)
        return cls.generate_json(cls.STATE_ERROR_FILE, message)

    @classmethod
    def error_filename_JSON(cls, filename):
        message = "Filename {} is not recognized. Provide a valid filename please. Valid: video_uuid.(avi|mp4|MOV).".format(filename)
        return cls.generate_json(cls.STATE_ERROR_FILENAME, message)

    @classmethod
    def file_processed_JSON(cls, filename):
        message = "Filename {} has been processed successfully.".format(filename)
        return cls.generate_json(cls.STATE_FILE_PROCESSED, message, filename=filename)

    @classmethod
    def error_file_processing_JSON(cls):
        message = "Internal Error: error during file processing"
        return cls.generate_json(cls.STATE_ERROR_FILE_PROCESSING, message)

    @classmethod
    def init_reading_frames(cls, message):
        return cls.generate_json(cls.STATE_INIT_READING_FRAMES, message)

    @classmethod
    def init_motion_estimation_json(cls, message):
        return cls.generate_json(cls.STATE_INIT_MOTION_ESTIMATION, message)

    @classmethod
    def init_frame_position_smoothing_json(cls, message):
        return cls.generate_json(cls.STATE_INIT_FRAME_POSITION_SMOOTHING, message)

    @classmethod
    def init_frames_shift_json(cls, message):
        return cls.generate_json(cls.STATE_INIT_FRAMES_SHIFT, message)

    @classmethod
    def init_frames_cropping_json(cls, message):
        return cls.generate_json(cls.STATE_INIT_FRAMES_CROPPING, message)

    @classmethod
    def init_video_writing_json(cls, message):
        return cls.generate_json(cls.STATE_INIT_VIDEO_WRITING, message)

    @classmethod
    def update_step_json(cls, id, step, total):
        return cls.generate_json(cls.STATE_UPDATE_STEP + "_" + id, message="", step=str(step), total=str(total))
