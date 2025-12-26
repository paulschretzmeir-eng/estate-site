import React, { useState } from 'react';
import { addToFavorites, removeFromFavorites } from '../utils/api';
import { isAuthenticated } from '../utils/auth';

function PropertyCard({ property, compact = false, isFavorite: initialFavorite = false }) {
  const [isFavorite, setIsFavorite] = useState(initialFavorite);
  const [showDetails, setShowDetails] = useState(false);

  const handleFavoriteToggle = async (e) => {
    e.preventDefault();
    if (!isAuthenticated()) {
      alert('Please log in to save favorites');
      return;
    }

    try {
      if (isFavorite) {
        await removeFromFavorites(property.id);
        setIsFavorite(false);
      } else {
        await addToFavorites(property.id);
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  if (compact) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-lg transition-shadow">
        <div className="flex gap-3 p-3">
          {/* Image */}
          {property.image_url && (
            <div className="w-24 h-24 flex-shrink-0">
              <img
                src={property.image_url}
                alt={property.title}
                className="w-full h-full object-cover rounded-lg"
              />
            </div>
          )}

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white line-clamp-1">
                {property.title}
              </h3>
              <button
                onClick={handleFavoriteToggle}
                className="flex-shrink-0 p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
              >
                <svg
                  className={`h-4 w-4 ${
                    isFavorite
                      ? 'fill-red-500 text-red-500'
                      : 'fill-none text-gray-400'
                  }`}
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>

            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {property.location}
            </p>

            <div className="flex items-center gap-3 mt-2">
              <span className="text-lg font-bold text-magenta-500">
                €{property.price?.toLocaleString()}
              </span>
              <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                {property.bedrooms && (
                  <span>🛏️ {property.bedrooms}</span>
                )}
                {property.bathrooms && (
                  <span>🚿 {property.bathrooms}</span>
                )}
                {property.surface_area && (
                  <span>📐 {property.surface_area}m²</span>
                )}
              </div>
            </div>

            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-xs text-magenta-500 hover:text-magenta-600 font-medium mt-2"
            >
              {showDetails ? 'Hide details' : 'View details'}
            </button>
          </div>
        </div>

        {/* Expanded Details */}
        {showDetails && (
          <div className="px-3 pb-3 pt-0 border-t border-gray-200 dark:border-gray-700 mt-3">
            <div className="space-y-2 text-sm">
              {property.description && (
                <p className="text-gray-600 dark:text-gray-400">
                  {property.description}
                </p>
              )}
              {property.amenities && property.amenities.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                    Amenities:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {property.amenities.map((amenity, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-xs rounded-full"
                      >
                        {amenity}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Full card view (for search results page)
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow">
      {/* Image */}
      {property.image_url && (
        <div className="relative h-48 overflow-hidden">
          <img
            src={property.image_url}
            alt={property.title}
            className="w-full h-full object-cover"
          />
          <button
            onClick={handleFavoriteToggle}
            className="absolute top-3 right-3 p-2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-full hover:scale-110 transition-transform"
          >
            <svg
              className={`h-5 w-5 ${
                isFavorite
                  ? 'fill-red-500 text-red-500'
                  : 'fill-none text-gray-600 dark:text-gray-400'
              }`}
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {property.title}
        </h3>

        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          📍 {property.location}
        </p>

        <div className="flex items-center justify-between mb-3">
          <span className="text-2xl font-bold text-magenta-500">
            €{property.price?.toLocaleString()}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {property.listing_type}
          </span>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
          {property.bedrooms && (
            <span>🛏️ {property.bedrooms} bed</span>
          )}
          {property.bathrooms && (
            <span>🚿 {property.bathrooms} bath</span>
          )}
          {property.surface_area && (
            <span>📐 {property.surface_area}m²</span>
          )}
        </div>

        {property.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
            {property.description}
          </p>
        )}

        {property.amenities && property.amenities.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {property.amenities.slice(0, 3).map((amenity, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-xs rounded-full"
              >
                {amenity}
              </span>
            ))}
            {property.amenities.length > 3 && (
              <span className="px-2 py-1 text-xs text-gray-500">
                +{property.amenities.length - 3} more
              </span>
            )}
          </div>
        )}

        <button className="w-full py-2 bg-gradient-to-r from-magenta-500 to-blue-500 text-white font-medium rounded-lg hover:shadow-lg transition-all">
          View Details
        </button>
      </div>
    </div>
  );
}

export default PropertyCard;
