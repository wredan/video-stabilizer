import asyncio
import os
import uuid
import websockets
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from src.video_processing import VideoProcessing
from config.config_video import ConfigVideoParameters
from .json_encoder import cod_file_uploaded_JSON, cod_error_uploading_file_JSON
from .utils import get_file_extension
import json

# Gestione del trasferimento del file HTTP
class FileHandler(SimpleHTTPRequestHandler):
    def do_PUT(self):
        if self.path.startswith('/upload/'):
            length = int(self.headers['Content-Length'])
            try:
                extension = get_file_extension(self.path)
                print("Extension:", extension)
            except ValueError as e:
                print(str(e))
                self.send_response(400, message=cod_error_uploading_file_JSON(e))
                # Invia gli headers
                self.send_header('Content-type', 'application/json')
                self.end_headers()

            output_path = "data/files/output/" + self.client_address[0]
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            unique_name = str(uuid.uuid4())
            path = "data/files/input/" + self.client_address[0] + "/" + unique_name
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(self.rfile.read(length))
            self.send_response(200, message=cod_file_uploaded_JSON(filename=unique_name))
            self.end_headers()
        else:
            # Qui puoi gestire altre richieste GET.
            # Ad esempio, potresti voler restituire un file specifico:
            self.send_response(200, message=self.path)
            # Invia gli headers
            self.send_header('Content-type', 'application/json')
            self.end_headers()

    def do_GET(self):
        if self.path.startswith('/download/'):
            # Ottieni il percorso del file richiesto
            requested_file = self.path[len('/download/'):]

            try:
                # Apri il file in modalità lettura binaria
                with open(requested_file, 'rb') as file:
                    # Leggi il contenuto del file
                    file_content = file.read()

                # Imposta gli headers per la risposta HTTP
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', 'attachment; filename="{}"'.format(requested_file))
                self.send_header('Content-Length', str(len(file_content)))
                self.end_headers()

                # Invia il contenuto del file come corpo della risposta
                self.wfile.write(file_content)

            except FileNotFoundError:
                # Se il file richiesto non esiste, restituisci un errore 404
                self.send_response(404)
                self.end_headers()

        else:
            # Qui puoi gestire altre richieste GET.
            # Ad esempio, potresti voler restituire un file specifico:
            self.send_response(200, message=self.path)
            # Invia gli headers
            self.send_header('Content-type', 'text/plain')
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
