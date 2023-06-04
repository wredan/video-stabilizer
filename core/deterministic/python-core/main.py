from config.config_server import ConfigServerParameters
from uvicorn import run

if __name__ == "__main__":
    config_parameters = ConfigServerParameters()
    run("src.request_handler.controller:app", host=config_parameters.server_address, port=config_parameters.http_port, reload=False)