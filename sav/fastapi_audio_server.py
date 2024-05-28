from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import openai
import time
import os
import io

app = FastAPI()

os.environ["OPENAI_API_KEY"] = "Your_openai_key"  # OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, text: str, websocket: WebSocket):
        await websocket.send_text(text)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
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
                manager.disconnect(websocket)
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                break
    finally:
        manager.disconnect(websocket)

@app.get("/")
async def get():
    return FileResponse("voice_frontend.html")
