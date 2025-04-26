import base64
import io
from PIL import Image
import whisper
import openai
from gtts import gTTS
from ..core.config import settings
import ssl
import urllib

# Disable SSL certificate verification (only for bad Mac SSL cases)
ssl_context = ssl._create_unverified_context()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ssl_context)
)
urllib.request.install_opener(opener)

openai.api_key = settings.OPENAI_API_KEY

class AIProcessor:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
    
    async def process_screen(self, image_data: str) -> dict:
        """Process screenshot and generate response"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
            
            import uuid

            filename = f"received_screen_{uuid.uuid4().hex}.jpeg"
            image.save(filename, "JPEG")
            
            # Convert image to text description using OpenAI's Vision model
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
            
            return {
                "text": response.choices[0].message.content,
                "type": "screen"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def process_audio(self, audio_data: str) -> dict:
        """Process base64 audio and generate AI response"""
        try:
            # Step 1: Decode Base64
            decoded_audio = base64.b64decode(audio_data)
            
            # Step 2: Save to WAV file (so you can listen to it later)
            with open("received_audio.wav", "wb") as f:
                f.write(decoded_audio)

            # Step 3: Transcribe audio using Whisper
            result = self.whisper_model.transcribe("received_audio.wav")
            transcription = result["text"]
            
            # Step 4: Get AI response from OpenAI GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": transcription}
                ]
            )
            ai_response = response.choices[0].message.content
            
            # Step 5: Convert AI response to speech
            tts = gTTS(text=ai_response, lang='en')
            audio_io = io.BytesIO()
            tts.write_to_fp(audio_io)
            tts_audio_base64 = base64.b64encode(audio_io.getvalue()).decode('utf-8')

            return {
                "text": ai_response,
                "audio": tts_audio_base64,
                "type": "audio"
            }
        except Exception as e:
            return {"error": str(e)}

ai_processor = AIProcessor() 