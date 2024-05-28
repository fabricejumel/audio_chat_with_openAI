from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import openai
import time
import os
import io
from typing import List, Dict
from collections import defaultdict

app = FastAPI()

os.environ["OPENAI_API_KEY"] = "Your_openai_key"  # OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_info: Dict[str, Dict] = defaultdict(dict)

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_info[client_id]['connected_at'] = time.time()

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        self.client_info.pop(client_id, None)

    async def send_text(self, text: str, websocket: WebSocket):
        await websocket.send_text(text)

    def get_active_clients(self) -> List[str]:
        return list(self.active_connections.keys())

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            try:
                data = await websocket.receive_bytes()

                # Process the audio data with OpenAI's speech recognition
                audio_file = io.BytesIO(data)
                response = openai.Audio.transcribe("whisper-1", audio_file)
                transcript = response['text']

                # Send the transcript back to the client
                await manager.send_text(transcript, websocket)

            except WebSocketDisconnect:
                manager.disconnect(client_id)
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                break
    finally:
        manager.disconnect(client_id)

@app.get("/clients")
async def get_active_clients():
    return manager.get_active_clients()

@app.get("/")
async def get():
    return FileResponse("voice_frontend.html")
