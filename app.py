from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import openai
import base64
from PIL import Image
import io
import whisper
from gtts import gTTS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Whisper
whisper_model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('screen_data')
def handle_screen_data(image_data):
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Process with OpenAI Vision
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What do you see in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                            }
                        }
                    ]
                }
            ]
        )
        
        text_response = response.choices[0].message.content
        
        # Convert response to speech
        tts = gTTS(text=text_response, lang='en')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_data = base64.b64encode(audio_io.getvalue()).decode('utf-8')
        
        emit('ai_response', {
            'text': text_response,
            'audio': audio_data,
            'type': 'screen'
        })
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('audio_data')
def handle_audio_data(audio_data):
    try:
        # Save audio data temporarily
        audio_bytes = base64.b64decode(audio_data)
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        
        # Transcribe audio using Whisper
        result = whisper_model.transcribe("temp_audio.wav")
        transcription = result["text"]
        
        # Get AI response using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": transcription}
            ]
        )
        
        ai_response = response.choices[0].message.content
        
        # Convert response to speech
        tts = gTTS(text=ai_response, lang='en')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_data = base64.b64encode(audio_io.getvalue()).decode('utf-8')
        
        emit('ai_response', {
            'text': ai_response,
            'audio': audio_data,
            'type': 'audio'
        })
        
        # Clean up temporary file
        os.remove("temp_audio.wav")
        
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True) 