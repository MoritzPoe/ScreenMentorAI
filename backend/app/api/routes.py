from fastapi import APIRouter, UploadFile, File
import base64

router = APIRouter()

# @router.post("/analyze-screen")
# async def analyze_screen(image: UploadFile = File(...)):
#     image_data = await image.read()
#     encoded_image = base64.b64encode(image_data).decode('utf-8')
#     base64_string = f"data:image/jpeg;base64,{encoded_image}"
#     response = await ai_processor.process_screen(base64_string)
#     return response

# @router.post("/analyze-audio")
# async def analyze_audio(audio: UploadFile = File(...)):
#     audio_data = await audio.read()
#     response = await ai_processor.process_audio(audio_data)
#     return response