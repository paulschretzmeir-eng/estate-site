import React from 'react'
import PropertyCard from './PropertyCard'

export default function ResultsList({ listings }){
  if(!listings || listings.length===0){
    return <div className="p-4 text-gray-600">No results found.</div>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {listings.map(l => <PropertyCard key={l.id || l._id || Math.random()} listing={l} />)}
    </div>
  )
}
