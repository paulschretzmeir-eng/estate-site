from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
import re
from typing import Any, Dict, List

from database import db


USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"


def parse_user_query(prompt: str) -> Dict[str, Any]:
    """Extract filters including location hierarchy (judet, sector, area_neighborhood).

    Returns a dict possibly containing: bedrooms, bathrooms, max_price, min_price,
    judet, sector, area_neighborhood, city_town, available_for_sale, available_for_rent,
    construction_status, semantic_keywords.
    """
    filters: Dict[str, Any] = {}
    text = prompt or ""

    m = re.search(r"(\d+)\s*(?:bed|beds|bedroom|bedrooms)", text, re.I)
    if m:
        filters["bedrooms"] = int(m.group(1))

    # Parse bathrooms as integer (schema is int only)
    m = re.search(r"(\d+)\s*(?:bath|baths|bathroom|bathrooms)", text, re.I)
    if m:
        try:
            filters["bathrooms"] = int(m.group(1))
        except ValueError:
            pass

    m = re.search(r"(?:under|<|less than|max)\s*€?\s*(\d+[\d,]*)", text, re.I)
    if m:
        filters["max_price"] = int(m.group(1).replace(",", ""))
    else:
        m2 = re.search(r"€\s*(\d+[\d,]*)", text)
        if m2:
            filters["max_price"] = int(m2.group(1).replace(",", ""))

    m = re.search(r"(?:at least|min)\s*€?\s*(\d+[\d,]*)", text, re.I)
    if m:
        filters["min_price"] = int(m.group(1).replace(",", ""))

    # Parse sector (1-6 for Bucharest)
    m = re.search(r"sector\s*(\d+)", text, re.I)
    if m:
        sector_num = int(m.group(1))
        if 1 <= sector_num <= 6:
            filters["sector"] = sector_num

    # Parse Ilfov or Bucharest (judet)
    if re.search(r"ilfov", text, re.I):
        filters["judet"] = "Ilfov"
    elif re.search(r"(buchare|bucuresti|bucuresti)", text, re.I):
        filters["judet"] = "București"

    # Parse neighborhood/area (Pipera, Floreasca, Voluntari, etc.)
    neighborhoods = [
        "Pipera", "Floreasca", "Primăverii", "Aviatorilor", "Dorobanți", "Titan",
        "Tei", "Colentina", "Voluntari", "Otopeni", "Chitila", "Buftea",
        "Militari", "Drumul Taberei", "Ferentari", "Berceni", "Pantelimon",
        "Cotroceni", "Obor", "Universitate", "Dristor", "Vitan"
    ]
    for nbhood in neighborhoods:
        if re.search(rf"\b{nbhood}\b", text, re.I):
            filters["area_neighborhood"] = nbhood
            break

    # Legacy: parse generic location (will be mapped if possible)
    m = re.search(r"\bin\s+([A-Za-z\- ]{2,30})\b", text, re.I)
    if m and "area_neighborhood" not in filters:
        filters["city_town"] = m.group(1).strip()

    if re.search(r"for sale|buy|purchase", text, re.I):
        filters["available_for_sale"] = True
    if re.search(r"for rent|rent|rental", text, re.I):
        filters["available_for_rent"] = True

    if re.search(r"new construction|newly built|pre[- ]?construction", text, re.I):
        filters["construction_status"] = "pre_construction"
    elif re.search(r"under construction|in construction", text, re.I):
        filters["construction_status"] = "under_construction"
    elif re.search(r"move[- ]?in ready|completed|ready to move", text, re.I):
        filters["construction_status"] = "completed"

    amenity_keywords = [
        "park", "school", "supermarket", "grocery", "gym", "restaurant", "cafe",
        "public transport", "subway", "train", "tram", "bus", "playground",
        "hospital", "clinic",
    ]
    semantic: List[str] = []
    for k in amenity_keywords:
        if re.search(rf"\b{k}\b", text, re.I):
            norm = k.rstrip("s")
            if norm not in semantic:
                semantic.append(norm)
    if semantic:
        filters["semantic_keywords"] = semantic

    return filters


def hybrid_search(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run a structured search via Supabase using new location hierarchy."""
    try:
        client = db.get_cursor()
        query = client.table("listings").select("*")

        query = query.eq("is_active", True)

        # Price filters
        if filters.get("max_price") is not None:
            query = query.lte("price", filters["max_price"])
        if filters.get("min_price") is not None:
            query = query.gte("price", filters["min_price"])

        # Property filters
        if filters.get("bedrooms") is not None:
            query = query.gte("bedrooms", filters["bedrooms"])
        if filters.get("bathrooms") is not None:
            query = query.gte("bathrooms", filters["bathrooms"])

        # Location hierarchy filters (new)
        if filters.get("judet"):
            query = query.eq("judet", filters["judet"])
        if filters.get("sector") is not None:
            query = query.eq("sector", filters["sector"])
        if filters.get("area_neighborhood"):
            query = query.ilike("area_neighborhood", f"%{filters['area_neighborhood'].strip()}%")
        if filters.get("city_town"):
            query = query.ilike("city_town", f"%{filters['city_town'].strip()}%")

        # Transaction type filters
        if filters.get("available_for_sale") is True:
            query = query.eq("available_for_sale", True)
        if filters.get("available_for_rent") is True:
            query = query.eq("available_for_rent", True)

        # Construction status filter
        if filters.get("construction_status"):
            query = query.eq("construction_status", filters["construction_status"])

        # Amenities filter (semantic search)
        if filters.get("semantic_keywords"):
            keywords = filters["semantic_keywords"]
            try:
                if hasattr(query, "overlaps"):
                    query = query.overlaps("nearby_amenities", keywords)
                elif hasattr(query, "contains"):
                    query = query.contains("nearby_amenities", keywords)
                else:
                    for kw in keywords:
                        query = query.ilike("neighborhood_description", f"%{kw}%")
            except Exception:
                pass

        # Execute and sort
        query = query.order("price", desc=False).limit(10)
        response = query.execute()

        data = None
        if isinstance(response, dict):
            data = response.get("data") or []
        else:
            data = getattr(response, "data", None) or getattr(response, "body", None) or []

        if data is None:
            return []
        if not isinstance(data, list):
            return [data]
        return data

    except Exception as e:
        print(f"[search_engine] Search error: {e}")
        return []


def generate_ai_response(prompt: str, filters: Dict[str, Any], listings: List[Dict[str, Any]]) -> str:
    """Return a user-friendly summary of listings with new location format."""
    if USE_REAL_AI:
        return "(AI response not implemented)"

    if not listings:
        return (
            "No listings matched your query. "
            "Try broadening price range or removing strict filters."
        )

    parts = [f"I found {len(listings)} listings matching your filters:\n"]
    for r in listings:
        # Format location using new hierarchy
        judet = r.get("judet") or "Unknown"
        city_town = r.get("city_town") or ""
        sector = r.get("sector")
        area_neighborhood = r.get("area_neighborhood") or ""
        
        if sector:
            location = f"{area_neighborhood}, Sector {sector}, {city_town}"
        else:
            location = f"{area_neighborhood}, {city_town}, {judet}" if area_neighborhood else city_town
        
        beds = r.get("bedrooms") or "-"
        baths = r.get("bathrooms") or "-"
        sqm = r.get("sqm") or "-"
        price = r.get("price")
        rent = r.get("rent_price")
        
        line = f"• {location} — {beds} bd • {baths} ba • {sqm} m²"
        if price is not None:
            try:
                line += f" • €{int(price):,} (sale)"
            except Exception:
                line += f" • €{price} (sale)"
        if rent is not None:
            try:
                line += f" • €{int(rent):,}/mo (rent)"
            except Exception:
                line += f" • €{rent}/mo (rent)"
        parts.append(line)
    return "\n".join(parts)


def search(user_prompt: str) -> Dict[str, Any]:
    filters = parse_user_query(user_prompt)
    results = hybrid_search(filters)
    text = generate_ai_response(user_prompt, filters, results)
    return {"filters": filters, "results": results, "response": text}


if __name__ == "__main__":
    print(search("2 bedroom apartment under 800000 in Berlin for sale near park"))
