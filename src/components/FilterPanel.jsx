import React, { useState } from 'react'

export default function FilterPanel({ onApply }){
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [bedrooms, setBedrooms] = useState('')
  const [bathrooms, setBathrooms] = useState('')
  const [city, setCity] = useState('')
  const [forSale, setForSale] = useState(false)
  const [forRent, setForRent] = useState(false)
  const [construction, setConstruction] = useState('')

  const apply = () => {
    const filters = {}
    if(minPrice) filters.min_price = Number(minPrice)
    if(maxPrice) filters.max_price = Number(maxPrice)
    if(bedrooms) filters.bedrooms = Number(bedrooms)
    if(bathrooms) filters.bathrooms = Number(bathrooms)
    if(city) filters.city = city
    if(forSale) filters.available_for_sale = true
    if(forRent) filters.available_for_rent = true
    if(construction) filters.construction_status = construction
    onApply(filters)
  }

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="font-semibold mb-2">Filters</h3>
      <div className="grid grid-cols-2 gap-2">
        <input placeholder="Min price" value={minPrice} onChange={e=>setMinPrice(e.target.value)} className="border px-2 py-1 rounded" />
        <input placeholder="Max price" value={maxPrice} onChange={e=>setMaxPrice(e.target.value)} className="border px-2 py-1 rounded" />
        <input placeholder="Bedrooms" value={bedrooms} onChange={e=>setBedrooms(e.target.value)} className="border px-2 py-1 rounded" />
        <input placeholder="Bathrooms (1-4)" value={bathrooms} onChange={e=>setBathrooms(e.target.value)} className="border px-2 py-1 rounded" />
        <input placeholder="City" value={city} onChange={e=>setCity(e.target.value)} className="border px-2 py-1 rounded col-span-2" />
      </div>
      <div className="flex items-center gap-3 mt-3">
        <label className="flex items-center gap-2"><input type="checkbox" checked={forSale} onChange={e=>setForSale(e.target.checked)} /> For sale</label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={forRent} onChange={e=>setForRent(e.target.checked)} /> For rent</label>
      </div>
      <div className="mt-3">
        <select value={construction} onChange={e=>setConstruction(e.target.value)} className="border px-2 py-1 rounded w-full">
          <option value="">Any construction status</option>
          <option value="completed">Completed</option>
          <option value="under_construction">Under construction</option>
          <option value="pre_construction">Pre-construction</option>
        </select>
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={apply} className="px-3 py-2 bg-blue-600 text-white rounded">Apply</button>
      </div>
    </div>
  )
}
