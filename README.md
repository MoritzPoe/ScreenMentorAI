# AI Screen and Audio Assistant

An AI-powered application that captures screen and audio input, processes them through OpenAI's GPT model, and provides audio responses. The application features a ChatGPT-like interface with screen sharing and audio recording capabilities.

## Features

- Real-time screen capture
- Audio recording and transcription
- Integration with OpenAI's GPT for intelligent responses
- Text-to-speech conversion for AI responses
- Modern, ChatGPT-like user interface
- WebSocket-based real-time communication

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   └── main.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
├── .env.example
└── requirements.txt
```

## Setup Instructions

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
5. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
6. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
7. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: Secret key for JWT token generation
- `FRONTEND_URL`: URL of the frontend application

## Technologies Used

- **Backend**:
  - FastAPI
  - WebSocket
  - OpenAI API
  - Whisper (for speech-to-text)
  - gTTS (for text-to-speech)

- **Frontend**:
  - React
  - TypeScript
  - Tailwind CSS
  - Socket.io-client

## License

MIT 