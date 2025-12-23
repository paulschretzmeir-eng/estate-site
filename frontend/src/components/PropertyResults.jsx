import React from 'react';

function formatCurrencyEUR(value) {
  if (value === null || value === undefined) return null;
  const num = typeof value === 'number' ? value : parseFloat(String(value).replace(/[^0-9.]/g, ''));
  if (Number.isNaN(num)) return String(value);
  return num.toLocaleString('en-US');
}

function AmenityList({ items }) {
  if (!Array.isArray(items) || items.length === 0) return null;
  const top = items.slice(0, 5).map(String);
  return (
    <p className="mt-2 text-sm text-gray-600">
      Nearby: {top.join(', ')}
    </p>
  );
}

function Stat({ icon, children }) {
  return (
    <div className="flex items-center gap-1 text-gray-700">
      {icon}
      <span className="text-sm">{children}</span>
    </div>
  );
}

function BedIcon() {
  return (
    <svg className="h-4 w-4 text-gray-500" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M3 7a2 2 0 0 1 2-2h9a3 3 0 0 1 3 3v1h2a2 2 0 0 1 2 2v6h-2v-2H5v2H3V7zm2 7h14v-3a1 1 0 0 0-1-1h-5v-1a1 1 0 0 0-1-1H5v6z"/>
    </svg>
  );
}

function BathIcon() {
  return (
    <svg className="h-4 w-4 text-gray-500" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M7 3a3 3 0 0 1 3 3v4h9a1 1 0 1 1 0 2h-1.126l-.84 6.719A3 3 0 0 1 14.06 22H9.94a3 3 0 0 1-2.974-2.281L6.126 12H5a1 1 0 1 1 0-2h3V6a1 1 0 0 0-2 0 1 1 0 1 1-2 0 3 3 0 0 1 3-3z"/>
    </svg>
  );
}

export default function PropertyResults({ results }) {
  const list = Array.isArray(results) ? results : [];

  if (list.length === 0) {
    return (
      <div className="w-full rounded-lg border border-gray-200 bg-white p-6 text-center text-gray-700">
        No properties found. Try adjusting your search.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {list.map((item, idx) => {
        const city = item?.city || 'Unknown';
        const beds = item?.bedrooms ?? '-';
        const baths = item?.bathrooms ?? '-';
        const price = item?.price;
        const rent = item?.rent_price;
        const status = item?.construction_status || '—';
        const amenities = item?.nearby_amenities;

        const saleText = price != null ? `${formatCurrencyEUR(price)} EUR` : null;
        const rentText = rent != null ? `${formatCurrencyEUR(rent)} EUR/month` : null;

        return (
          <div
            key={item?.id ?? idx}
            className="group relative flex flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="mb-3 flex items-start justify-between">
              <h3 className="text-lg font-semibold text-gray-900">{city}</h3>
              {status ? (
                <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
                  {String(status).replace(/_/g, ' ')}
                </span>
              ) : null}
            </div>

            <div className="mb-3 flex items-center gap-4">
              <Stat icon={<BedIcon />}>{beds} bd</Stat>
              <Stat icon={<BathIcon />}>{baths} ba</Stat>
            </div>

            <div className="mb-2 flex flex-wrap items-center gap-3 text-gray-800">
              {saleText ? (
                <span className="text-sm font-medium">
                  For sale: <span className="font-semibold">{saleText}</span>
                </span>
              ) : null}
              {rentText ? (
                <span className="text-sm font-medium">
                  Rent: <span className="font-semibold">{rentText}</span>
                </span>
              ) : null}
            </div>

            <AmenityList items={amenities} />
          </div>
        );
      })}
    </div>
  );
}
