import json
import uuid
import random
from pathlib import Path

random.seed(42)

# Output path
OUT_PATH = Path(__file__).resolve().parent.parent / "database" / "seed" / "romania_listings.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# City and neighborhood quotas
CITY_PLAN = {
    "Bucharest": {
        "count": 80,
        "neighborhoods": [
            "Pipera","Herastrau","Baneasa","Floreasca","Obor","Unirii","Drumul Taberei","Militari","Titan","Vitan",
            "Cotroceni","Dorobanti","Primaverii","Aviatorilor","Romana","Cismigiu","Stefan cel Mare","Colentina","Pantelimon","Tei"
        ]
    },
    "Cluj-Napoca": {
        "count": 40,
        "neighborhoods": [
            "Centru","Manastur","Zorilor","Gheorgheni","Marasti","Someseni","Grigorescu","Andrei Muresanu","Europa","Buna Ziua"
        ]
    },
    "Timișoara": {
        "count": 30,
        "neighborhoods": [
            "Centru","Fabric","Iosefin","Complexul Studentesc","Circumvalatiunii","Torontalului","Sagului","Fratelia","Mehala","Ciarda Rosie"
        ]
    },
    "Brașov": {
        "count": 25,
        "neighborhoods": [
            "Centru","Tractorul","Astra","Bartolomeu","Schei","Noua","Darste","Stupini","Sacele"
        ]
    },
    "Constanța": {
        "count": 15,
        "neighborhoods": [
            "Centru","Mamaia","Tomis Nord","Tomis Sud","Tomis III","Palazu Mare","Compozitorilor"
        ]
    },
    "Iași": {
        "count": 10,
        "neighborhoods": [
            "Centru","Tatarasi","Pacurari","Copou","Alexandru cel Bun"
        ]
    },
}

# Bedroom distribution (exact counts)
BEDROOM_PLAN = {
    0: 10,   # studio
    1: 30,
    2: 80,
    3: 50,
    4: 20,
    5: 10,   # 5+ treated as 5
}

# Transaction type distribution
TRANS_PLAN = {
    "sale_completed": 120,
    "sale_under_construction": 20,
    "rent": 60,
}

# Property type tags for titles/descriptions (no dedicated field in schema)
TYPE_BUCKETS = [
    ("Modern Apartment", 0.35),
    ("Renovated Apartment", 0.15),
    ("Older Apartment (Unrenovated)", 0.10),
    ("House/Villa", 0.20),
    ("New Construction Condo", 0.10),
    ("Luxury Penthouse", 0.05),
    ("Studio/Starter Home", 0.05),
]

AMENITIES_URBAN = ["metro station","supermarket","park","school","shopping mall","restaurant","gym","hospital"]
AMENITIES_SUBURB = ["green space","parking","quiet area","family-friendly"]
AMENITIES_LUX = ["swimming pool","spa","concierge","rooftop terrace","smart home"]

IMAGE_KEYWORDS = [
    "apartment interior","modern kitchen","living room","balcony view","bedroom","Romanian architecture","luxury home"
]

def pick_images(n: int) -> list:
    # Use deterministic pseudo IDs for Unsplash-style URLs
    imgs = []
    for _ in range(n):
        token = uuid.uuid4().hex[:16]
        imgs.append(f"https://images.unsplash.com/photo-{token}")
    return imgs

def make_address(city: str, neighborhood: str) -> str:
    street_names = ["Str. Mihai Eminescu", "Str. Iuliu Maniu", "Bd. Unirii", "Str. Kogălniceanu", "Str. Carol I", "Bd. Iuliu Hațieganu"]
    nr = random.randint(1, 200)
    return f"{random.choice(street_names)} {nr}, {neighborhood}"

def bathrooms_for_bed(bed: int) -> float:
    base = 1.0 if bed <= 1 else 1.5 if bed == 2 else 2.0 if bed == 3 else 2.5 if bed == 4 else 3.0
    # add 0.0 or 0.5 randomly
    return round(base + random.choice([0.0, 0.5]), 1)

def sale_price_for(city: str, bed: int, luxury: bool, under_construction_discount=False) -> int:
    # Base ranges by city tier
    city_tier = {
        "Bucharest": (70000, 1200000),
        "Cluj-Napoca": (60000, 800000),
        "Timișoara": (55000, 700000),
        "Brașov": (55000, 700000),
        "Constanța": (50000, 650000),
        "Iași": (45000, 600000),
    }[city]
    low, high = city_tier
    # Adjust by bedrooms
    factor = 1.0 + (bed * 0.15)
    if luxury:
        factor *= 1.4
    price = int(random.randint(low, high) * min(factor, 2.0))
    # Under construction discount
    if under_construction_discount:
        disc = random.uniform(0.15, 0.25)
        price = int(price * (1.0 - disc))
    return max(45000, min(price, 1200000))

def rent_price_for(city: str, bed: int, luxury: bool) -> int:
    # Base rent ranges by city tier
    city_tier = {
        "Bucharest": (350, 4000),
        "Cluj-Napoca": (300, 3500),
        "Timișoara": (280, 2500),
        "Brașov": (280, 2500),
        "Constanța": (300, 3000),
        "Iași": (250, 2200),
    }[city]
    low, high = city_tier
    factor = 1.0 + (bed * 0.20)
    if luxury:
        factor *= 1.3
    rent = int(random.randint(low, high) * min(factor, 2.0))
    return max(250, min(rent, 4000))

def desc_for(ptype: str, bed: int, neighborhood: str, city: str) -> str:
    lines = [
        f"Located in {neighborhood}, {city}, this {ptype.lower()} offers a balanced mix of comfort and accessibility.",
        "Bright living spaces, well-appointed finishes, and convenient access to public transport and local amenities.",
        "Ideal for modern urban living, with thoughtful layout and quality materials throughout.",
        "Nearby parks, schools, and shopping options make this property a great fit for families and professionals alike.",
        "Move-in ready and available with flexible viewing times.",
    ]
    random.shuffle(lines)
    return " ".join(lines[:4])

def pick_amenities(ptype: str, neighborhood: str) -> list:
    amens = []
    amens += random.sample(AMENITIES_URBAN, k=random.randint(3, 5))
    if neighborhood in ["Pipera","Baneasa","Primaverii","Aviatorilor","Dorobanti","Cotroceni","Andrei Muresanu","Europa","Buna Ziua"]:
        amens += random.sample(AMENITIES_SUBURB, k=random.randint(1, 2))
    if "Luxury" in ptype or "Penthouse" in ptype or "House/Villa" in ptype:
        lux_add = random.sample(AMENITIES_LUX, k=random.randint(1, 3))
        amens += lux_add
    # dedupe
    return sorted(set(amens))

def assign_types(total: int) -> list:
    # Create a list of property types with counts based on percentages
    buckets = []
    remaining = total
    for name, pct in TYPE_BUCKETS[:-1]:
        cnt = int(round(total * pct))
        buckets += [name] * cnt
        remaining -= cnt
    # last bucket gets the remainder
    last_name = TYPE_BUCKETS[-1][0]
    buckets += [last_name] * remaining
    random.shuffle(buckets)
    return buckets

def generate_listings() -> list:
    total = sum(v["count"] for v in CITY_PLAN.values())
    assert total == 200

    # Prepare bedroom pool
    bedroom_pool = []
    for bed, cnt in BEDROOM_PLAN.items():
        bedroom_pool += [bed] * cnt
    random.shuffle(bedroom_pool)

    # Prepare transaction pool
    trans_pool = (["sale_completed"] * TRANS_PLAN["sale_completed"] +
                  ["sale_under_construction"] * TRANS_PLAN["sale_under_construction"] +
                  ["rent"] * TRANS_PLAN["rent"])
    random.shuffle(trans_pool)

    # Property type tags
    type_pool = assign_types(total)

    listings = []
    idx = 0
    for city, conf in CITY_PLAN.items():
        count = conf["count"]
        neighborhoods = conf["neighborhoods"]
        for i in range(count):
            bed = bedroom_pool.pop()
            trans = trans_pool.pop()
            ptype = type_pool.pop()
            nbhd = random.choice(neighborhoods)

            is_lux = ("Luxury" in ptype) or ("Penthouse" in ptype) or (ptype == "House/Villa")
            under_cons = (trans == "sale_under_construction")

            if trans.startswith("sale"):
                price = sale_price_for(city, bed, is_lux, under_construction_discount=under_cons)
                rent_price = None
                available_for_sale = True
                available_for_rent = False
                status = "under_construction" if under_cons else "completed"
            else:
                price = None
                rent_price = rent_price_for(city, bed, is_lux)
                available_for_sale = False
                available_for_rent = True
                status = "completed"

            desc = desc_for(ptype, bed, nbhd, city)
            address = make_address(city, nbhd)
            images = pick_images(random.randint(3, 5))
            amenities = pick_amenities(ptype, nbhd)

            item = {
                "id": str(uuid.uuid4()),
                "description": desc,
                "city": city,
                "address": address,
                "bedrooms": bed if bed <= 5 else 5,
                "bathrooms": bathrooms_for_bed(bed),
                "price": price,
                "rent_price": rent_price,
                "available_for_sale": available_for_sale,
                "available_for_rent": available_for_rent,
                "construction_status": status,
                "nearby_amenities": amenities,
                "listing_url": f"https://example.com/listings/{idx}",
                "image_urls": images,
            }
            listings.append(item)
            idx += 1

    # Sanity checks
    assert len(listings) == 200
    return listings


def main():
    data = generate_listings()
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(data)} listings to {OUT_PATH}")


if __name__ == "__main__":
    main()
