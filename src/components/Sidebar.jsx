import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { getChatList, deleteChat } from '../utils/api';
import { isAuthenticated, currentUser, logout } from '../utils/auth';

function Sidebar({ isOpen, onClose }) {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const user = currentUser();

  useEffect(() => {
    if (isAuthenticated()) {
      loadChats();
    } else {
      setIsLoading(false);
    }
  }, []);

  const loadChats = async () => {
    try {
      const chatList = await getChatList();
      setChats(chatList || []);
    } catch (error) {
      console.error('Failed to load chats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    navigate('/chat');
    onClose?.();
  };

  const handleDeleteChat = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (window.confirm('Delete this chat?')) {
      try {
        await deleteChat(id);
        setChats(prev => prev.filter(chat => chat.id !== id));
        if (chatId === id) {
          navigate('/chat');
        }
      } catch (error) {
        console.error('Failed to delete chat:', error);
      }
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const groupChatsByDate = (chats) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);

    const groups = {
      today: [],
      yesterday: [],
      lastWeek: [],
      older: []
    };

    chats.forEach(chat => {
      const chatDate = new Date(chat.updated_at || chat.created_at);
      const chatDateOnly = new Date(chatDate.getFullYear(), chatDate.getMonth(), chatDate.getDate());

      if (chatDateOnly.getTime() === today.getTime()) {
        groups.today.push(chat);
      } else if (chatDateOnly.getTime() === yesterday.getTime()) {
        groups.yesterday.push(chat);
      } else if (chatDateOnly >= lastWeek) {
        groups.lastWeek.push(chat);
      } else {
        groups.older.push(chat);
      }
    });

    return groups;
  };

  const groupedChats = groupChatsByDate(chats);

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-magenta-500 to-blue-500 text-white font-medium rounded-lg hover:shadow-lg transition-all duration-200"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-2">
          {!isAuthenticated() ? (
            <div className="p-4 text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                Sign in to save your chat history
              </p>
              <Link
                to="/login"
                className="text-sm text-magenta-500 hover:text-magenta-600 font-medium"
              >
                Log in
              </Link>
            </div>
          ) : isLoading ? (
            <div className="p-4 text-center">
              <div className="inline-block w-6 h-6 border-2 border-gray-300 border-t-magenta-500 rounded-full animate-spin"></div>
            </div>
          ) : chats.length === 0 ? (
            <div className="p-4 text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No chats yet
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {groupedChats.today.length > 0 && (
                <div>
                  <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Today
                  </h3>
                  <div className="space-y-1">
                    {groupedChats.today.map(chat => (
                      <ChatItem
                        key={chat.id}
                        chat={chat}
                        isActive={chatId === chat.id}
                        onDelete={handleDeleteChat}
                      />
                    ))}
                  </div>
                </div>
              )}

              {groupedChats.yesterday.length > 0 && (
                <div>
                  <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Yesterday
                  </h3>
                  <div className="space-y-1">
                    {groupedChats.yesterday.map(chat => (
                      <ChatItem
                        key={chat.id}
                        chat={chat}
                        isActive={chatId === chat.id}
                        onDelete={handleDeleteChat}
                      />
                    ))}
                  </div>
                </div>
              )}

              {groupedChats.lastWeek.length > 0 && (
                <div>
                  <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Last 7 Days
                  </h3>
                  <div className="space-y-1">
                    {groupedChats.lastWeek.map(chat => (
                      <ChatItem
                        key={chat.id}
                        chat={chat}
                        isActive={chatId === chat.id}
                        onDelete={handleDeleteChat}
                      />
                    ))}
                  </div>
                </div>
              )}

              {groupedChats.older.length > 0 && (
                <div>
                  <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                    Older
                  </h3>
                  <div className="space-y-1">
                    {groupedChats.older.map(chat => (
                      <ChatItem
                        key={chat.id}
                        chat={chat}
                        isActive={chatId === chat.id}
                        onDelete={handleDeleteChat}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* User Profile */}
        {isAuthenticated() && (
          <div className="p-3 border-t border-gray-200 dark:border-gray-800">
            <div className="relative">
              <button
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-magenta-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                  {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="flex-1 text-left overflow-hidden">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user?.email}
                  </p>
                </div>
                <svg className="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>

              {/* Profile Menu */}
              {showProfileMenu && (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1">
                  <Link
                    to="/settings"
                    className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => setShowProfileMenu(false)}
                  >
                    Settings
                  </Link>
                  <Link
                    to="/favorites"
                    className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => setShowProfileMenu(false)}
                  >
                    Favorites
                  </Link>
                  <hr className="my-1 border-gray-200 dark:border-gray-700" />
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Log out
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </aside>
    </>
  );
}

function ChatItem({ chat, isActive, onDelete }) {
  const [showDelete, setShowDelete] = useState(false);

  return (
    <Link
      to={`/chat/${chat.id}`}
      className={`block px-3 py-2 rounded-lg transition-colors group relative ${
        isActive
          ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50'
      }`}
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm truncate">
            {chat.title || 'New Chat'}
          </p>
        </div>
        {showDelete && (
          <button
            onClick={(e) => onDelete(chat.id, e)}
            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-all"
          >
            <svg className="h-4 w-4 text-red-600 dark:text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        )}
      </div>
    </Link>
  );
}

export default Sidebar;
