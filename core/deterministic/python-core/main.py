import src.request_handler as RequestHandler
from config.config_server import ConfigServerParameters

if __name__ == "__main__":
   config_parameters = ConfigServerParameters()
   RequestHandler.start_websocket(config_parameters)
   RequestHandler.start_file_handler(config_parameters)

