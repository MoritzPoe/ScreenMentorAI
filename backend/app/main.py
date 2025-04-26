from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.routes import router
import socketio
from .services.ai_processor import mp3_and_jpg_to_mp3
import base64

from pydub import AudioSegment
import os

app = FastAPI(title="AI Screen and Audio Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

# Socket.IO setup
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[settings.FRONTEND_URL]
)


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def process_data(sid, data):
    print(f"Received combined audio and screen data from {sid}")

    try:
        # Step 1: Unpack the payload
        base64_audio = data['audio']
        base64_image = data['image']

        # Step 2: Decode and save audio (WAV format first)
        audio_bytes = base64.b64decode(base64_audio)
        audio_webm_path = f"temp_audio_{sid}.webm"
        with open(audio_webm_path, "wb") as f:
            f.write(audio_bytes)

        # Step 3: Convert WAV to MP3
        audio_mp3_path = f"temp_audio_{sid}.mp3"
        convert_webm_to_mp3(audio_webm_path, audio_mp3_path)
        print(f"Converted Webm to MP3: {audio_mp3_path}")

        # Step 4: Decode and save image
        image_bytes = base64.b64decode(base64_image.split(',')[1])
        image_path = f"temp_image_{sid}.jpg"
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        # Step 5: Call your unified AI pipeline with MP3 path
        model_text_response = await mp3_and_jpg_to_mp3(audio_mp3_path, image_path)

        # Step 6: Send AI text response back to frontend
        await sio.emit('ai_response', {
            "text": model_text_response,
            "type": "combined"
        }, room=sid)

    except Exception as e:
        print("Error in process_data:", e)
        await sio.emit('ai_response', {
            "error": str(e),
            "type": "error"
        }, room=sid)

def convert_webm_to_mp3(input_webm_path, output_mp3_path):
    import subprocess
    subprocess.run([
        "ffmpeg", "-i", input_webm_path, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_mp3_path
    ], check=True)

# Mount the Socket.IO application
app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

