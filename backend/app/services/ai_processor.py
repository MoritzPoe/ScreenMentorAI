import base64
import openai
import ssl
import urllib
from openai import AsyncOpenAI
from openai import OpenAI
#from openai.audio import LocalAudioPlayer
from pydub import AudioSegment
from pydub.playback import play
import base64
import io
from PIL import Image
import whisper
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

key = settings.OPENAI_API_KEY

client = OpenAI(api_key=key)
openai = AsyncOpenAI(api_key=key)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe", 
        file=audio_file)
    return transcription.text
    
def generate_response(image_base64, text_prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        max_output_tokens=300,
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": f"""{text_prompt} 
                        Answer briefly (1–2 sentences), only using commas and dots. If needed, mention screen areas (top left, bottom right, near icons).""" },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
    )
    return response.output_text

async def gpt_audio_responce(gpt_respnce):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=gpt_respnce,
        instructions="Speak in a calm, warm, and friendly tone, with a natural rhythm and soft intonation, like a professional storyteller or a podcast host. Avoid sharp or robotic sounds.",
        #response_format="pcm",
    ) as response:
        #await LocalAudioPlayer().play(response)
        await response.stream_to_file('gpt_output.mp3')
        # Load and play an MP3 file
        audio = AudioSegment.from_file("gpt_output.mp3", format="mp3")
        play(audio)

async def mp3_and_jpg_to_mp3(path_to_user_mp3, path_to_user_jpg):
    image = encode_image_to_base64(path_to_user_jpg)
    user_promt = transcribe_audio(path_to_user_mp3)
    model_text_responce = generate_response(image, user_promt)
    await gpt_audio_responce(model_text_responce)
    return model_text_responce

