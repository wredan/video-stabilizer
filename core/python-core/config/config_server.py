import configparser
from enum import Enum

class DFD(Enum):
    MSE = 1
    MAD = 2

class ConfigServerParameters:
    def __init__(
        self,
    ) -> None:
        config = configparser.ConfigParser()
        config.read("config/config.ini")

        self.set_connection_parameters(config)

    def set_connection_parameters(self, config):
        self.server_address = config.get('connection', 'server_address')
        self.websocket_port = config.getint('connection', 'websocket_port')
        self.http_port = config.getint('connection', 'http_port')
        self.file_base_path = config.get('connection', 'file_base_path')
        self.connect_timeout = config.getint('connection', 'connect_timeout')
        self.read_timeout = config.getint('connection', 'read_timeout')
        self.write_timeout = config.getint('connection', 'write_timeout')