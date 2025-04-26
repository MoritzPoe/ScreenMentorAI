import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import { CameraIcon, MicrophoneIcon } from '@heroicons/react/24/solid';

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
  const [showPopup, setShowPopup] = useState(false); // State for pop-up
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

      setMessages((prev) => [...prev, newMessage]);
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

      const videoElement = document.createElement('video');
      videoElement.srcObject = stream;

      // Wait for the video to load metadata
      await new Promise((resolve) => {
        videoElement.onloadedmetadata = () => {
          videoElement.play();
          resolve(null);
        };
      });

      // Delay screenshot by 2 seconds
      setTimeout(() => {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(videoElement, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg');
        socket.emit('screen_data', imageData);

        // Stop the video stream
        stream.getTracks().forEach((track) => track.stop());
        setIsScreenSharing(false);
      }, 5000);

      // Show success pop-up
      setShowPopup(true); // Show the pop-up
      setTimeout(() => {
        setShowPopup(false); // Hide the pop-up after 3 seconds
      }, 3000); // 3000 milliseconds = 3 seconds
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
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
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
      {/* Pop-up notification */}
      {showPopup && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-4 py-2 rounded shadow-lg">
          Launch succeeded!
        </div>
      )}

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

      <div className="border-t bg-white p-6">
        <div className="flex items-center justify-center space-x-8">
          {/* Screen Capture Button */}
          <button
            onClick={isScreenSharing ? undefined : startScreenCapture}
            className={`p-4 rounded-full shadow-md transition-all duration-300
              ${isScreenSharing ? 'bg-rose-400 text-white' : 'bg-rose-100 hover:bg-rose-200 text-rose-700'}
            `}
          >
            <CameraIcon className="h-8 w-8" />
          </button>

          {/* Audio Record Button */}
          <button
            onClick={isRecording ? stopAudioRecording : startAudioRecording}
            className={`relative p-6 rounded-full shadow-md transition-all duration-500
              ${isRecording ? 'bg-emerald-400 text-white' : 'bg-emerald-100 hover:bg-emerald-200 text-emerald-700'}
            `}
          >
            <MicrophoneIcon
              className={`h-8 w-8 transform transition-transform duration-500 ${
                isRecording ? 'rotate-45 scale-110' : 'rotate-0 scale-100'
              }`}
            />
            {/* "Stop" Indicator */}
            {isRecording && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
              </div>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;