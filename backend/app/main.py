from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from .core.config import settings
from .api.routes import router
import socketio
from .services.ai_processor import ai_processor

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
async def screen_data(sid, data):
    # Handle incoming screen data    
    print(f"Received screen_data from {sid}")
    response = await ai_processor.process_screen(data)
    await sio.emit('ai_response', response, room=sid)

@sio.event
async def audio_data(sid, data):
    # Handle incoming audio data
    print(f"Received audio_data from {sid}")
    response = await ai_processor.process_audio(data)
    await sio.emit('ai_response', response, room=sid)

# Mount the Socket.IO application
app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

