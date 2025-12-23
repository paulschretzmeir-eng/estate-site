import json
import uuid
import random
from pathlib import Path

random.seed(42)

# Output path
OUT_PATH = Path(__file__).resolve().parent.parent / "database" / "seed" / "romania_listings.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Bucharest + Ilfov location structure (200 total)
LOCATION_PLAN = {
    "București": {
        "total": 140,
        "sectors": {
            1: {
                "count": 23,
                "neighborhoods": [
                    "Aviatorilor", "Aviației", "Băneasa", "Bucureștii Noi", "Chibrit",
                    "Dămăroaia", "Domenii", "Dorobanți", "Floreasca (North)", "Gara de Nord",
                    "Grivița", "Pajura", "Pipera (Bucharest)", "Piața Romană", "Piața Victoriei",
                    "Primăverii", "Sisești", "Străulești", "Domenii", "Cotroceni",
                    "Dorobanți (North)", "Aviatorilor (South)", "Pipera (Central)"
                ]
            },
            2: {
                "count": 23,
                "neighborhoods": [
                    "Andronache", "Baicului", "Colentina", "Floreasca (Main)", "Fundeni",
                    "Gara Obor", "Iancului", "Moșior", "Obor", "Pantelimon",
                    "Petricani", "Pipera (South)", "Ștefan cel Mare", "Tei", "Teiul Doamnei",
                    "Vatra Luminoasă", "Obor (North)", "Colentina (East)", "Tei (North)",
                    "Fundeni (South)", "Floreasca (East)", "Moșior (East)", "Iancului (South)"
                ]
            },
            3: {
                "count": 23,
                "neighborhoods": [
                    "23 August", "Balta Albă", "Centrul Civic", "Centrul Vechi (Lipscani)",
                    "Dristor", "Dudești", "Muncii", "Pallady", "Piața Unirii (East)",
                    "Sălăjan", "Titan", "Universitate", "Vitan", "Dristor (North)",
                    "Dudești (South)", "Titan (West)", "Piața Unirii (Central)", "Muncii (North)",
                    "Obor (South)", "Dristor (East)", "Titan (South)", "Vitan (West)", "Pallady (North)"
                ]
            },
            4: {
                "count": 23,
                "neighborhoods": [
                    "Apărătorii Patriei", "Berceni", "Brâncoveanu", "Eroii Revoluției",
                    "Giurgiului", "Metalurgiei", "Olteniței", "Piața Unirii (South)",
                    "Progresul", "Timpuri Noi", "Tineretului", "Văcărești", "Brâncoveanu (East)",
                    "Olteniței (North)", "Metalurgiei (East)", "Tineretului (West)",
                    "Apărătorii Patriei (North)", "Eroii Revoluției (South)", "Progresul (North)",
                    "Văcărești (East)", "Timpuri Noi (West)", "Giurgiului (South)", "Berceni (North)"
                ]
            },
            5: {
                "count": 24,
                "neighborhoods": [
                    "13 Septembrie", "Antiaeriană", "Cotroceni", "Ferentari", "Ghencea (South)",
                    "Giurgiului (West)", "Mărgeanului", "Panduri", "Piața Unirii (SW/Parliament)",
                    "Rahova", "Sălaj", "Sebastian", "Antiaeriană (East)", "Ferentari (North)",
                    "Cotroceni (East)", "Ghencea (Central)", "Panduri (North)", "Rahova (South)",
                    "Sălaj (West)", "13 Septembrie (East)", "Mărgeanului (North)",
                    "Giurgiului (Central)", "Sebastian (East)", "Antiaeriană (North)"
                ]
            },
            6: {
                "count": 24,
                "neighborhoods": [
                    "Crângași", "Drumul Taberei", "Ghencea (North)", "Giulești", "Grozăvești",
                    "Militari", "Pace", "Regie", "Uverturii", "Virtuții", "Drumul Taberei (West)",
                    "Militari (East)", "Giulești (South)", "Grozăvești (North)", "Crângași (South)",
                    "Pace (East)", "Regie (North)", "Virtuții (West)", "Uverturii (East)",
                    "Ghencea (West)", "Militari (North)", "Drumul Taberei (East)",
                    "Giulești (North)", "Grozăvești (East)"
                ]
            }
        }
    },
    "Ilfov": {
        "total": 60,
        "towns": {
            "Bragadiru": {"count": 5, "neighborhoods": ["Bragadiru"]},
            "Buftea": {"count": 5, "neighborhoods": ["Buftea", "Buciumeni"]},
            "Chitila": {"count": 5, "neighborhoods": ["Chitila", "Rudeni"]},
            "Măgurele": {"count": 5, "neighborhoods": ["Măgurele", "Alunișu", "Dumitrana", "Pruni", "Vârteju"]},
            "Otopeni": {"count": 5, "neighborhoods": ["Otopeni", "Odăile"]},
            "Pantelimon": {"count": 5, "neighborhoods": ["Pantelimon (Town)"]},
            "Popești-Leordeni": {"count": 5, "neighborhoods": ["Popești-Leordeni"]},
            "Voluntari": {"count": 5, "neighborhoods": ["Voluntari", "Pipera (Voluntari)"]},
        },
        "communes": [
            "1 Decembrie", "Afumați", "Balotești", "Berceni (Commune)", "Brănești", "Cernica",
            "Chiajna", "Ciolpani", "Ciorogârla", "Clinceni", "Copăceni", "Corbeanca",
            "Cornetu", "Dărăști-Ilfov", "Dascălu", "Dobroești", "Domnești", "Dragomirești-Vale",
            "Găneasa", "Glina", "Grădiștea", "Gruiu", "Jilava", "Moara Vlăsiei",
            "Mogoșoaia", "Nuci", "Periș", "Petrăchioaia", "Snagov", "Ștefăneștii de Jos",
            "Tunari", "Vidra"
        ]
    }
}

# Pricing tiers by area
PRICING_TIERS = {
    "premium": {
        "areas": ["Pipera", "Floreasca", "Primăverii", "Aviatorilor", "Dorobanți"],
        "sale_range": (250000, 800000),
        "rent_range": (1500, 3500)
    },
    "mid_range": {
        "areas": ["Titan", "Tei", "Colentina", "Voluntari", "Otopeni", "Cotroceni"],
        "sale_range": (120000, 350000),
        "rent_range": (700, 1500)
    },
    "affordable": {
        "areas": ["Militari", "Drumul Taberei", "Ferentari", "Berceni", "Pantelimon", "Chitila", "Buftea"],
        "sale_range": (60000, 180000),
        "rent_range": (300, 800)
    }
}

# Property types
TYPE_BUCKETS = [
    ("Modern Apartment", 0.35),
    ("Renovated Apartment", 0.15),
    ("Older Apartment (Unrenovated)", 0.10),
    ("House/Villa", 0.20),
    ("New Construction Condo", 0.10),
    ("Luxury Penthouse", 0.05),
    ("Studio/Starter Home", 0.05),
]

AMENITIES_URBAN = ["metro station", "supermarket", "park", "school", "shopping mall", "restaurant", "gym", "hospital"]
AMENITIES_SUBURBAN = ["green space", "parking", "quiet area", "family-friendly"]
AMENITIES_LUXURY = ["swimming pool", "spa", "concierge", "rooftop terrace", "smart home"]

def bathrooms_for_bed(bed: int) -> int:
    """Return integer bathrooms based on bedrooms."""
    if bed == 0:
        return 1
    elif bed == 1:
        return 1
    elif bed == 2:
        return 2
    elif bed == 3:
        return 2 if random.random() < 0.5 else 3
    else:  # 4+
        return 3 if random.random() < 0.6 else 4
    return 1

def sqm_for_apartment(bed: int) -> int:
    """Generate realistic square meters."""
    ranges = {
        0: (35, 55),
        1: (50, 75),
        2: (75, 110),
        3: (100, 140),
        4: (130, 170),
        5: (160, 220),
    }
    bed_key = min(bed, 5)
    low, high = ranges[bed_key]
    return random.randint(low, high)

def get_pricing_tier(area: str) -> dict:
    """Get pricing tier for an area."""
    for tier_name, tier_data in PRICING_TIERS.items():
        if any(a.lower() in area.lower() for a in tier_data["areas"]):
            return tier_data
    # Default to mid-range
    return PRICING_TIERS["mid_range"]

def sale_price_for(area: str, bed: int, luxury: bool, under_construction=False) -> int:
    """Generate realistic sale price."""
    tier = get_pricing_tier(area)
    low, high = tier["sale_range"]
    factor = 1.0 + (bed * 0.15)
    if luxury:
        factor *= 1.4
    price = int(random.randint(low, high) * min(factor, 2.0))
    if under_construction:
        disc = random.uniform(0.15, 0.25)
        price = int(price * (1.0 - disc))
    return max(45000, min(price, 1200000))

def rent_price_for(area: str, bed: int, luxury: bool) -> int:
    """Generate realistic monthly rent."""
    tier = get_pricing_tier(area)
    low, high = tier["rent_range"]
    factor = 1.0 + (bed * 0.20)
    if luxury:
        factor *= 1.3
    rent = int(random.randint(low, high) * min(factor, 2.0))
    return max(250, min(rent, 4000))

def pick_amenities(area: str) -> list:
    """Pick amenities based on area."""
    amens = list(random.sample(AMENITIES_URBAN, k=random.randint(3, 5)))
    if any(p in area.lower() for p in ["pipera", "primăverii", "dorobanți", "aviatorilor"]):
        amens += random.sample(AMENITIES_SUBURBAN, k=random.randint(1, 2))
    if "villa" in area.lower() or "luxury" in area.lower():
        amens += random.sample(AMENITIES_LUXURY, k=random.randint(1, 3))
    return sorted(set(amens))

def assign_types(total: int) -> list:
    """Create a shuffled list of property types."""
    buckets = []
    remaining = total
    for name, pct in TYPE_BUCKETS[:-1]:
        cnt = int(round(total * pct))
        buckets += [name] * cnt
        remaining -= cnt
    last_name = TYPE_BUCKETS[-1][0]
    buckets += [last_name] * remaining
    random.shuffle(buckets)
    return buckets

def generate_listings() -> list:
    """Generate all 200 listings with new location hierarchy."""
    listings = []
    type_pool = assign_types(200)
    
    # Transaction mix
    trans_pool = (["sale_completed"] * 120 + ["sale_under_construction"] * 20 + ["rent"] * 60)
    random.shuffle(trans_pool)
    
    # Bedroom distribution
    bedroom_pool = (
        [0] * 10 + [1] * 30 + [2] * 80 + [3] * 50 + [4] * 20 + [5] * 10
    )
    random.shuffle(bedroom_pool)
    
    # Bucharest listings (sectors 1-6)
    for sector_num in range(1, 7):
        sector_conf = LOCATION_PLAN["București"]["sectors"][sector_num]
        for _ in range(sector_conf["count"]):
            bed = bedroom_pool.pop()
            trans = trans_pool.pop()
            ptype = type_pool.pop()
            neighborhood = random.choice(sector_conf["neighborhoods"])
            
            is_luxury = "Luxury" in ptype or "Penthouse" in ptype or ptype == "House/Villa"
            under_cons = (trans == "sale_under_construction")
            
            if trans.startswith("sale"):
                price = sale_price_for(neighborhood, bed, is_luxury, under_cons)
                rent_price = None
                avail_sale = True
                avail_rent = False
                status = "under_construction" if under_cons else "completed"
            else:
                price = None
                rent_price = rent_price_for(neighborhood, bed, is_luxury)
                avail_sale = False
                avail_rent = True
                status = "completed"
            
            listing = {
                "id": str(uuid.uuid4()),
                "judet": "București",
                "city_town": "București",
                "sector": sector_num,
                "area_neighborhood": neighborhood,
                "address": f"Str. {neighborhood} {random.randint(1, 200)}, Sector {sector_num}, București",
                "city": "București",
                "state": "București",
                "bedrooms": bed if bed <= 5 else 5,
                "bathrooms": bathrooms_for_bed(bed),
                "sqm": sqm_for_apartment(bed),
                "price": price,
                "rent_price": rent_price,
                "available_for_sale": avail_sale,
                "available_for_rent": avail_rent,
                "construction_status": status,
                "nearby_amenities": pick_amenities(neighborhood),
                "description": f"Located in {neighborhood}, Sector {sector_num}, București. {ptype.lower()} with modern finishes.",
                "neighborhood_description": f"Vibrant neighborhood near {neighborhood}.",
                "listing_url": f"https://example.com/listings/{uuid.uuid4().hex[:8]}",
                "image_urls": [f"https://images.unsplash.com/photo-{uuid.uuid4().hex[:16]}" for _ in range(random.randint(3, 5))],
            }
            listings.append(listing)
    
    # Ilfov listings (towns + communes)
    ilfov_conf = LOCATION_PLAN["Ilfov"]
    
    # Towns (40 listings)
    for town_name, town_conf in ilfov_conf["towns"].items():
        for _ in range(town_conf["count"]):
            bed = bedroom_pool.pop()
            trans = trans_pool.pop()
            ptype = type_pool.pop()
            neighborhood = random.choice(town_conf["neighborhoods"])
            
            is_luxury = "Luxury" in ptype or "Penthouse" in ptype or ptype == "House/Villa"
            under_cons = (trans == "sale_under_construction")
            
            if trans.startswith("sale"):
                price = sale_price_for(neighborhood, bed, is_luxury, under_cons)
                rent_price = None
                avail_sale = True
                avail_rent = False
                status = "under_construction" if under_cons else "completed"
            else:
                price = None
                rent_price = rent_price_for(neighborhood, bed, is_luxury)
                avail_sale = False
                avail_rent = True
                status = "completed"
            
            listing = {
                "id": str(uuid.uuid4()),
                "judet": "Ilfov",
                "city_town": town_name,
                "sector": None,
                "area_neighborhood": neighborhood,
                "address": f"Str. {neighborhood} {random.randint(1, 200)}, {town_name}, Ilfov",
                "city": town_name,
                "state": "Ilfov",
                "bedrooms": bed if bed <= 5 else 5,
                "bathrooms": bathrooms_for_bed(bed),
                "sqm": sqm_for_apartment(bed),
                "price": price,
                "rent_price": rent_price,
                "available_for_sale": avail_sale,
                "available_for_rent": avail_rent,
                "construction_status": status,
                "nearby_amenities": pick_amenities(neighborhood),
                "description": f"Located in {neighborhood}, {town_name}, Ilfov. {ptype.lower()} with convenient access.",
                "neighborhood_description": f"Suburban area near {neighborhood}.",
                "listing_url": f"https://example.com/listings/{uuid.uuid4().hex[:8]}",
                "image_urls": [f"https://images.unsplash.com/photo-{uuid.uuid4().hex[:16]}" for _ in range(random.randint(3, 5))],
            }
            listings.append(listing)
    
    # Communes (20 listings)
    communes = ilfov_conf["communes"]
    for _ in range(20):
        bed = bedroom_pool.pop()
        trans = trans_pool.pop()
        ptype = type_pool.pop()
        commune = random.choice(communes)
        
        is_luxury = "Luxury" in ptype or "Penthouse" in ptype or ptype == "House/Villa"
        under_cons = (trans == "sale_under_construction")
        
        if trans.startswith("sale"):
            price = sale_price_for(commune, bed, is_luxury, under_cons)
            rent_price = None
            avail_sale = True
            avail_rent = False
            status = "under_construction" if under_cons else "completed"
        else:
            price = None
            rent_price = rent_price_for(commune, bed, is_luxury)
            avail_sale = False
            avail_rent = True
            status = "completed"
        
        listing = {
            "id": str(uuid.uuid4()),
            "judet": "Ilfov",
            "city_town": commune,
            "sector": None,
            "area_neighborhood": commune,
            "address": f"Str. {commune} {random.randint(1, 200)}, {commune}, Ilfov",
            "city": commune,
            "state": "Ilfov",
            "bedrooms": bed if bed <= 5 else 5,
            "bathrooms": bathrooms_for_bed(bed),
            "sqm": sqm_for_apartment(bed),
            "price": price,
            "rent_price": rent_price,
            "available_for_sale": avail_sale,
            "available_for_rent": avail_rent,
            "construction_status": status,
            "nearby_amenities": pick_amenities(commune),
            "description": f"Located in {commune}, Ilfov. {ptype.lower()} in a rural/suburban setting.",
            "neighborhood_description": f"Peaceful area in {commune}.",
            "listing_url": f"https://example.com/listings/{uuid.uuid4().hex[:8]}",
            "image_urls": [f"https://images.unsplash.com/photo-{uuid.uuid4().hex[:16]}" for _ in range(random.randint(3, 5))],
        }
        listings.append(listing)
    
    return listings

def main():
    data = generate_listings()
    assert len(data) == 200, f"Expected 200 listings, got {len(data)}"
    
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Wrote {len(data)} listings to {OUT_PATH}")
    
    # Summary
    bucharest_count = sum(1 for l in data if l["judet"] == "București")
    ilfov_count = sum(1 for l in data if l["judet"] == "Ilfov")
    print(f"   - București: {bucharest_count} listings")
    print(f"   - Ilfov: {ilfov_count} listings")
    
    # Sample
    sample = data[0]
    print(f"\n📍 Sample listing:")
    print(f"   {sample['area_neighborhood']}, Sector {sample.get('sector') or 'N/A'}, {sample['city_town']}, {sample['judet']}")
    print(f"   {sample['bedrooms']} bed • {sample['bathrooms']} bath • {sample['sqm']} m²")
    if sample['price']:
        print(f"   €{sample['price']:,} (sale)")
    if sample['rent_price']:
        print(f"   €{sample['rent_price']:,}/month (rent)")

if __name__ == "__main__":
    main()
