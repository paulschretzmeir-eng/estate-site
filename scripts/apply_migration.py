#!/usr/bin/env python3
"""
Apply European standards migration to Supabase using psycopg2.
Drops old listings table and recreates with new schema.
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load env
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_connection_string():
    """Extract PostgreSQL connection string from Supabase URL."""
    # Supabase URL format: https://project-ref.supabase.co
    # We need to construct: postgresql://postgres:password@project-ref.supabase.co/postgres
    # The project ref is the first part of the URL
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    # Extract project ref from URL: https://ycfmrloksqrbyfmivpbu.supabase.co
    project_ref = SUPABASE_URL.split("//")[1].split(".supabase.co")[0]
    
    # Construct connection string
    # Format: postgresql://postgres:<password>@<project_ref>.supabase.co/postgres
    conn_string = f"postgresql://postgres:{SUPABASE_KEY}@{project_ref}.supabase.co/postgres"
    return conn_string

def apply_migration():
    try:
        conn_string = get_connection_string()
        print("=" * 70)
        print("APPLY MIGRATION: European/Romanian Real Estate Standards")
        print("=" * 70)
        print(f"\n🔌 Connecting to Supabase PostgreSQL...")
        
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        print("✓ Connected to database")
        
        # SQL migration
        sql = """
        -- Drop old table
        DROP TABLE IF EXISTS listings CASCADE;
        
        -- Create new table with European standards
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
        
        -- Indexes for performance
        CREATE INDEX idx_listings_city ON listings(city);
        CREATE INDEX idx_listings_price ON listings(price);
        CREATE INDEX idx_listings_rent_price ON listings(rent_price);
        CREATE INDEX idx_listings_bedrooms ON listings(bedrooms);
        CREATE INDEX idx_listings_available_sale ON listings(available_for_sale);
        CREATE INDEX idx_listings_available_rent ON listings(available_for_rent);
        """
        
        print("\n📝 Applying migration...")
        cursor.execute(sql)
        conn.commit()
        
        print("✓ Migration applied successfully!")
        print("\n✅ Listings table recreated with European standards:")
        print("  - bathrooms: INTEGER (whole rooms, not decimals)")
        print("  - sqm: INTEGER (square meters, not feet)")
        print("  - price/rent_price: INTEGER (EUR)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)
