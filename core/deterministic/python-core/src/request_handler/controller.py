import asyncio
from fastapi import FastAPI, Request, WebSocket, UploadFile, File, WebSocketDisconnect
import src.request_handler.request_handler as RequestHandler
from .json_encoder import cod_error_file_processing_JSON
from starlette.websockets import WebSocketState

app = FastAPI()

# Gestione del trasferimento del file HTTP
@app.put("/upload/{filename}")
async def upload_file(request: Request, filename: str, file: UploadFile = File(...)):
   return await RequestHandler.upload_file_handler(request=request, filename=filename, file=file)


@app.get("/download/{filename}")
async def download_file(request: Request, filename: str):
   return RequestHandler.download_file_handler(request, filename)

@app.get("/delete-files")
async def download_file(request: Request):
   return RequestHandler.delete_downloaded_file(request)

# Gestione della connessione WebSocket
active_connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)   
    try:
        await RequestHandler.websocket_handler(websocket)
    finally:
        active_connections.remove(websocket) 
    
