#!/usr/bin/env python3
"""
Smart Enrichment & Insert - Romania Listings with Foreign Keys

Workflow:
1. Fetch property_types and partitioning_types for FK lookups
2. Enrich all 200 listings with:
   - property_type_id (based on bedrooms)
   - partitioning_id (weighted random: 60% Detached, 30% Semi, 10% Open)
   - Developer info for under_construction/planned properties
   - High-value amenities based on property quality
3. Batch insert enriched data (50 per batch)
4. Verify and report statistics
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SEED_PATH = Path(__file__).resolve().parent.parent / "database" / "seed" / "romania_listings.json"
BATCH_SIZE = 50

# Developer names (30% One United, 70% others)
PREMIUM_DEVELOPER = "One United Properties"
OTHER_DEVELOPERS = [
    "Nordis Group",
    "Urban Spaces",
    "Eden Capital",
    "Globalworth",
    "Portland Trust",
    "Genesis Property",
    "ARCHI Development",
    "River Development"
]

# High-value Romanian amenities by tier
PREMIUM_AMENITIES = [
    "Centrală Proprie",
    "Încălzire în Pardoseală", 
    "Parcare Subterană",
    "Piscină",
    "Spa & Wellness",
    "Concierge 24/7",
    "Sistem Smart Home",
    "Terasă Panoramică"
]

MID_AMENITIES = [
    "Centrală Proprie",
    "Parcare",
    "Lift",
    "Balcon",
    "Aer Condiționat",
    "Sistem de Securitate",
    "Bucătărie Echipată"
]

BASIC_AMENITIES = [
    "Balcon",
    "Lift",
    "Parcare Exterioară",
    "Zonă Verde",
    "Apropiere Transport Public"
]


def fetch_reference_tables(client: Client) -> Dict:
    """Fetch property_types and partitioning_types to build FK lookup dicts."""
    print("📥 Fetching reference tables...")
    
    # Get property types (use 'slug' for lookup)
    prop_types = client.table("property_types").select("*").execute()
    property_map = {row["slug"]: row["id"] for row in prop_types.data}
    print(f"  ✓ Property types: {list(property_map.keys())}")
    
    # Get partitioning types (use 'slug' for lookup)
    part_types = client.table("partitioning_types").select("*").execute()
    partitioning_map = {row["slug"]: row["id"] for row in part_types.data}
    print(f"  ✓ Partitioning types: {list(partitioning_map.keys())}")
    
    return {
        "property_types": property_map,
        "partitioning_types": partitioning_map
    }


def map_bedrooms_to_property_type(bedrooms: int, property_map: Dict) -> int:
    """Map bedroom count to property_type_id."""
    if bedrooms == 0:
        return property_map.get("studio", property_map.get("apartment-1-room"))
    elif bedrooms == 1:
        return property_map.get("apartment-1-room", property_map.get("studio"))
    elif bedrooms == 2:
        return property_map.get("apartment-2-rooms")
    elif bedrooms == 3:
        return property_map.get("apartment-3-rooms")
    elif bedrooms >= 4:
        return property_map.get("apartment-4-plus")
    else:
        # Default to 2-room
        return property_map.get("apartment-2-rooms")


def assign_partitioning(partitioning_map: Dict) -> int:
    """Weighted random partitioning: 60% Detached, 30% Semi, 10% Open."""
    rand = random.random()
    if rand < 0.60:
        return partitioning_map.get("decomandat", partitioning_map.get("detached"))
    elif rand < 0.90:
        return partitioning_map.get("semidecomandat", partitioning_map.get("semi-detached"))
    else:
        return partitioning_map.get("nedecomandat", partitioning_map.get("open-space"))


def generate_developer_info(area: str, construction_status: str) -> Dict:
    """Generate developer name, project name, and dates for developments."""
    if construction_status not in ["under_construction", "planned"]:
        return {
            "developer_name": None,
            "project_name": None,
            "construction_start_date": None
        }
    
    # 30% chance of premium developer
    if random.random() < 0.30:
        developer = PREMIUM_DEVELOPER
    else:
        developer = random.choice(OTHER_DEVELOPERS)
    
    # Generate project name
    project_templates = [
        f"{area} Residence",
        f"The {area} Tower",
        f"Skyline {area}",
        f"{area} Living",
        f"{area} Plaza",
        f"Grand {area}"
    ]
    project_name = random.choice(project_templates)
    
    # Construction start date: 6-18 months ago
    start_offset = random.randint(180, 540)
    construction_start = datetime.now() - timedelta(days=start_offset)
    
    return {
        "developer_name": developer,
        "project_name": project_name,
        "construction_start_date": construction_start.strftime("%Y-%m-%d")
    }


def enrich_amenities(price: int, sqm: int, sector: int, current_amenities: List[str]) -> List[str]:
    """Add high-value amenities based on property tier."""
    if not current_amenities:
        current_amenities = []
    
    # Determine tier based on price per sqm
    if price and sqm and sqm > 0:
        price_per_sqm = price / sqm
        if price_per_sqm > 2500 or (sector and sector == 1):
            # Premium tier
            extra = random.sample(PREMIUM_AMENITIES, min(4, len(PREMIUM_AMENITIES)))
        elif price_per_sqm > 1500:
            # Mid tier
            extra = random.sample(MID_AMENITIES, min(3, len(MID_AMENITIES)))
        else:
            # Basic tier
            extra = random.sample(BASIC_AMENITIES, min(2, len(BASIC_AMENITIES)))
    else:
        extra = random.sample(MID_AMENITIES, 2)
    
    # Merge with existing, remove duplicates
    enriched = list(set(current_amenities + extra))
    return enriched


def enrich_listing(listing: Dict, ref_tables: Dict) -> Dict:
    """
    Enrich a single listing with:
    - property_type_id
    - partitioning_id
    - developer info (if development)
    - enhanced amenities
    """
    enriched = listing.copy()
    
    # Map property type
    bedrooms = listing.get("bedrooms", 2)
    enriched["property_type_id"] = map_bedrooms_to_property_type(
        bedrooms, ref_tables["property_types"]
    )
    
    # Assign partitioning
    enriched["partitioning_id"] = assign_partitioning(ref_tables["partitioning_types"])
    
    # Generate developer info for developments
    construction_status = listing.get("construction_status", "completed")
    area = listing.get("area_neighborhood", "Central")
    dev_info = generate_developer_info(area, construction_status)
    enriched["developer_name"] = dev_info["developer_name"]
    enriched["project_name"] = dev_info["project_name"]
    enriched["construction_start_date"] = dev_info["construction_start_date"]
    
    # Enrich amenities
    price = listing.get("price", 0)
    sqm = listing.get("sqm", 0)
    sector = listing.get("sector")
    current_amenities = listing.get("nearby_amenities", [])
    enriched["nearby_amenities"] = enrich_amenities(price, sqm, sector, current_amenities)
    
    return enriched


def load_and_enrich(ref_tables: Dict) -> List[Dict]:
    """Load seed data and enrich all 200 listings."""
    print(f"\n📂 Loading seed data from {SEED_PATH.name}...")
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        listings = json.load(f)
    
    print(f"✓ Loaded {len(listings)} listings")
    print("\n🔧 Enriching listings...")
    
    enriched = []
    for idx, listing in enumerate(listings):
        enriched_listing = enrich_listing(listing, ref_tables)
        enriched.append(enriched_listing)
        
        if (idx + 1) % 50 == 0:
            print(f"  ✓ Enriched {idx + 1}/{len(listings)}")
    
    print(f"✓ Enrichment complete: {len(enriched)} listings ready")
    return enriched


def batch_insert(client: Client, listings: List[Dict]) -> Dict:
    """Insert enriched listings in batches of 50."""
    print(f"\n📤 Batch inserting {len(listings)} listings...")
    
    total = len(listings)
    stats = {
        "one_united": 0,
        "decomandat": 0,
        "semi": 0,
        "open": 0,
        "developments": 0
    }
    
    for start in range(0, total, BATCH_SIZE):
        batch = listings[start : start + BATCH_SIZE]
        batch_num = start // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"⏳ Inserting batch {batch_num}/{total_batches} ({len(batch)} rows)...")
        
        # Track stats
        for item in batch:
            if item.get("developer_name") == PREMIUM_DEVELOPER:
                stats["one_united"] += 1
            if item.get("developer_name"):
                stats["developments"] += 1
        
        res = client.table("listings").insert(batch).execute()
        if hasattr(res, "error") and res.error:
            raise RuntimeError(f"Insert error on batch {batch_num}: {res.error}")
        
        print(f"  ✓ Batch {batch_num} inserted")
    
    print(f"✓ Completed inserts: {total} rows")
    return stats


def verify(client: Client, stats: Dict):
    """Verify insertion and print enrichment statistics."""
    print("\n📊 VERIFICATION & STATISTICS")
    print("=" * 70)
    
    # Total count
    res = client.table("listings").select("id").execute()
    total = len(res.data)
    print(f"\n✓ Total listings inserted: {total}")
    
    # Location hierarchy count
    loc = client.table("location_hierarchy").select("id").execute()
    loc_total = len(loc.data)
    print(f"✓ Location hierarchy entries: {loc_total}")
    
    # Developer stats
    print(f"\n🏗️  DEVELOPMENT STATISTICS:")
    print(f"  - One United Properties: {stats['one_united']} listings")
    print(f"  - Other developers: {stats['developments'] - stats['one_united']} listings")
    print(f"  - Total developments: {stats['developments']} listings")
    
    # Partitioning breakdown (query actual data)
    print(f"\n🏠 PARTITIONING BREAKDOWN:")
    
    # Get partitioning IDs
    part_types = client.table("partitioning_types").select("*").execute()
    for part in part_types.data:
        count_res = client.table("listings").select("id").eq("partitioning_id", part["id"]).execute()
        count = len(count_res.data)
        percentage = (count / total * 100) if total > 0 else 0
        part_name = part.get("name_en", part.get("slug", "Unknown"))
        print(f"  - {part_name}: {count} ({percentage:.1f}%)")
    
    # Sample București Sector 2
    print(f"\n📍 SAMPLE (București, Sector 2):")
    sample = (
        client
        .table("listings")
        .select("id, area_neighborhood, bedrooms, bathrooms, sqm, price, developer_name, project_name")
        .eq("judet", "București")
        .eq("sector", 2)
        .order("price", desc=True)
        .limit(3)
        .execute()
    )
    for idx, row in enumerate(sample.data, 1):
        dev_info = f" | Dev: {row['developer_name']}" if row.get('developer_name') else ""
        proj_info = f" | Project: {row['project_name']}" if row.get('project_name') else ""
        print(f"  {idx}. {row['area_neighborhood']} — {row['bedrooms']}bd, {row['bathrooms']}ba, {row['sqm']}m²{dev_info}{proj_info}")


def main():
    print("=" * 70)
    print("SMART ENRICHMENT & INSERT - ROMANIA LISTINGS")
    print("=" * 70)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment")
        return
    
    # Initialize client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Step 1: Fetch reference tables
    ref_tables = fetch_reference_tables(client)
    
    # Step 2: Load and enrich all listings
    enriched_listings = load_and_enrich(ref_tables)
    
    # Step 3: Batch insert
    stats = batch_insert(client, enriched_listings)
    
    # Step 4: Verify
    verify(client, stats)
    
    print("\n" + "=" * 70)
    print("✅ SMART ENRICHMENT & INSERT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
