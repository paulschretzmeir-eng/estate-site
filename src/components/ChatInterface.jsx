import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sendChatMessage, getChatHistory } from '../utils/api';
import PropertyCard from './PropertyCard';
import { isAuthenticated } from '../utils/auth';

function ChatInterface() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Load chat history if chatId exists
    if (chatId) {
      loadChatHistory();
    } else {
      // New chat - start with welcome message
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: 'Hi! I\'m here to help you find the perfect property. What are you looking for?',
        timestamp: new Date()
      }]);
    }
  }, [chatId]);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const history = await getChatHistory(chatId);
      setMessages(history.messages || []);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        chatId: chatId || 'new',
        message: input.trim(),
        conversationHistory: messages
      });

      const assistantMessage = {
        id: Date.now().toString() + '-assistant',
        role: 'assistant',
        content: response.message,
        properties: response.properties || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If this was a new chat, navigate to the chat URL
      if (!chatId && response.chatId) {
        navigate(`/chat/${response.chatId}`, { replace: true });
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now().toString() + '-error',
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    navigate('/chat');
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: 'Hi! I\'m here to help you find the perfect property. What are you looking for?',
      timestamp: new Date()
    }]);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-magenta-500 to-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-3'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-2xl rounded-tl-sm px-4 py-3'
                }`}
              >
                {/* Message Content */}
                <p className="whitespace-pre-wrap">{message.content}</p>

                {/* Property Cards (if any) */}
                {message.properties && message.properties.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {message.properties.map((property) => (
                      <PropertyCard
                        key={property.id}
                        property={property}
                        compact={true}
                      />
                    ))}
                  </div>
                )}

                {/* Timestamp */}
                <p className="text-xs mt-2 opacity-60">
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            {/* Gradient Border */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-magenta-500 via-purple-500 to-blue-500 rounded-xl opacity-50 blur-sm"></div>
            
            <div className="relative flex items-center gap-2 bg-white dark:bg-gray-800 rounded-xl">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about properties, refine your search, or request details..."
                className="flex-1 px-5 py-3.5 bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 rounded-xl outline-none"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="px-6 py-3.5 bg-gradient-to-r from-magenta-500 to-blue-500 text-white font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all duration-200 mr-1"
              >
                {isLoading ? (
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>
            </div>
          </form>

          {/* Sign up prompt for non-authenticated users */}
          {!isAuthenticated() && (
            <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-3">
              <button
                onClick={() => navigate('/signup')}
                className="text-magenta-500 hover:text-magenta-600 font-medium"
              >
                Sign up free
              </button>
              {' '}to save your chat history and favorites
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
