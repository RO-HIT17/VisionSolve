'use client'
import React, { useState, useRef, useEffect } from 'react';
import { 
  FaPaperPlane, 
  FaFileUpload, 
  FaRobot, 
  FaUser, 
  FaSpinner, 
  FaPlayCircle, 
  FaBars, 
  FaHistory, 
  FaCog, 
  FaQuestion, 
  FaSignOutAlt,
  FaSearch,
  FaBell,
  FaChevronLeft
} from 'react-icons/fa';
import '../globals.css'

interface Message {
  sender: 'user' | 'bot';
  type: 'text' | 'file' | 'video';
  content: string | File | null;
  videoUrl?: string;
  imageUrl?: string;
}

interface Conversation {
  id: string;
  title: string;
  date: string;
}

const ChatbotUI: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFilePreview, setSelectedFilePreview] = useState<string | null>(null);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [botResponseVideoUrl, setBotResponseVideoUrl] = useState<string | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [pastConversations, setPastConversations] = useState<Conversation[]>([
    { id: '1', title: 'Linear Equations', date: '2025-03-14' },
    { id: '2', title: 'Calculus Problem', date: '2025-03-13' },
    { id: '3', title: 'Geometry Question', date: '2025-03-10' },
  ]);

  const handleSendMessage = async () => {
    if (inputText.trim()) {
      const newMessage: Message = { sender: 'user', type: 'text', content: inputText.trim() };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInputText('');
      setIsBotTyping(true);
      
      setTimeout(async () => {
        const mockVideoUrl = 'https://www.w3schools.com/html/mov_bbb.mp4';
        const botReply: Message = { 
          sender: 'bot', 
          type: 'video', 
          content: null, 
          videoUrl: mockVideoUrl 
        };
        setMessages((prevMessages) => [...prevMessages, botReply]);
        setIsBotTyping(false);
      }, 1500);
    }
  };

  const createImagePreview = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        resolve(reader.result as string);
      };
      reader.readAsDataURL(file);
    });
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const isImage = file.type.startsWith('image/');
      let imageUrl = isImage ? await createImagePreview(file) : undefined;

      const newMessage: Message = {
        sender: 'user',
        type: 'file',
        content: file,
        imageUrl: imageUrl
      };
      setMessages((prevMessages) => [...prevMessages, newMessage]);

      setIsBotTyping(true);
      setTimeout(async () => {
        const mockVideoUrl = 'https://www.w3schools.com/html/mov_bbb.mp4';
        const botReply: Message = { 
          sender: 'bot', 
          type: 'video', 
          content: null, 
          videoUrl: mockVideoUrl 
        };
        setMessages((prevMessages) => [...prevMessages, botReply]);
        setIsBotTyping(false);
      }, 3000);
    }
  };

  const handleFileUpload = async () => {
    if (selectedFile) {
      const isImage = selectedFile.type.startsWith('image/');
      const newMessage: Message = {
        sender: 'user',
        type: 'file',
        content: selectedFile,
        imageUrl: isImage ? selectedFilePreview || undefined : undefined
      };
      
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setSelectedFile(null);
      setSelectedFilePreview(null);
      setIsBotTyping(true);
      setBotResponseVideoUrl(null);

      setTimeout(async () => {
        const mockVideoUrl = 'https://www.w3schools.com/html/mov_bbb.mp4';
        const botReply: Message = { sender: 'bot', type: 'video', content: null, videoUrl: mockVideoUrl };
        setMessages((prevMessages) => [...prevMessages, botReply]);
        setIsBotTyping(false);
      }, 3000);
    }
  };

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const startNewConversation = () => {
    setMessages([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 flex flex-col">
  {/* Navbar */}
  <nav className="bg-white shadow-md py-3 px-6 flex items-center justify-between">
    <div className="flex items-center">
      <button onClick={toggleSidebar} className="text-gray-700 hover:text-indigo-600 mr-4">
        <FaBars className="text-xl" />
      </button>
      <h1 className="font-bold text-xl text-indigo-700">Math Solution Bot</h1>
    </div>
    <div className="flex items-center space-x-4">
      <div className="relative">
        <input
          type="text"
          placeholder="Search conversations..."
          className="bg-gray-100 rounded-full py-1.5 px-4 pr-8 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400 w-48"
        />
        <FaSearch className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-xs" />
      </div>
      <button className="relative text-gray-700 hover:text-indigo-600">
        <FaBell className="text-xl" />
        <span className="absolute -top-1 -right-1 bg-red-500 rounded-full w-4 h-4 flex items-center justify-center text-white text-xs">2</span>
      </button>
      <div className="h-8 w-8 rounded-full bg-indigo-500 text-white flex items-center justify-center font-medium">
        CC
      </div>
    </div>
  </nav>

  <div className="flex flex-1 overflow-hidden">
    {/* Sidebar */}
    <aside
      className={`bg-white shadow-lg transition-all duration-300 ease-in-out ${
        isSidebarOpen ? "w-64" : "w-0"
      } overflow-hidden flex flex-col`}
    >
      <div className="p-4 border-b">
        <button
          onClick={startNewConversation}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-full py-2 px-4 text-sm font-medium flex items-center justify-center"
        >
          <FaRobot className="mr-2" /> New Conversation
        </button>
      </div>
      <div className="overflow-y-auto flex-1">
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Recent conversations</h3>
          {pastConversations.map((convo) => (
            <div
              key={convo.id}
              className="py-2 px-3 rounded-md hover:bg-indigo-50 cursor-pointer mb-1 group transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 group-hover:text-indigo-700">
                  {convo.title}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(convo.date).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>

    <div className="flex-1 flex flex-col">
      <div className="flex-1 p-4 sm:p-6 md:p-8 flex flex-col items-center">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden max-w-2xl w-full flex flex-col">
          <div className="bg-indigo-500 text-white py-4 px-6 flex items-center justify-between">
            <div className="flex items-center">
              <FaRobot className="text-xl mr-3" />
              <h2 className="text-lg font-semibold">Chat Session</h2>
            </div>
            <span className="text-sm opacity-75">Online</span>
          </div>

          <div className="p-4 h-[500px] overflow-y-auto flex flex-col space-y-3 scroll-smooth" id="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} items-start`}>
            {msg.sender === "bot" && <FaRobot className="text-xl text-indigo-500 mr-3 mt-1" />}
            <div
              className={`rounded-xl p-3 w-fit max-w-[80%] ${
                msg.sender === "user"
                  ? "bg-blue-200 text-blue-800 rounded-br-none"
                  : "bg-gray-100 text-gray-800 rounded-bl-none"
              }`}
            >
              {msg.type === "text" && <p className="text-sm break-words">{msg.content}</p>}
              {msg.type === "file" && (
                <div>
                  {msg.imageUrl ? (
                    <img 
                      src={msg.imageUrl} 
                      alt="Uploaded content" 
                      className="max-w-xs h-auto rounded-lg"
                    />
                  ) : (
                    <div className="text-sm text-gray-600">
                      <FaFileUpload className="inline mr-2" />
                      {(msg.content as File)?.name || "File"}
                    </div>
                  )}
                </div>
              )}
              {msg.type === "video" && msg.videoUrl && (
                <video 
                  controls 
                  className="mt-2 rounded-lg"
                  style={{ maxWidth: '100%' }}
                >
                  <source src={msg.videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              )}
            </div>
            {msg.sender === "user" && <FaUser className="text-xl text-blue-500 ml-3 mt-1" />}
          </div>
        ))}
        {isBotTyping && (
          <div className="flex items-center justify-start">
            <FaRobot className="text-xl text-indigo-500 mr-3" />
            <div className="bg-gray-100 rounded-xl p-3">
              <FaSpinner className="animate-spin" />
            </div>
          </div>
        )}
        <div ref={chatBottomRef} />
      </div>

          <div className="bg-gray-50 py-3 px-4 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="relative flex-grow">
                <input
                  type="text"
                  className="w-full rounded-full py-2.5 pl-4 pr-12 border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  placeholder="Type your math problem or question..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
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
                </label>
                <input id="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept="image/*, application/pdf" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <p className="mt-6 text-sm text-gray-500  text-center">
        Powered by <span className="font-semibold text-indigo-600">Code Crusaders</span>
      </p>
    </div>
  </div>
</div>

   
  );
};

export default ChatbotUI;