#!/usr/bin/env python3
"""
Populate Supabase listings table with Romanian residential property listings.

Steps:
1. Load 200 Romanian listings from database/seed/romania_listings.json
2. Connect to Supabase
3. CREATE table if it doesn't exist (with new European standards schema)
4. DELETE all rows from listings table
5. Batch insert the 200 listings
6. Verify: count rows and log 2 sample rows
"""

import json
import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SEED_PATH = Path(__file__).resolve().parent.parent / "database" / "seed" / "romania_listings.json"
BATCH_SIZE = 50


def load_listings():
    """Load the 200 Romanian listings from seed JSON."""
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✓ Loaded {len(data)} listings from {SEED_PATH}")
    return data


def ensure_schema(client):
    """Create listings table if it doesn't exist (with new European standards schema)."""
    print("⏳ Ensuring table schema exists...")
    try:
        # Try to query the table - if it fails, create it
        client.table("listings").select("id").limit(1).execute()
        print("✓ Listings table already exists")
    except Exception as e:
        print(f"⚠️  Table doesn't exist or error: {e}")
        print("📝 Creating listings table with European standards schema...")
        
        # Use RPC to execute raw SQL - check if RPC exists
        try:
            # Try using the SQL migration as an RPC call
            sql = """
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
            """
            # Try executing via RPC if available
            result = client.rpc("sql_exec", {"sql": sql}).execute()
            print("✓ Table created via RPC")
        except Exception as rpc_err:
            print(f"⚠️  RPC failed: {rpc_err}")
            print("❌ Cannot auto-create table. Please run the SQL migration manually:")
            print("   1. Go to Supabase Dashboard > SQL Editor")
            print("   2. Open: database/migrations/001_european_standards.sql")
            print("   3. Execute the SQL")
            print("   4. Run this script again")
            raise


def delete_all(client):
    """Delete all rows from listings table."""
    print("⏳ Deleting all existing listings from database...")
    response = client.table("listings").delete().neq("id", "").execute()
    print(f"✓ Deleted all existing listings")


def batch_insert(client, listings, batch_size=BATCH_SIZE):
    """Insert listings in batches to avoid payload limits."""
    total = len(listings)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = listings[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"⏳ Inserting batch {batch_num}/{total_batches} ({len(batch)} listings)...")
        response = client.table("listings").insert(batch).execute()
        inserted += len(batch)
        print(f"  ✓ Batch {batch_num} inserted ({inserted}/{total})")
    
    print(f"✓ Batch insert complete: {inserted} listings inserted")
    return inserted


def verify(client):
    """Verify the population by checking row count and sampling 2 rows."""
    print("\n📊 Verifying database population...")
    
    # Get total count
    response = client.table("listings").select("id").execute()
    count = len(response.data)
    print(f"✓ Total rows in listings table: {count}")
    
    # Get 2 sample rows (with readable subset of fields)
    sample = client.table("listings").select(
        "id, city, bedrooms, bathrooms, price, rent_price, available_for_sale, available_for_rent, construction_status, address"
    ).limit(2).execute()
    
    print(f"\n📍 Sample rows:")
    for i, row in enumerate(sample.data, 1):
        print(f"\n  Sample {i}:")
        print(f"    ID: {row['id']}")
        print(f"    Address: {row['address']}")
        print(f"    City: {row['city']}")
        print(f"    Bedrooms: {row['bedrooms']}, Bathrooms: {row['bathrooms']}")
        trans_type = ""
        if row['available_for_sale']:
            trans_type += f"Sale: €{row['price']:,}" if row['price'] else "Sale (under construction)"
        if row['available_for_rent']:
            if trans_type:
                trans_type += " | "
            trans_type += f"Rent: €{row['rent_price']}/mo"
        print(f"    Transaction: {trans_type}")
        print(f"    Status: {row['construction_status']}")
    
    print(f"\n✅ Population verification complete!")
    return count


def main():
    print("=" * 70)
    print("POPULATE LISTINGS TABLE WITH ROMANIAN PROPERTIES")
    print("=" * 70)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL or SUPABASE_KEY not set in .env")
        return
    
    print(f"\n🔌 Connecting to Supabase: {SUPABASE_URL}")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("\n🏗️  Step 1: Ensuring table schema...")
    ensure_schema(client)
    
    print("\n📥 Step 2: Loading seed data...")
    listings = load_listings()
    
    print("\n🗑️  Step 3: Clearing existing data...")
    delete_all(client)
    
    print("\n📝 Step 4: Batch inserting new listings...")
    inserted = batch_insert(client, listings, batch_size=BATCH_SIZE)
    
    print("\n🔍 Step 5: Verifying population...")
    total_count = verify(client)
    
    print("\n" + "=" * 70)
    if total_count == 200:
        print("✅ SUCCESS! Database populated with 200 Romanian listings")
    else:
        print(f"⚠️  WARNING: Expected 200 rows but found {total_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
