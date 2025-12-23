import React, { useState } from 'react';
import { searchProperties } from '../services/api';

export default function SearchBar({ onSearchResults }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;

    setError('');
    const trimmed = query.trim();
    if (!trimmed) {
      setError('Please enter a search query.');
      return;
    }

    setLoading(true);
    try {
      const data = await searchProperties(trimmed);
      const results = Array.isArray(data?.results) ? data.results : data;
      if (typeof onSearchResults === 'function') {
        onSearchResults(results);
      }
    } catch (err) {
      const message = err?.message || 'Something went wrong while searching.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div className="flex w-full items-stretch gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 2 bedroom apartment in Bucharest under 300000"
            aria-label="Search query"
            className="flex-1 rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-400 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="submit"
            disabled={loading}
            className={`rounded-xl px-5 py-3 font-medium text-white shadow-sm transition ${
              loading
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-300'
            }`}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        ) : null}
      </form>
    </div>
  );
}
