import React, { useState } from 'react'
import SearchBar from '../components/SearchBar'
import FilterPanel from '../components/FilterPanel'
import ResultsList from '../components/ResultsList'
import { searchAPI } from '../utils/api'

export default function Search(){
  const [filters, setFilters] = useState({})
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState([])

  const doSearch = async (promptOrText) => {
    setError(null)
    setLoading(true)
    setQuery(promptOrText || '')
    try{
      const body = promptOrText || ''
      const resp = await searchAPI(body)
      // Backend returns: {ok: true, data: {filters, results, response}}
      console.log('[Search] API response:', resp)
      if (resp.ok && resp.data) {
        const listings = resp.data.results || []
        console.log('[Search] Setting results:', listings.length, 'listings')
        setResults(listings)
      } else {
        // Fallback for unexpected structure
        setResults(resp.results || [])
      }
    }catch(e){
      console.error('[Search] Error:', e)
      setError(e.message)
    }finally{
      setLoading(false)
    }
  }

  const applyFilters = (f) => {
    setFilters(f)
    // build a prompt summarizing filters or call backend directly with filters later
    const prompt = Object.keys(f).length ? `filters:${JSON.stringify(f)}` : ''
    doSearch(prompt)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="grid md:grid-cols-4 gap-6">
        <div className="md:col-span-3">
          <SearchBar onSearch={doSearch} />
          <div className="mt-4">
            {loading && <div className="p-4 bg-white rounded shadow">Loading...</div>}
            {error && <div className="p-4 bg-red-50 text-red-700 rounded">{error}</div>}
            {!loading && <ResultsList listings={results} />}
          </div>
        </div>
        <aside className="md:col-span-1">
          <FilterPanel onApply={applyFilters} />
        </aside>
      </div>
    </div>
  )
}
