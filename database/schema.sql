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
    
    -- Core listing data
    price INTEGER NOT NULL,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    sqft INTEGER,
    property_type VARCHAR(20) DEFAULT 'sale',
    
    -- Location
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

-- 3) Create indexes for fast queries
CREATE INDEX idx_price ON listings(price) WHERE is_active = TRUE;
CREATE INDEX idx_bedrooms ON listings(bedrooms) WHERE is_active = TRUE;
CREATE INDEX idx_city ON listings(city) WHERE is_active = TRUE;
CREATE INDEX idx_state ON listings(state) WHERE is_active = TRUE;
CREATE INDEX idx_property_type ON listings(property_type) WHERE is_active = TRUE;

-- 4) Composite index for common queries
CREATE INDEX idx_location_price ON listings(city, state, price) WHERE is_active = TRUE;

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
