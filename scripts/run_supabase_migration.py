#!/usr/bin/env python3
"""
Run full Supabase database migration in ordered steps:

STEP 1: DELETE all existing listings
STEP 2: UPDATE schema - add new location columns
STEP 3: CREATE location_hierarchy lookup table
STEP 4: INSERT new 200 listings in batches of 50
STEP 5: VERIFY counts and sample query

Environment variables required (in .env or shell):
- SUPABASE_URL: https://<project-ref>.supabase.co
- SUPABASE_DB_PASSWORD: PostgreSQL database password from Supabase settings

Notes:
- Connects directly to Postgres using psycopg2 with SSL.
- Automatically detects existing columns in `listings` and inserts matching fields from JSON.
- Idempotent ALTER TABLE statements via IF NOT EXISTS.
"""

import json
import os
from pathlib import Path
from typing import List, Dict

import psycopg2
import psycopg2.extras as extras
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

SEED_PATH = Path(__file__).resolve().parent.parent / "database" / "seed" / "romania_listings.json"
MIGRATION_002_PATH = Path(__file__).resolve().parent.parent / "database" / "migrations" / "002_location_hierarchy_lookup.sql"


def get_conn_params():
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL not set")
    if not SUPABASE_DB_PASSWORD:
        raise ValueError("SUPABASE_DB_PASSWORD not set (Supabase Postgres password)")

    # Extract project ref from URL: https://ycfmrloksqrbyfmivpbu.supabase.co
    try:
        project_ref = SUPABASE_URL.split("//")[1].split(".supabase.co")[0]
    except Exception:
        raise ValueError("Invalid SUPABASE_URL format; expected https://<ref>.supabase.co")

    # Try direct DB host first
    direct_host = f"db.{project_ref}.supabase.co"
    direct_user = "postgres"

    return {
        "host": direct_host,
        "port": 5432,
        "dbname": "postgres",
        "user": direct_user,
        "password": SUPABASE_DB_PASSWORD,
        "sslmode": "require",
    }


def connect():
    params = get_conn_params()
    print(f"🔌 Connecting to Supabase Postgres at {params['host']}:5432 (SSL)")
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    return conn


def step_1_delete_all(cursor):
    print("\nSTEP 1: DELETE all existing listings")
    cursor.execute("DELETE FROM listings;")
    print("✓ Deleted all rows from listings")


def step_2_update_schema(cursor):
    print("\nSTEP 2: UPDATE schema - add new location columns")
    sql = """
    ALTER TABLE IF EXISTS listings
        ADD COLUMN IF NOT EXISTS judet VARCHAR(50),
        ADD COLUMN IF NOT EXISTS city_town VARCHAR(100),
        ADD COLUMN IF NOT EXISTS sector INTEGER,
        ADD COLUMN IF NOT EXISTS area_neighborhood VARCHAR(100);

    -- Optional: add helpful indexes
    CREATE INDEX IF NOT EXISTS idx_judet ON listings(judet);
    CREATE INDEX IF NOT EXISTS idx_sector ON listings(sector);
    CREATE INDEX IF NOT EXISTS idx_city_town ON listings(city_town);
    CREATE INDEX IF NOT EXISTS idx_area_neighborhood ON listings(area_neighborhood);
    """
    cursor.execute(sql)
    print("✓ Added columns: judet, city_town, sector, area_neighborhood")


def read_sql_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def step_3_create_location_hierarchy(cursor):
    print("\nSTEP 3: CREATE location_hierarchy lookup table")
    sql = read_sql_file(MIGRATION_002_PATH)
    cursor.execute(sql)
    print("✓ location_hierarchy table created and populated")


def load_seed() -> List[Dict]:
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Seed file must contain a JSON array")
    print(f"✓ Loaded {len(data)} listings from {SEED_PATH}")
    return data


def get_listings_columns(cursor) -> List[str]:
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'listings'
        ORDER BY ordinal_position;
    """)
    cols = [r[0] for r in cursor.fetchall()]
    return cols


def step_4_insert_batches(cursor):
    print("\nSTEP 4: INSERT new 200 listings (batches of 50)")
    listings = load_seed()

    # Determine available columns in the listings table
    cols = get_listings_columns(cursor)

    # Prepare column list for insertion based on seed keys and existing table columns
    # We include a safe subset to avoid errors if some columns are missing
    preferred_cols_order = [
        "id", "judet", "city_town", "sector", "area_neighborhood",
        "address", "city", "state",
        "bedrooms", "bathrooms", "sqm",
        "price", "rent_price",
        "available_for_sale", "available_for_rent",
        "construction_status",
        "nearby_amenities", "description", "neighborhood_description",
        "listing_url", "image_urls",
    ]
    insert_cols = [c for c in preferred_cols_order if c in cols]

    if not insert_cols:
        raise RuntimeError("No matching columns found in listings table for insertion")

    # Convert listings dicts to rows matching insert_cols
    def row_for(item: Dict):
        return [item.get(c, None) for c in insert_cols]

    rows = [row_for(item) for item in listings]

    # Batch insert using execute_values
    batch_size = 50
    total = len(rows)
    for start in range(0, total, batch_size):
        end = start + batch_size
        batch = rows[start:end]
        template = "(" + ", ".join(["%s"] * len(insert_cols)) + ")"
        sql = f"INSERT INTO listings ({', '.join(insert_cols)}) VALUES %s"
        extras.execute_values(cursor, sql, batch, template=template)
        print(f"✓ Inserted batch {start//batch_size + 1} ({len(batch)} rows)")

    print(f"✓ Completed inserts: {total} rows")


def step_5_verify(cursor):
    print("\nSTEP 5: VERIFY")

    cursor.execute("SELECT COUNT(*) FROM listings;")
    listings_count = cursor.fetchone()[0]
    print(f"- Listings count: {listings_count}")

    cursor.execute("SELECT COUNT(*) FROM location_hierarchy;")
    loc_count = cursor.fetchone()[0]
    print(f"- Location hierarchy count: {loc_count}")

    cursor.execute("""
        SELECT id, area_neighborhood, city_town, judet, sector, bedrooms, bathrooms, sqm, price
        FROM listings
        WHERE judet='București' AND sector=2
        ORDER BY price DESC
        LIMIT 3;
    """)
    rows = cursor.fetchall()
    print("- Sample (București, Sector 2, 3 results):")
    for r in rows:
        print(f"  • {r}")


def main():
    print("=" * 70)
    print("RUN FULL SUPABASE MIGRATION (5 STEPS)")
    print("=" * 70)

    try:
        conn = connect()
        cursor = conn.cursor()

        step_1_delete_all(cursor)
        step_2_update_schema(cursor)
        step_3_create_location_hierarchy(cursor)
        step_4_insert_batches(cursor)
        step_5_verify(cursor)

        cursor.close()
        conn.close()
        print("\n✅ Migration complete")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Ensure .env has SUPABASE_URL and SUPABASE_DB_PASSWORD.")


if __name__ == "__main__":
    main()
