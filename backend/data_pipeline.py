from dotenv import load_dotenv
load_dotenv()

import os
import random
import uuid
from typing import List, Dict, Any

from database import db

USE_REAL_DATA = os.getenv("USE_REAL_DATA", "false").lower() == "true"

print(f"[data_pipeline] USE_REAL_DATA={USE_REAL_DATA}")


def generate_fake_embedding(dim: int = 1536) -> List[float]:
    """Generate a pseudo-random embedding vector of given dimension.

    In development we produce random floats in [-1,1].
    """
    print("[data_pipeline] Generating fake embedding")
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]


def get_fake_listings() -> List[Dict[str, Any]]:
    """Return 5 realistic-looking fake listings for development/testing."""
    print("[data_pipeline] Creating fake listings")
    examples: List[Dict[str, Any]] = []
    sample_cities = [
        ("Berlin", "BE"),
        ("Munich", "BY"),
        ("Hamburg", "HH"),
        ("Frankfurt", "HE"),
        ("Cologne", "NW"),
        ("Austin", "TX"),
        ("San Francisco", "CA"),
        ("New York", "NY"),
        ("London", "LN"),
    ]

    amenities_by_type = {
        "urban": ["park", "public_transport", "supermarket", "cafe", "gym"],
        "suburban": ["park", "supermarket", "school", "playground", "clinic"],
        "luxury": ["gym", "pool", "spa", "concierge", "parking"],
    }

    for i in range(5):
        city, state = sample_cities[i % len(sample_cities)]
        # vary property type and amenities
        prop_type = random.choice(["urban", "suburban", "luxury"])
        amenities = random.sample(amenities_by_type[prop_type], k=min(3, len(amenities_by_type[prop_type])))

        # mix availability flags with some having both
        sale_flag = random.random() > 0.3
        rent_flag = random.random() > 0.5
        if random.random() > 0.85:
            sale_flag = True
            rent_flag = True

        construction_status = random.choice(["completed", "under_construction", "pre_construction"])

        listing = {
            "id": str(uuid.uuid4()),
            "price": random.randint(200000, 1200000),
            "rent_price": random.randint(800, 5000),
            "bedrooms": random.randint(1, 5),
            "bathrooms": round(random.uniform(1.0, 3.5), 1),
            "sqft": random.randint(40, 250),
            "available_for_sale": sale_flag,
            "available_for_rent": rent_flag,
            "address": f"{random.randint(1,200)} Example St",
            "city": city,
            "state": state,
            "zip_code": f"{random.randint(10000,99999)}",
            "latitude": round(52.0 + random.uniform(-0.5, 0.5), 8),
            "longitude": round(13.0 + random.uniform(-0.5, 0.5), 8),
            "description": f"Charming {random.randint(1,5)}-room property in {city}.",
            "neighborhood_description": f"Quiet residential area near amenities in {city}.",
            "nearby_amenities": amenities,
            "construction_status": construction_status,
            "completion_date": None,
            "developer_name": random.choice(["Acme Developments", "Prime Builders", "Urban Homes"]),
            "project_name": f"Project {random.choice(['A', 'B', 'C', 'D'])}",
            "embedding": generate_fake_embedding(1536),
            "raw_json": {},
            "source_api": "FAKE_DATA",
            "listing_url": f"https://example.com/listing/{i}",
            "image_urls": [f"https://example.com/images/{i}/1.jpg"],
            "is_active": True,
        }
        examples.append(listing)

    return examples


def store_listing(listing_data: Dict[str, Any]) -> bool:
    """Store a single listing into the listings table using Supabase client.

    Returns True on success, False on failure.
    """
    print(f"[data_pipeline] Storing listing {listing_data.get('id')}")
    try:
        # Use the Database.insert_listing convenience method
        res = db.insert_listing(listing_data)

        # Supabase client can return dict-like or object responses depending on client version
        error = None
        if isinstance(res, dict):
            error = res.get("error")
        else:
            error = getattr(res, "error", None)

        if error:
            print(f"[data_pipeline] Supabase returned error for {listing_data.get('id')}: {error}")
            return False

        print(f"[data_pipeline] Stored listing {listing_data.get('id')}")
        return True
    except Exception as e:
        print(f"[data_pipeline] Error storing listing {listing_data.get('id')}: {e}")
        return False


def run_data_pipeline():
    """Fetch listings (fake or real) and store them in the DB."""
    print("[data_pipeline] Running data pipeline")
    if USE_REAL_DATA:
        print("[data_pipeline] USE_REAL_DATA is True but no real source is implemented in dev mode")
        listings = []
    else:
        listings = get_fake_listings()

    stored = 0
    for l in listings:
        if store_listing(l):
            stored += 1

    print(f"[data_pipeline] Pipeline complete. Stored {stored}/{len(listings)} listings")


if __name__ == "__main__":
    run_data_pipeline()
