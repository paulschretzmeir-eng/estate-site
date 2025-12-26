import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { searchAPI } from '../utils/api';
import PropertyResults from '../components/PropertyResults';

function SearchPage() {
  const location = useLocation();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState([]);

  // Handle initial query from landing page
  useEffect(() => {
    const initialQuery = location.state?.initialQuery;
    if (initialQuery) {
      setQuery(initialQuery);
      handleSearch(initialQuery);
    }
  }, [location.state]);

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      const response = await searchAPI(searchQuery);
      const listings = Array.isArray(response?.results) ? response.results : response;
      setResults(listings);
    } catch (err) {
      const errorMsg = err?.message || 'Something went wrong. Please try again.';
      setError(errorMsg);
      console.error('[SearchPage] Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-300">
      {/* Search Bar Section */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="relative">
            {/* Gradient Border */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-magenta-500 via-purple-500 to-blue-500 rounded-xl opacity-50 blur-sm"></div>
            
            <div className="relative flex items-stretch gap-2 bg-white dark:bg-gray-800 rounded-xl">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 2 bedroom apartment in Bucharest under 300000"
                className="flex-1 px-5 py-3.5 bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 rounded-xl outline-none"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="px-6 py-3.5 bg-gradient-to-r from-magenta-500 to-blue-500 text-white font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all duration-200"
              >
                {isLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-3 px-4 py-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-400">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 border-4 border-gray-200 dark:border-gray-700 border-t-magenta-500 rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Searching properties...</p>
          </div>
        ) : (
          <PropertyResults results={results} />
        )}
      </div>
    </div>
  );
}

export default SearchPage;
