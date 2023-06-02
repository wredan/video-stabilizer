
import asyncio
import websockets
import requests

async def send_file():
    # Connessione al server WebSocket
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Invio del file tramite HTTP
        with open('./data/input/unstable/0.mp4', 'rb') as f:
            requests.put('http://localhost:8000/0.mp4', data=f)
        # Notifica al server che il trasferimento del file è completo
        await websocket.send('{"code": "file_transfer_complete", "filename": "0.mp4"}')
        # Attesa della risposta del server
        response = await websocket.recv()
        print(f"< {response}")

# Invio del file
asyncio.get_event_loop().run_until_complete(send_file())
