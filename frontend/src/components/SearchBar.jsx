import React, { useState } from 'react'

export default function SearchBar({ onSearch }){
  const [mode, setMode] = useState('natural') // natural | prompt | filters
  const [text, setText] = useState('')

  const submit = (e) => {
    e.preventDefault()
    if(!text && mode !== 'filters') return
    onSearch(text)
  }

  return (
    <div className="bg-white p-4 rounded shadow">
      <div className="flex items-center gap-3 mb-3">
        <button onClick={()=>setMode('natural')} className={`px-3 py-1 rounded ${mode==='natural'?'bg-blue-600 text-white':'bg-gray-100'}`}>Natural</button>
        <button onClick={()=>setMode('prompt')} className={`px-3 py-1 rounded ${mode==='prompt'?'bg-blue-600 text-white':'bg-gray-100'}`}>Prompt+Filters</button>
        <button onClick={()=>setMode('filters')} className={`px-3 py-1 rounded ${mode==='filters'?'bg-blue-600 text-white':'bg-gray-100'}`}>Filters</button>
      </div>

      {mode !== 'filters' && (
        <form onSubmit={submit} className="flex gap-2">
          <input value={text} onChange={e=>setText(e.target.value)} placeholder={mode==='natural'?"e.g. 2 bedroom apartment under 800k in Berlin":"Enter prompt + filters"} className="flex-1 border px-3 py-2 rounded" />
          <button className="px-4 py-2 bg-blue-600 text-white rounded">Search</button>
        </form>
      )}

      {mode === 'filters' && (
        <div className="text-sm text-gray-600">Use the filter panel to set structured filters and click Search in the panel.</div>
      )}
    </div>
  )
}
