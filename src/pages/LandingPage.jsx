import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LandingPage() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    // Navigate to chat page with the query
    navigate('/chat', { state: { initialQuery: query } });
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300 bg-white dark:bg-gray-950">
      {/* Header */}
      <header className="w-full px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-magenta-500 to-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">E</span>
          </div>
          <span className="text-xl font-semibold text-gray-900 dark:text-white">EstateGPT</span>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            Log in
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="px-4 py-2 text-sm font-medium bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
          >
            Sign up for free
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 pb-24">
        <div className="w-full max-w-4xl mx-auto text-center space-y-12">
          {/* Hero Text */}
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-semibold text-gray-900 dark:text-white">
              What property can I help with?
            </h1>
          </div>

          {/* Search Bar Container */}
          <div className="w-full max-w-3xl mx-auto">
            <form onSubmit={handleSearch} className="relative">
              {/* Gradient Border Effect */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-magenta-500 via-purple-500 to-blue-500 rounded-2xl opacity-75 blur-sm group-hover:opacity-100 transition duration-200"></div>
              
              {/* Search Input */}
              <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask anything about properties..."
                  className="w-full px-6 py-5 pr-14 text-lg bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 rounded-2xl outline-none focus:ring-0"
                  disabled={isLoading}
                />
                
                <button
                  type="submit"
                  disabled={isLoading || !query.trim()}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 bg-gradient-to-r from-magenta-500 to-blue-500 rounded-xl text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all duration-200"
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

            {/* Quick Action Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
              <button
                onClick={() => setQuery('2 bedroom apartment in Bucharest under 300000')}
                className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="mr-2">🏢</span>
                Bucharest apartments
              </button>
              <button
                onClick={() => setQuery('luxury villa with pool for rent')}
                className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="mr-2">🏡</span>
                Luxury villas
              </button>
              <button
                onClick={() => setQuery('studio apartment near metro under 150000')}
                className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="mr-2">🚇</span>
                Near metro
              </button>
            </div>
          </div>

          {/* Feature Pills */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-8">
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-900 rounded-full text-sm text-gray-600 dark:text-gray-400">
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span>AI-powered search</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-900 rounded-full text-sm text-gray-600 dark:text-gray-400">
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span>200+ properties</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-900 rounded-full text-sm text-gray-600 dark:text-gray-400">
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span>Instant results</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full px-6 py-4 text-center text-xs text-gray-500 dark:text-gray-600">
        <p>
          By using EstateGPT, you agree to our{' '}
          <a href="#" className="hover:text-gray-700 dark:hover:text-gray-400 underline">Terms</a>
          {' '}and have read our{' '}
          <a href="#" className="hover:text-gray-700 dark:hover:text-gray-400 underline">Privacy Policy</a>
        </p>
      </footer>
    </div>
  );
}

export default LandingPage;
