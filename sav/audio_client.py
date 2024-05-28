import asyncio
import websockets
import pyaudio

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5

# Function to record audio from the microphone
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return b''.join(frames)

# Function to send audio file to the WebSocket server
async def send_audio(uri, audio_data):
    async with websockets.connect(uri) as websocket:
        await websocket.send(audio_data)
        
        # Receive response from the server
        response = await websocket.recv()
        print(f"Received: {response}")

async def main():
    uri = "ws://127.0.0.1:8000/ws"
    audio_data = record_audio()
    await send_audio(uri, audio_data)

if __name__ == "__main__":
    asyncio.run(main())
