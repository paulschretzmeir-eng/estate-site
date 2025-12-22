import React from 'react'

export default function PropertyCard({ listing }){
  const img = (listing.image_urls && listing.image_urls[0]) || 'https://via.placeholder.com/400x250.png?text=Property'
  const price = listing.price ? `${Number(listing.price).toLocaleString()} EUR` : null
  const rent = listing.rent_price ? `${Number(listing.rent_price).toLocaleString()} EUR/mo` : null

  return (
    <div className="bg-white rounded shadow overflow-hidden">
      <img src={img} alt="property" className="w-full h-48 object-cover" />
      <div className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold">{listing.project_name || listing.address || listing.city}</h3>
            <div className="text-sm text-gray-500">{listing.city} • {listing.bedrooms || '-'} bd</div>
          </div>
          <div className="text-right">
            {price && <div className="font-bold text-lg">{price}</div>}
            {rent && <div className="text-sm text-gray-600">{rent}</div>}
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-2">{listing.neighborhood_description || listing.description || ''}</p>
        <div className="mt-3 text-sm text-gray-500">Status: {listing.construction_status || 'unknown'}</div>
      </div>
    </div>
  )
}
