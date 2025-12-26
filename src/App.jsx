import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import SearchPage from './pages/SearchPage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ChatPage from './pages/ChatPage';
import OAuthCallback from './pages/OAuthCallback';
import Navbar from './components/Navbar';
import { isAuthenticated } from './utils/auth';

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        {/* Landing Page - NO NAVBAR */}
        <Route path="/" element={<LandingPage />} />

        {/* Chat Pages - NO NAVBAR (has its own layout) */}
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:chatId" element={<ChatPage />} />
        
        {/* OAuth Callback */}
        <Route path="/auth/callback" element={<OAuthCallback />} />

        {/* All other pages WITH NAVBAR */}
        <Route
          path="/*"
          element={
            <>
              <Navbar />
              <Routes>
                <Route path="/search" element={<SearchPage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
              </Routes>
            </>
          }
        />
      </Routes>
    </div>
  );
}

export default App;
