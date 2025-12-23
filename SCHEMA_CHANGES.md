# EstateGPT Database Schema - European Standards

## Summary of Changes

The database schema has been refactored to meet **European/Romanian real estate standards**:

### 1. **Bathrooms: DECIMAL(3,1) → INTEGER**
   - **Old**: `bathrooms DECIMAL(3,1)` (allowed values like 1.5, 2.0, 2.5)
   - **New**: `bathrooms INTEGER` (whole numbers only: 1, 2, 3, 4)
   - **Reason**: European real estate typically counts rooms (not fractions)
   - **Example**: A 2-bedroom apartment has 2 bathrooms (not 1.5)

### 2. **Square Footage → Square Meters (sqft → sqm)**
   - **Old**: `sqft DECIMAL` (square feet, US standard)
   - **New**: `sqm INTEGER` (square meters, European standard)
   - **Reason**: European and Romanian real estate uses square meters
   - **Conversion**: sqm = sqft ÷ 10.764
   - **Value Ranges**:
     - Studio: 35–55 m²
     - 1-bedroom: 50–75 m²
     - 2-bedroom: 75–110 m²
     - 3-bedroom: 100–140 m²
     - 4-bedroom: 130–170 m²
     - 5+ bedroom: 160–220 m²

### 3. **Currency: EUR (Euros)**
   - **Price Fields**: `price INTEGER` (sale price in EUR)
   - **Rent Fields**: `rent_price INTEGER` (monthly rent in EUR)
   - **Storage**: Whole euros (e.g., 250000 = €250,000)
   - **Reason**: Romania uses EUR; no decimal storage needed for whole euro amounts

## Current Schema (European Standards)

```sql
CREATE TABLE listings (
    id VARCHAR(100) PRIMARY KEY,
    
    -- Core listing data (EUR, Romanian standards)
    price INTEGER,                    -- Sale price in EUR (whole euros)
    rent_price INTEGER,               -- Monthly rent in EUR
    bedrooms INTEGER,                 -- Number of bedrooms
    bathrooms INTEGER,                -- Number of bathrooms (integers only)
    sqm INTEGER,                      -- Area in square meters
    
    -- Property availability
    available_for_sale BOOLEAN DEFAULT FALSE,
    available_for_rent BOOLEAN DEFAULT FALSE,
    
    -- Location & description
    address TEXT,
    city VARCHAR(100),                -- City name (Bucharest, Cluj, etc.)
    description TEXT,                 -- Property description
    nearby_amenities TEXT[],          -- Array of amenities
    construction_status VARCHAR(50),  -- 'completed' or 'under_construction'
    
    -- Media & links
    listing_url TEXT,                 -- URL to listing
    image_urls TEXT[],                -- Array of image URLs
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## How to Apply This Schema

### Option 1: Manual SQL Migration (Recommended for Safety)

1. Open [Supabase Dashboard](https://app.supabase.com)
2. Navigate to **SQL Editor**
3. Create a new query and paste this SQL:

```sql
DROP TABLE IF EXISTS listings CASCADE;

CREATE TABLE listings (
    id VARCHAR(100) PRIMARY KEY,
    price INTEGER,
    rent_price INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    sqm INTEGER,
    available_for_sale BOOLEAN DEFAULT FALSE,
    available_for_rent BOOLEAN DEFAULT FALSE,
    address TEXT,
    city VARCHAR(100),
    description TEXT,
    nearby_amenities TEXT[],
    construction_status VARCHAR(50) DEFAULT 'completed',
    listing_url TEXT,
    image_urls TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_listings_city ON listings(city);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_rent_price ON listings(rent_price);
CREATE INDEX idx_listings_bedrooms ON listings(bedrooms);
CREATE INDEX idx_listings_available_sale ON listings(available_for_sale);
CREATE INDEX idx_listings_available_rent ON listings(available_for_rent);
```

4. Click **Run** to execute

### Option 2: Automated Script (If Direct PostgreSQL Connection Available)

```bash
python scripts/apply_migration.py
```

Note: This requires direct PostgreSQL access which may not be available in all network environments.

## Frontend Display Guide

When displaying listings in the frontend, use these field names and formats:

### Property Information Display
```javascript
// Bedroom/bathroom display
`${listing.bedrooms} bed${listing.bedrooms > 1 ? 's' : ''}, ${listing.bathrooms} bath${listing.bathrooms > 1 ? 's' : ''}`

// Area display (with unit)
`${listing.sqm} m²`

// Price display (for sale)
listing.price ? `€${listing.price.toLocaleString()} sale` : null

// Price display (for rent)
listing.rent_price ? `€${listing.rent_price.toLocaleString()}/month` : null
```

### Example Listing Object
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "city": "Bucharest",
  "bedrooms": 2,
  "bathrooms": 2,
  "sqm": 95,
  "price": 250000,
  "rent_price": 1200,
  "available_for_sale": true,
  "available_for_rent": false,
  "construction_status": "completed",
  "address": "Str. Mihail Eminescu 42, Bucharest",
  "description": "Modern 2-bedroom apartment in the heart of Bucharest...",
  "nearby_amenities": ["metro station", "supermarket", "park", "gym"],
  "listing_url": "https://example.com/listings/123",
  "image_urls": ["https://images.unsplash.com/..."]
}
```

### UI Component Updates
- **Bathrooms**: Display as integer (e.g., "2 baths" not "2.5 baths")
- **Area**: Always append " m²" unit
- **Prices**: Format with locale-specific thousands separators, prefix with "€"
- **Rent**: Always show as "€X/month" or "€X per month"

## Data Validation Rules

When inserting or updating listings, ensure:

- `bathrooms`: Integer between 1 and 5 (typically)
- `sqm`: Integer between 35 and 400 (realistic apartment sizes)
- `price`: Integer, typically between €45,000 and €1,200,000 (Romanian market)
- `rent_price`: Integer, typically between €250 and €4,000 per month
- `bedrooms`: Integer, typically 0–5 (0 = studio)
- `city`: One of: Bucharest, Cluj-Napoca, Timișoara, Brașov, Constanța, Iași

## Migration Rollback (If Needed)

If you need to revert to the old schema, keep a backup of the old table structure or use Supabase backups. Contact Supabase support if critical data loss occurs.

## Testing

After applying the schema and populating the database, run:

```bash
python scripts/populate_listings.py
```

This will:
1. Load 200 Romanian listings from `database/seed/romania_listings.json`
2. Create the table (if not already created)
3. Delete existing listings
4. Insert all 200 listings in batches
5. Verify the population with row count and sample rows

Expected output:
```
✅ SUCCESS! Database populated with 200 Romanian listings
```

## Related Files

- **Schema Definition**: [database/schema.sql](../database/schema.sql)
- **Migration Script**: [database/migrations/001_european_standards.sql](../database/migrations/001_european_standards.sql)
- **Seed Data Generator**: [scripts/generate_romania_listings.py](../scripts/generate_romania_listings.py)
- **Population Script**: [scripts/populate_listings.py](../scripts/populate_listings.py)
- **Seed Data**: [database/seed/romania_listings.json](../database/seed/romania_listings.json)
