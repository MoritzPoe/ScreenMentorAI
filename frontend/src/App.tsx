import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import { CameraIcon, MicrophoneIcon, PaperAirplaneIcon } from '@heroicons/react/24/solid';

const socket = io('http://localhost:8000');

interface Message {
  type: 'user' | 'ai';
  content: string;
  audioUrl?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    socket.on('ai_response', (response) => {
      const newMessage: Message = {
        type: 'ai',
        content: response.text,
      };
      
      if (response.audio) {
        newMessage.audioUrl = `data:audio/mp3;base64,${response.audio}`;
      }
      
      setMessages(prev => [...prev, newMessage]);
    });

    return () => {
      socket.off('ai_response');
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startScreenCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      setIsScreenSharing(true);

      const track = stream.getVideoTracks()[0];
      
      // Take screenshot every 5 seconds
      const interval = setInterval(() => {
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.onloadedmetadata = () => {
          const canvas = document.createElement('canvas');
          canvas.width = videoElement.videoWidth;
          canvas.height = videoElement.videoHeight;
          const ctx = canvas.getContext('2d');
          ctx?.drawImage(videoElement, 0, 0);
          const imageData = canvas.toDataURL('image/jpeg');
          socket.emit('screen_data', imageData);
        };
      }, 5000);

      track.onended = () => {
        clearInterval(interval);
        setIsScreenSharing(false);
      };
    } catch (err) {
      console.error('Error capturing screen:', err);
      setIsScreenSharing(false);
    }
  };

  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const audioChunks: BlobPart[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const reader = new FileReader();
        reader.onload = () => {
          if (reader.result instanceof ArrayBuffer) {
            socket.emit('audio_data', reader.result);
          }
        };
        reader.readAsArrayBuffer(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error recording audio:', err);
      setIsRecording(false);
    }
  };

  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`rounded-lg p-4 max-w-[70%] ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800'
              }`}
            >
              <p>{message.content}</p>
              {message.audioUrl && (
                <audio controls className="mt-2">
                  <source src={message.audioUrl} type="audio/mp3" />
                </audio>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t bg-white p-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={isScreenSharing ? undefined : startScreenCapture}
            className={`p-2 rounded-full ${
              isScreenSharing
                ? 'bg-red-500 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            <CameraIcon className="h-6 w-6" />
          </button>
          <button
            onClick={isRecording ? stopAudioRecording : startAudioRecording}
            className={`p-2 rounded-full ${
              isRecording
                ? 'bg-red-500 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            <MicrophoneIcon className="h-6 w-6" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default App; 