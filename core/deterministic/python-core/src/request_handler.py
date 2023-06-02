import asyncio
import websockets
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from src.video_processing import VideoProcessing
from config.config_video import ConfigVideoParameters
import json

# Gestione del trasferimento del file HTTP
class FileHandler(SimpleHTTPRequestHandler):
    def do_PUT(self):
        length = int(self.headers['Content-Length'])
        path = "data/files/input" + self.path
        with open(path, 'wb') as f:
            f.write(self.rfile.read(length))
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Qui puoi gestire le richieste GET.
        # Ad esempio, potresti voler restituire un file specifico:
        self.send_response(200, message=self.path)
        # Invia gli headers
        self.send_header('Content-type', 'test/plain')
        self.end_headers()

# Gestione della connessione WebSocket
async def websocket_handler(websocket, path):
    async for message in websocket:
        # Decodifica il messaggio JSON
        data = json.loads(message)
        print("MESSAGE: ", data)
        if 'code' in data and data['code'] == 'file_transfer_complete':
            print("File ricevuto, inizio elaborazione...")
            # Qui dovresti elaborare il file e caricare il file elaborato
            filename = data.get('filename', '')
            print(f"Filename: {filename}")
            path = process_video(filename)
            await websocket.send('file_processed: download at ' + path)


def start_websocket(config_parameters):
    # Avvio del server WebSocket
    print("Websocket running...")
    try:
        start_server = websockets.serve(websocket_handler, config_parameters.server_address, config_parameters.websocket_port)
        asyncio.get_event_loop().run_until_complete(start_server)
    except KeyboardInterrupt:
        asyncio.get_event_loop().stop()

def start_file_handler(config_parameters):
    # Avvio del server HTTP
    httpd = TCPServer((config_parameters.server_address, config_parameters.http_port), FileHandler)
    print("Server http running...")
    try:
        asyncio.get_event_loop().run_in_executor(None, httpd.serve_forever)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        httpd.server_close()
        asyncio.get_event_loop().stop()

def process_video(video_name, stabilization_parameters = None):
    config_parameters = ConfigVideoParameters()
    if stabilization_parameters is not None:
        config_parameters.set_stabilization_parameters(block_size= stabilization_parameters["block_size"], 
                                                       search_range= stabilization_parameters["search_range"], 
                                                       filter_intensity= stabilization_parameters["filter_intensity"], 
                                                       crop_frames= stabilization_parameters["crop_frames"])
    video_processing = VideoProcessing(video_path= config_parameters.path_in + "/" + video_name, 
                                       config_parameters=config_parameters)
    path = video_processing.run()
    return config_parameters.base_Server_path + path
