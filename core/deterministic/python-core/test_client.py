import asyncio
import hashlib
import os
import websockets
import requests
import json

async def send_file():
    # Connessione al server WebSocket
    async with websockets.connect('ws://localhost:8000/ws') as websocket:
        
        # Invio del file tramite HTTP
        print(" > UPLOADING FILE")
        with open('./data/input/unstable/0.mp4', 'rb') as f:
            response = requests.put('http://localhost:8000/upload/0.mp4', files={'file': f})
        
        response_data = json.loads(response.content)
        print(f" < {response_data}")
        if response_data.get('code') == 'file_uploaded':
            filename = response_data.get('data', {}).get('filename')
            print(" > SENDING CODE: start_processing for file " + filename)
            
            # Notifica al server che il trasferimento del file è completo
            await websocket.send(cod_file_uploaded_JSON(filename))
            
            # Attesa della risposta del server
            response = await websocket.recv()
            print(f" < {response}")

            # Parse the response
            response_data = json.loads(response)
            if response_data.get('code') == 'file_processed_success':
                filename = response_data.get('data', {}).get('filename')
                if filename:
                    # Download the processed file
                    print(" > DOWNLOADING FILE: " + filename)
                    response = requests.get(f'http://localhost:8000/download/{filename}')
                    # Save the file
                    downloaded_file_path = f'./{filename}'

                    with open(f'./{filename}', 'wb') as f:
                        f.write(response.content)
                    print(f" < File {filename} downloaded successfully!")

                    print(f" > Requesting files delete") 
                    response = requests.get(f'http://localhost:8000/delete-files')
                    print(f" < {response.content}")
            else:
                print(" <", response_data)
        else:
            print(" <", response_data)

def cod_file_uploaded_JSON(filename = None):
    json_string = {
        "code": "start_processing",
        "data": {
            "filename": filename,
            "stabilization_parameters": {
                "block_size": (64, 64), 
                "search_range": 16, 
                "filter_intensity": 80, 
            }
        }
    }
    return json.dumps(json_string)

# Invio del file
asyncio.get_event_loop().run_until_complete(send_file())
