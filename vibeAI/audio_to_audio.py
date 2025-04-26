import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
import openai
import base64
from openai import OpenAI
import time


key= ''
client = OpenAI(api_key=key)
openai = AsyncOpenAI(api_key=key)


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
       transcription = client.audio.transcriptions.create(
    model="gpt-4o-mini-transcribe", 
    file=audio_file
)
    return transcription.text

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

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


def make_respoce(audio_path, image_path):
    start_time = time.time()

    text = transcribe_audio(audio_path)

    image_base64 = encode_image_to_base64(image_path)

    gpt_response = generate_response(image_base64, text)
    end_time = time.time()
    print(f"Time to geterante responce: {end_time - start_time:.4f} secounds")
    print(f"{gpt_response}")
    return gpt_response

async def main(audio_file_path, image_file_path, audio_output_path):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=make_respoce(audio_file_path, image_file_path),
        instructions="Speak in a calm, warm, and friendly tone, with a natural rhythm and soft intonation, like a professional storyteller or a podcast host. Avoid sharp or robotic sounds.",
        # response_format="pcm",
    ) as response:
        # await LocalAudioPlayer().play(response)
        await response.stream_to_file(audio_output_path)


# if __name__ == "__main__":
#     asyncio.run(main())