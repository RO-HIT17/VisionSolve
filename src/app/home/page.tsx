'use client'
import React, { useState, useRef, useEffect } from 'react';

import { FaPaperPlane, FaFileUpload, FaRobot, FaUser, FaSpinner, FaPlayCircle } from 'react-icons/fa';

interface Message {
  sender: 'user' | 'bot';
  type: 'text' | 'file' | 'video';
  content: string | File | null;
  videoUrl?: string;
}

const ChatbotUI: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [botResponseVideoUrl, setBotResponseVideoUrl] = useState<string | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async () => {
    if (inputText.trim()) {
      const newMessage: Message = { sender: 'user', type: 'text', content: inputText.trim() };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInputText('');
      setIsBotTyping(true);
      setBotResponseVideoUrl(null); 
      setTimeout(async () => {
        const mockVideoUrl = 'https://www.w3schools.com/html/mov_bbb.mp4'; 
        const botReply: Message = { sender: 'bot', type: 'video', content: null, videoUrl: mockVideoUrl };
        setMessages((prevMessages) => [...prevMessages, botReply]);
        setIsBotTyping(false);
      }, 1500);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleFileUpload = async () => {
    if (selectedFile) {
      const newMessage: Message = { sender: 'user', type: 'file', content: selectedFile };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setSelectedFile(null);
      setIsBotTyping(true);
      setBotResponseVideoUrl(null);
      setTimeout(async () => {
        const mockVideoUrl = 'https://www.w3schools.com/html/mov_bbb.mp4'; 
        const botReply: Message = { sender: 'bot', type: 'video', content: null, videoUrl: mockVideoUrl };
        setMessages((prevMessages) => [...prevMessages, botReply]);
        setIsBotTyping(false);
      }, 3000);
    } else {
      alert('Please select a file to upload.');
    }
  };

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 py-10 px-6 sm:px-10 flex flex-col items-center">
      <div className="bg-white shadow-xl rounded-lg overflow-hidden max-w-2xl w-full">
        <div className="bg-indigo-500 text-white py-4 px-6 flex items-center justify-between">
          <div className="flex items-center">
            <FaRobot className="text-xl mr-3" />
            <h2 className="text-lg font-semibold">Math Solution Bot</h2>
          </div>
          <span className="text-sm opacity-75">Online</span>
        </div>
        <div className="p-4 h-[500px] overflow-y-auto flex flex-col space-y-3 scroll-smooth" id="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} items-start`}>
              {msg.sender === 'bot' && <FaRobot className="text-xl text-indigo-500 mr-3 mt-1" />}
              <div className={`rounded-xl p-3 w-fit max-w-[80%] ${msg.sender === 'user' ? 'bg-blue-200 text-blue-800 rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
                {msg.type === 'text' && <p className="text-sm break-words">{msg.content}</p>}
                {msg.type === 'file' && msg.content instanceof File && (
                  <div className="flex items-center bg-blue-100 rounded-md p-2">
                    <FaFileUpload className="text-blue-500 mr-2" />
                    <span className="text-xs font-medium text-blue-700 break-words">{msg.content.name}</span>
                  </div>
                )}
                {msg.type === 'video' && msg.videoUrl && (
                  <div className="relative rounded-md overflow-hidden shadow-md">
                    <video src={msg.videoUrl} controls className="w-full h-auto max-h-64 object-cover rounded-md" poster="https://via.placeholder.com/400x300/f0f0f0/888?Text=Math+Solution" />
                    <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white rounded-full p-1">
                      <FaPlayCircle className="text-sm" />
                    </div>
                  </div>
                )}
              </div>
              {msg.sender === 'user' && <FaUser className="text-xl text-blue-500 ml-3 mt-1" />}
            </div>
          ))}
          {isBotTyping && (
            <div className="flex justify-start items-center">
              <FaRobot className="text-xl text-indigo-500 mr-3 mt-1" />
              <div className="rounded-xl p-3 bg-gray-100 text-gray-800 rounded-bl-none">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-[200ms]"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-[300ms]"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-[400ms]"></div>
                  <span className="text-sm italic text-gray-600">Processing...</span>
                </div>
              </div>
            </div>
          )}
          {botResponseVideoUrl && messages[messages.length - 1]?.sender === 'bot' && messages[messages.length - 1]?.type === 'video' && (
            <div className="flex justify-start items-start">
              <FaRobot className="text-xl text-indigo-500 mr-3 mt-1" />
              <div className="rounded-xl p-3 bg-gray-100 text-gray-800 rounded-bl-none">
                <div className="relative rounded-md overflow-hidden shadow-md">
                  <video src={botResponseVideoUrl} controls className="w-full h-auto max-h-64 object-cover rounded-md" poster="https://via.placeholder.com/400x300/f0f0f0/888?Text=Math+Solution" />
                  <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white rounded-full p-1">
                    <FaPlayCircle className="text-sm" />
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>
        <div className="bg-gray-50 py-3 px-4 border-t border-gray-200 flex items-center space-x-3">
          <div className="relative flex-grow">
            <input
              type="text"
              className="w-full rounded-full py-2.5 pl-4 pr-12 border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              placeholder="Type your math problem or question..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button
              onClick={handleSendMessage}
              className="absolute right-3 top-1/2 -translate-y-1/2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-full p-2 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-colors duration-200"
            >
              <FaPaperPlane className="text-lg" />
            </button>
          </div>
          <div>
            <label htmlFor="file-upload" className="cursor-pointer text-gray-600 hover:text-indigo-500 transition-colors duration-200">
              <FaFileUpload className="text-xl" />
              <input id="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept="image/*, application/pdf" />
            </label>
            {selectedFile && (
              <button
                onClick={handleFileUpload}
                className="ml-2 bg-green-500 hover:bg-green-600 text-white rounded-md py-2 px-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-green-400 transition-colors duration-200"
              >
                Upload
              </button>
            )}
          </div>
        </div>
      </div>
      <p className="mt-6 text-sm text-gray-500">
        Powered by <span className="font-semibold text-indigo-600">Awesome Math AI</span>
      </p>
    </div>
  );
};

export default ChatbotUI;