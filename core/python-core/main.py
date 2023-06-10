import os
from config.config_server import ConfigServerParameters
from uvicorn import run
import logging

if __name__ == "__main__":
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh_info = logging.FileHandler('logs/log_info.log')
    fh_info.setLevel(logging.INFO)
    fh_info.setFormatter(formatter)

    fh_error = logging.FileHandler('logs/log_error.log')
    fh_error.setLevel(logging.ERROR)
    fh_error.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  
    ch.setFormatter(formatter)

    logger.addHandler(fh_info)
    logger.addHandler(fh_error)
    logger.addHandler(ch)

    config_parameters = ConfigServerParameters()
    run("src.request_handler.controller:app", 
        host=config_parameters.server_address, 
        port=config_parameters.http_port, 
        reload=False,
        log_config= "config/config_log_uvicorn.ini")