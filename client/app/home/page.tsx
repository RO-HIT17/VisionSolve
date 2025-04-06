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
  FaChevronLeft,
  FaPencilAlt 
} from 'react-icons/fa';
import '../globals.css'

interface Message {
  sender: 'user' | 'bot';
  type: 'text' | 'file' | 'video';
  message?: string;
  content: string | File | null;
  videoUrl?: string;
  imageUrl?: string;
}

interface Conversation {
    id: string;
    title: string;
    date: string;
    topic: 'photosynthesis' | 'calculus' | 'central';
  }
  const topicMessages = {
    photosynthesis: [
      {
        sender: 'user',
        type: 'text',
        content: 'What do you mean by Photosynthesis',
      },
      {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: '/static/photosynthesis.mp4'
      },
      {
        sender: 'user',
        type: 'text',
        content: 'Explain any physics topic',
      },
      {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: '/static/physics.mp4'
      }
    ],
    calculus: [
      {
        sender: 'user',
        type: 'text',
        content: 'How to find the derivative of x²?',
      },
      {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: '/static/derivative-solution.mp4'
      },
      {
        sender: 'user',
        type: 'text',
        content: 'Explain gaussian integral',
      },
      {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: '/static/gaussian-integral.mp4'
      }
    ],
    central: [
      {
        sender: 'user',
        type: 'text',
        content: 'Explain central limit theorem',
      },
      {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: '/static/central-limit.mp4'
      }
    ]
  };

const ChatbotUI: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFilePreview, setSelectedFilePreview] = useState<string | null>(null);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [botResponseVideoUrl, setBotResponseVideoUrl] = useState<string | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [selectedHandwritten, setSelectedHandwritten] = useState<File | null>(null);
  const [pastConversations, setPastConversations] = useState<Conversation[]>([
    { 
      id: '1', 
      title: 'Photosynthesis', 
      date: '2025-03-15',
      topic: 'photosynthesis'
    },
    { 
      id: '2', 
      title: 'Calculus Problems', 
      date: '2025-03-15',
      topic: 'calculus'
    },
    { 
      id: '3', 
      title: 'Central Limit Theorem', 
      date: '2025-03-15',
      topic: 'central'
    },
  ]);
  const loadConversation = (conversation: Conversation) => {
    setSelectedConversationId(conversation.id);
    setMessages([]); 
    setTimeout(() => {
      const messages = topicMessages[conversation.topic].map(msg => ({
        ...msg,
        content: msg.content || null,
        videoUrl: msg.videoUrl ? `${msg.videoUrl}` : undefined
      }));
      setMessages(messages as Message[]);
    }, 50);
  };

  const ConversationItem = ({ convo }: { convo: Conversation }) => (
    <div
      key={convo.id}
      onClick={() => loadConversation(convo)}
      className={`py-2 px-3 rounded-md hover:bg-indigo-50 cursor-pointer mb-1 group transition-colors ${
        selectedConversationId === convo.id ? 'bg-indigo-100 border border-indigo-200' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 group-hover:text-indigo-700">
          {convo.title}
        </span>
        <span className="text-xs text-gray-400">
          {new Date(convo.date).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
        </span>
      </div>
      <div className="mt-1 text-xs text-gray-500">
        {convo.topic === 'photosynthesis' && 'Photosynthesis'}
        {convo.topic === 'calculus' && 'Calculus Problems'}
        {convo.topic === 'central' && 'Central Limit Questions'}
      </div>
    </div>
  );

  
  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const newMessage: Message = { sender: 'user', type: 'text', content: inputText.trim() };
    setMessages(prev => [...prev, newMessage]);
    setInputText('');
    setIsBotTyping(true);

    try {
      const response = await fetch('https://video-gen-backend-ava3edcqfvafa6d8.canadacentral-01.azurewebsites.net/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputText.trim() })
      });

      const data = await response.json();
      
      const botReply: Message = {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: data.videoUrl
      };
      setMessages(prev => [...prev, botReply]);
    } catch (error) {
      console.error('Error:', error);
      const botReply: Message = {
        sender: 'bot',
        type: 'text',
        content: 'Sorry, there was an error processing your request.'
      };
      setMessages(prev => [...prev, botReply]);
    }
    setIsBotTyping(false);
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
    if (!file) return;

    const isImage = file.type.startsWith('image/');
    const imageUrl = isImage ? URL.createObjectURL(file) : undefined;

    const newMessage: Message = {
      sender: 'user',
      type: 'file',
      content: file,
      message: "",
      imageUrl
    };
    setMessages(prev => [...prev, newMessage]);

    setIsBotTyping(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('https://video-gen-backend-ava3edcqfvafa6d8.canadacentral-01.azurewebsites.net/api/upload/pdf', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      const botReply: Message = {
        sender: 'bot',
        type: data.videoUrl ? 'video' : 'text',
        content: data.message || null,
        videoUrl: data.videoUrl
      };
      setMessages(prev => [...prev, botReply]);
    } catch (error) {
      console.error('Error:', error);
      const botReply: Message = {
        sender: 'bot',
        type: 'text',
        content: 'Sorry, there was an error processing your file.'
      };
      setMessages(prev => [...prev, botReply]);
    }
    setIsBotTyping(false);
  };
  const handleHandwrittenChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
  
    const newMessage: Message = {
      sender: 'user',
      type: 'file',
      content: file,
      imageUrl: URL.createObjectURL(file)
    };
    setMessages(prev => [...prev, newMessage]);
  
    setIsBotTyping(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
  
      const response = await fetch('https://video-gen-backend-ava3edcqfvafa6d8.canadacentral-01.azurewebsites.net/api/upload/handwritten', {
        method: 'POST',
        body: formData
      });
  
      const data = await response.json();
      
      const botReply: Message = {
        sender: 'bot',
        type: 'video',
        content: null,
        videoUrl: data.videoUrl
      };
      setMessages(prev => [...prev, botReply]);
    } catch (error) {
      console.error('Error:', error);
      const botReply: Message = {
        sender: 'bot',
        type: 'text',
        content: 'Sorry, there was an error processing your question.'
      };
      setMessages(prev => [...prev, botReply]);
    }
    setIsBotTyping(false);
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
        <ConversationItem key={convo.id} convo={convo} />
        ))}
        </div>
      </div>
    </aside>

    <div className="flex-1 flex flex-col">
      <div className="flex-1 p-4 sm:p-6 md:p-8 flex flex-col items-center">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden max-w-4xl w-full flex flex-col">
          <div className="bg-indigo-600 text-white py-4 px-6 flex items-center justify-between">
            <div className="flex items-center">
              <FaRobot className="text-xl mr-3" />
              <h2 className="text-lg font-semibold">Chat Session</h2>
            </div>
            <span className="text-sm opacity-75">Online</span>
          </div>

          <div className="p-4 h-[500px] overflow-y-auto flex flex-col space-y-3">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} items-start`}>
            {msg.sender === "bot" && <FaRobot className="text-xl text-indigo-500 mr-3 mt-1" />}
            <div className={`rounded-xl p-3 w-fit max-w-[80%] ${
              msg.sender === "user" ? "bg-blue-200 text-blue-800 rounded-br-none" : "bg-gray-100 text-gray-800 rounded-bl-none"
            }`}>
              {msg.type === "text" && typeof msg.content === "string" && <p className="text-sm break-words">{msg.content}</p>}
              {msg.type === "file" && (
                <div>
                  {msg.imageUrl ? (
                    <img src={msg.imageUrl} alt="Uploaded content" className="max-w-xs h-auto rounded-lg" />
                  ) : (
                    <div className="text-sm text-gray-600">
                      <FaFileUpload className="inline mr-2" />
                      {(msg.content as File)?.name || "File"}
                      {isBotTyping && <p className="mt-1 text-indigo-500">Processing your file...</p>}
                    </div>
                  )}
                </div>
              )}
              {msg.type === "video" && msg.videoUrl && (
                <video controls className="mt-2 rounded-lg" style={{ maxWidth: '100%' }}>
                  <source src={`https://video-gen-backend-ava3edcqfvafa6d8.canadacentral-01.azurewebsites.net${msg.videoUrl}`} type="video/mp4" />
                  {msg.message && <p className="mt-1">{msg.message}</p>}
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
              className="absolute right-3 top-1/2 -translate-y-1/2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-full p-2"
            >
              <FaPaperPlane className="text-lg" />
            </button>
          </div>
          <div>
            <label htmlFor="file-upload" className="cursor-pointer text-gray-600 hover:text-indigo-500">
              <FaFileUpload className="text-xl" />
            </label>
            <input id="file-upload" type="file" className="sr-only" onChange={handleFileChange} />
          </div>
          <div>
            <label htmlFor="handwritten-upload" className="cursor-pointer text-gray-600 hover:text-indigo-500">
            <FaPencilAlt className="text-xl" />
            </label>
            <input 
            id="handwritten-upload" 
            type="file" 
            className="sr-only" 
            onChange={handleHandwrittenChange}
            accept="image/*"
            />
        </div>
        </div>
      </div>

        </div>
      </div>
      <p className="mt-6 text-sm text-gray-500  text-center mb-4">
        Powered by <span className="font-semibold text-indigo-600">Code Crusaders</span>
      </p>
    </div>
  </div>
</div>

   
  );
};

export default ChatbotUI;