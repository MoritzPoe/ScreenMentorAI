from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from .core.config import settings
from .api.routes import router
import socketio

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
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[settings.FRONTEND_URL])
socket_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def screen_data(sid, data):
    # Handle incoming screen data
    response = await process_screen_data(data)
    await sio.emit('ai_response', response, room=sid)

@sio.event
async def audio_data(sid, data):
    # Handle incoming audio data
    response = await process_audio_data(data)
    await sio.emit('ai_response', response, room=sid)

# Mount the Socket.IO application
app.mount("/", socket_app) 