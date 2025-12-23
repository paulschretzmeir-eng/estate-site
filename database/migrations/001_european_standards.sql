-- ==========================================
-- Migration: European/Romanian Real Estate Standards
-- ==========================================
-- Refactor listings table schema for European standards:
-- 1. bathrooms: DECIMAL(3,1) → INTEGER (rooms, not fractions)
-- 2. sqft → sqm (square meters, not feet)
-- 3. Add EUR currency comment for price fields

-- Strategy: DROP and recreate table to ensure schema consistency
-- Copy this SQL into Supabase SQL Editor and execute

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

-- Create indexes for performance
CREATE INDEX idx_listings_city ON listings(city);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_rent_price ON listings(rent_price);
CREATE INDEX idx_listings_bedrooms ON listings(bedrooms);
CREATE INDEX idx_listings_available_sale ON listings(available_for_sale);
CREATE INDEX idx_listings_available_rent ON listings(available_for_rent);
