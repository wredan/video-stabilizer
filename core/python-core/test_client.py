import asyncio
import hashlib
import os
import websockets
import requests
import json

async def send_file():
        
        # Sending file video over HTTP
        print(" > UPLOADING FILE")
        with open('./data/input/unstable/0.mp4', 'rb') as f:
            response = requests.post('http://localhost:8000/upload/0.mp4', files={'file': f})
        
        response_data = json.loads(response.content)
        print(f" < {response_data}")

        # Connecting to the WebSocket
        if response_data.get('state') == 'file_uploaded':
            async with websockets.connect('ws://localhost:8000/ws') as websocket:
                filename = response_data.get('data', {}).get('filename')
                print(" > SENDING CODE: start_processing for file " + filename)
                
                # Sending start_processing for file to the server
                await websocket.send(file_uploaded_JSON(filename))
                
                # Waiting for server start_processing message
                response = await websocket.recv()
                print(f" < {response}")
                code = ""

                # Getting server updates for long run task
                while True:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    code = response_data.get('state')
                    if code == "file_processed_success":
                        break
                    elif code == "update_step":
                        print(" < " + str(response_data.get('data', {}).get('step')) + "/" + str(response_data.get('data', {}).get('total')))
                        await websocket.send("")
                    else:
                        print(f" < {response}")
                
                # File processed, request download
                filename = response_data.get('data', {}).get('filename')
                if filename:                    
                    print(" > DOWNLOADING FILE: " + filename)
                    response = requests.get(f'http://localhost:8000/download/{filename}')
                    
                    # Save the file
                    with open(f'./{filename}', 'wb') as f:
                        f.write(response.content)
                    print(f" < File {filename} downloaded successfully!")

                    # Requesting to delete processed file
                    # print(f" > Requesting files delete") 
                    # response = requests.get(f'http://localhost:8000/delete-files')
                    # print(f" < {response.content}")
                else:
                    print(" <", response_data)
        else:
            print(" <", response_data)

def file_uploaded_JSON(filename = None):
    json_string = {
        "state": "start_processing",
        "data": {
            "filename": filename,
            "stabilization_parameters": {
                "motion_estimation_method": 0,
                "block_size": 64, 
                "search_range": 16, 
                "filter_intensity": 80, 
                "crop_frames": False,
                "compare_motion": False
            }
        }
    }
    return json.dumps(json_string)

# Invio del file
asyncio.get_event_loop().run_until_complete(send_file())
