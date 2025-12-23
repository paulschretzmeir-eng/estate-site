-- ==========================================
-- 🏠 HYBRID REAL ESTATE SYSTEM - DATABASE SCHEMA
-- Single optimized table with pgvector
-- ==========================================

-- 1) Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2) Create the main listings table
CREATE TABLE listings (
    -- Primary Key
    id VARCHAR(100) PRIMARY KEY,
    
    -- Core listing data (EUR, Romanian standards)
    price INTEGER,          -- Price in EUR (whole euros)
    rent_price INTEGER,     -- Monthly rent in EUR
    bedrooms INTEGER,
    bathrooms INTEGER,      -- Number of bathroom rooms (integers only, Romanian standard)
    sqm INTEGER,            -- Square meters (NOT square feet; European standard)
    
    -- Property availability
    available_for_sale BOOLEAN DEFAULT FALSE,
    available_for_rent BOOLEAN DEFAULT FALSE,
    
    -- Location (new hierarchy: Bucharest + Ilfov)
    judet VARCHAR(50) NOT NULL,              -- 'București' or 'Ilfov'
    city_town VARCHAR(100) NOT NULL,         -- 'București' or Ilfov town/commune
    sector INTEGER,                          -- 1-6 for București sectors, NULL for Ilfov
    area_neighborhood VARCHAR(100) NOT NULL, -- Specific area: neighborhood, village, or town name
    
    -- Legacy location fields (deprecated, kept for compatibility)
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Descriptions
    description TEXT,
    neighborhood_description TEXT,
    
    -- Amenities (array)
    nearby_amenities TEXT[],
    
    -- Construction/Development Status
    construction_status VARCHAR(50) DEFAULT 'completed',
    completion_date DATE,
    developer_name VARCHAR(200),
    project_name VARCHAR(200),
    
    -- Vector embedding for semantic search
    embedding vector(1536),
    
    -- Full raw data backup
    raw_json JSONB,
    
    -- Metadata
    source_api VARCHAR(50),
    listing_url TEXT,
    image_urls TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 3) Create indexes for fast queries (updated for new location hierarchy)
CREATE INDEX idx_price ON listings(price) WHERE is_active = TRUE;
CREATE INDEX idx_rent_price ON listings(rent_price) WHERE is_active = TRUE;
CREATE INDEX idx_bedrooms ON listings(bedrooms) WHERE is_active = TRUE;
CREATE INDEX idx_judet ON listings(judet) WHERE is_active = TRUE;
CREATE INDEX idx_sector ON listings(sector) WHERE is_active = TRUE;
CREATE INDEX idx_city_town ON listings(city_town) WHERE is_active = TRUE;
CREATE INDEX idx_area_neighborhood ON listings(area_neighborhood) WHERE is_active = TRUE;
CREATE INDEX idx_available_for_sale ON listings(available_for_sale) WHERE is_active = TRUE;
CREATE INDEX idx_available_for_rent ON listings(available_for_rent) WHERE is_active = TRUE;
CREATE INDEX idx_construction_status ON listings(construction_status) WHERE is_active = TRUE;

-- 4) Composite index for common queries (location + price)
CREATE INDEX idx_judet_price ON listings(judet, price) WHERE is_active = TRUE;
CREATE INDEX idx_sector_price ON listings(judet, sector, price) WHERE is_active = TRUE;
CREATE INDEX idx_location_amenity ON listings(judet, city_town, area_neighborhood, price) WHERE is_active = TRUE;

-- 5) GIN index for amenities array search
CREATE INDEX idx_amenities ON listings USING gin(nearby_amenities);

-- 6) Vector similarity index for semantic search
CREATE INDEX idx_embedding ON listings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 7) Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8) Trigger to auto-update updated_at
CREATE TRIGGER update_listings_updated_at 
    BEFORE UPDATE ON listings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
-- ==========================================
-- ✅ Database schema created successfully!
-- ==========================================