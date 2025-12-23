from dotenv import load_dotenv
    if not listings:
        suggestions = [
            "Try broadening your price range.",
            "Try removing specific neighborhood names.",
            "Try 'for rent' or 'for sale' explicitly to refine results.",
        ]
        return (
            "No listings matched your query. "
            + "Here are some suggestions: "
            + " ".join(suggestions)
        )

    parts = [f"I found {len(listings)} listings matching your filters:\n"]

    for r in listings:
        price = r.get("price")
        rent = r.get("rent_price")
        city = r.get("city") or "Unknown"
        beds = r.get("bedrooms") or "-"
        baths = r.get("bathrooms") or "-"
        status = r.get("construction_status") or "unknown"
        amenities = r.get("nearby_amenities") or []

        line = f"• {city} — {beds} bd • {baths} ba"
        if price:
            line += f" • {price:,} EUR (sale)"
        if rent:
            line += f" • {rent:,} EUR/month (rent)"

        line += f"\n  Status: {status}."
        if amenities:
            # show up to 5 amenities
            line += f" Nearby: {', '.join(str(a) for a in amenities[:5])}."

        # include listing URL if available
        if r.get("listing_url"):
            line += f"\n  Link: {r.get('listing_url')}"

        parts.append(line)

    parts.append("\nIf you'd like, I can refine the search or show more details for any listing.")
    return "\n\n".join(parts)
        # Availability flags
    if re.search(r"for sale|buy|purchase", prompt, re.I):
        filters["available_for_sale"] = True
    if re.search(r"for rent|rent|rental", prompt, re.I):
        filters["available_for_rent"] = True

        # Nearby amenities / semantic keywords (array overlap)
        if filters.get("semantic_keywords"):
            keywords = filters.get("semantic_keywords")
            try:
                # prefer overlaps if available
                if hasattr(query, "overlaps"):
                    query = query.overlaps("nearby_amenities", keywords)
                elif hasattr(query, "contains"):
                    query = query.contains("nearby_amenities", keywords)
                else:
                    # fallback: use ilike on neighborhood_description
                    for kw in keywords:
                        query = query.ilike("neighborhood_description", f"%{kw}%")
            except Exception as e:
                print(f"[search_engine] Warning: amenity filter failed: {e}")
    for k in amenity_keywords:
        if re.search(rf"\b{k}\b", prompt, re.I):
            # normalize plural -> singular where appropriate
            norm = k.rstrip("s")
            if norm not in semantic:
                semantic.append(norm)
    if semantic:
        filters["semantic_keywords"] = semantic

    # better location heuristics: 'near X' or 'in X' or 'around X'
    m_loc = re.search(r"(?:in|near|around)\s+([A-Za-z\- ]{2,30})", prompt, re.I)
    if m_loc and not filters.get("city"):
        loc = m_loc.group(1).strip()
        filters["city"] = loc

    print(f"[search_engine] Extracted filters: {filters}")
    return filters


def hybrid_search(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query the database with structured filters and return top 10 results.

    Uses the Supabase client query builder instead of raw SQL/cursor.
    """
    print(f"[search_engine] Running hybrid_search with filters: {filters}")

    try:
        client = db.get_cursor()  # Supabase client
        query = client.table("listings").select("*")

        # Always filter active listings
        query = query.eq("is_active", True)

        # Price range
        if filters.get("max_price") is not None:
            query = query.lte("price", filters["max_price"])
        if filters.get("min_price") is not None:
            query = query.gte("price", filters["min_price"])

        # Bedrooms
        from dotenv import load_dotenv
        load_dotenv()

        import os
        import re
        from typing import Dict, Any, List

        from database import db

        USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"
from dotenv import load_dotenv
load_dotenv()

import os
import re
from typing import Dict, Any, List

from database import db

USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"

print(f"[search_engine] USE_REAL_AI={USE_REAL_AI}")


def parse_user_query(prompt: str) -> Dict[str, Any]:
    """Extract simple filters from a natural language prompt.

    For development (USE_REAL_AI=False) this uses simple regex/keyword matching.
    Extracted filters: bedrooms, max_price, min_price, bathrooms, city,
    available_for_sale, available_for_rent, construction_status, semantic_keywords
    """
    print(f"[search_engine] Parsing prompt: {prompt}")
    filters: Dict[str, Any] = {}

    # bedrooms: look for 'X bed' or 'X bedrooms'
    m = re.search(r"(\d+)\s*(?:bed|beds|bedroom|bedrooms)", prompt, re.I)
    if m:
        filters["bedrooms"] = int(m.group(1))

    # max price: look for 'under 500k' or '$500000' or 'max 500000'
    m2 = re.search(r"(?:under|<|less than|max)\s*\$?(\d+[\d,]*)", prompt, re.I)
    if m2:
        filters["max_price"] = int(m2.group(1).replace(",", ""))
    else:
        m3 = re.search(r"\$\s*(\d+[\d,]*)", prompt)
        if m3:
            filters["max_price"] = int(m3.group(1).replace(",", ""))

    # min price: 'at least 300k' or 'min 300000'
    m4 = re.search(r"(?:at least|min)\s*\$?(\d+[\d,]*)", prompt, re.I)
    if m4:
        filters["min_price"] = int(m4.group(1).replace(",", ""))

    # bathrooms: look for '2 bath' or '2 bathrooms'
    m5 = re.search(r"(\d+(?:\.\d+)?)\s*(?:bath|baths|bathroom|bathrooms)", prompt, re.I)
    if m5:
        try:
            filters["bathrooms"] = float(m5.group(1))
        except ValueError:
            pass

    # city: naive check for 'in CityName'
    m_city = re.search(r"in\s+([A-Za-z\- ]{2,30})", prompt, re.I)
    if m_city:
        filters["city"] = m_city.group(1).strip()

    # availability
    if re.search(r"for sale|buy|purchase", prompt, re.I):
        filters["available_for_sale"] = True
    if re.search(r"for rent|rent|rental", prompt, re.I):
        filters["available_for_rent"] = True

    # construction status
    if re.search(r"new construction|newly built|pre[- ]?construction", prompt, re.I):
        filters["construction_status"] = "pre_construction"
    if re.search(r"under construction|in construction", prompt, re.I):
        filters["construction_status"] = "under_construction"
    if re.search(r"move-in ready|move in ready|completed|ready to move|move-in", prompt, re.I):
        filters["construction_status"] = "completed"

    # nearby amenities keywords (simple keyword extraction)
    amenity_keywords = [
        "park",
        "parks",
        "school",
        "schools",
        "supermarket",
        "grocery",
        "gym",
        "restaurant",
        "cafe",
        "public transport",
        "subway",
        "train",
        "tram",
        "bus",
        "playground",
        "hospital",
        "clinic",
    ]
    semantic: List[str] = []
    for k in amenity_keywords:
        if re.search(rf"\b{k}\b", prompt, re.I):
            norm = k.rstrip("s")
            if norm not in semantic:
                semantic.append(norm)
    if semantic:
        filters["semantic_keywords"] = semantic

    # better location heuristics: 'near X' or 'around X'
    m_loc = re.search(r"(?:in|near|around)\s+([A-Za-z\- ]{2,30})", prompt, re.I)
    if m_loc and not filters.get("city"):
        loc = m_loc.group(1).strip()
        filters["city"] = loc

    print(f"[search_engine] Extracted filters: {filters}")
    return filters


def hybrid_search(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query the database with structured filters and return top 10 results.

    Uses the Supabase client query builder instead of raw SQL/cursor.
    """
    print(f"[search_engine] Running hybrid_search with filters: {filters}")

    try:
        client = db.get_cursor()  # Supabase client
        query = client.table("listings").select("*")

        # Always filter active listings
        query = query.eq("is_active", True)

        # Price range
        if filters.get("max_price") is not None:
            query = query.lte("price", filters["max_price"])
        if filters.get("min_price") is not None:
            query = query.gte("price", filters["min_price"])

        # Bedrooms
        if filters.get("bedrooms") is not None:
            query = query.gte("bedrooms", filters["bedrooms"])

        # Bathrooms
        if filters.get("bathrooms") is not None:
            query = query.gte("bathrooms", filters["bathrooms"])

        # City (case-insensitive). Use ILIKE for fuzzy/case-insensitive match.
        if filters.get("city"):
            city_val = filters["city"].strip()
            # exact case-insensitive match via ILIKE
            query = query.ilike("city", city_val)

        # Availability flags
        if filters.get("available_for_sale") is True:
            query = query.eq("available_for_sale", True)
        if filters.get("available_for_rent") is True:
            query = query.eq("available_for_rent", True)

        # Nearby amenities / semantic keywords (array overlap)
        if filters.get("semantic_keywords"):
            keywords = filters.get("semantic_keywords")
            try:
                # prefer overlaps if available
                if hasattr(query, "overlaps"):
                    query = query.overlaps("nearby_amenities", keywords)
                elif hasattr(query, "contains"):
                    query = query.contains("nearby_amenities", keywords)
                else:
                    # fallback: use ilike on neighborhood_description
                    for kw in keywords:
                        query = query.ilike("neighborhood_description", f"%{kw}%")
            except Exception as e:
                print(f"[search_engine] Warning: amenity filter failed: {e}")

        # Ordering and limit
        query = query.order("price", desc=False).limit(10)

        response = query.execute()

        # Normalize response to a list of dicts
        data = None
        if isinstance(response, dict):
            data = response.get("data") or []
        else:
            data = getattr(response, "data", None) or getattr(response, "body", None) or []

        if data is None:
            print("[search_engine] No data in response")
            return []

        # Ensure list
        if not isinstance(data, list):
            return [data]

        print(f"[search_engine] Found {len(data)} results")
        return data

    except Exception as e:
        print(f"[search_engine] Search error: {e}")
        return []


def generate_ai_response(prompt: str, filters: Dict[str, Any], listings: List[Dict[str, Any]]) -> str:
    """Generate a human-readable response. In dev mode uses a simple template."""
    print("[search_engine] Generating AI response (dev mode)")
    if USE_REAL_AI:
        # Placeholder for real AI call
        return "(AI response not implemented in this template)"

    # Simple formatted response
    if not listings:
        suggestions = [
            "Try broadening your price range.",
            "Try removing specific neighborhood names.",
            "Try 'for rent' or 'for sale' explicitly to refine results.",
        ]
        return (
            "No listings matched your query. "
            + "Here are some suggestions: "
            + " ".join(suggestions)
        )

    parts = [f"I found {len(listings)} listings matching your filters:\n"]

    for r in listings:
        price = r.get("price")
        rent = r.get("rent_price")
        city = r.get("city") or "Unknown"
        beds = r.get("bedrooms") or "-"
        baths = r.get("bathrooms") or "-"
        status = r.get("construction_status") or "unknown"
        amenities = r.get("nearby_amenities") or []

        line = f"• {city} — {beds} bd • {baths} ba"
        if price:
            line += f" • {price:,} EUR (sale)"
        if rent:
            line += f" • {rent:,} EUR/month (rent)"

        line += f"\n  Status: {status}."
        if amenities:
            # show up to 5 amenities
            line += f" Nearby: {', '.join(str(a) for a in amenities[:5])}."

        # include listing URL if available
        if r.get("listing_url"):
            line += f"\n  Link: {r.get('listing_url')}"

        parts.append(line)

    parts.append("\nIf you'd like, I can refine the search or show more details for any listing.")
    return "\n\n".join(parts)


def search(user_prompt: str) -> Dict[str, Any]:
    """Top-level search function: parse -> run -> format response."""
    filters = parse_user_query(user_prompt)
    results = hybrid_search(filters)
    text = generate_ai_response(user_prompt, filters, results)
    return {"filters": filters, "results": results, "response": text}


if __name__ == "__main__":
    print(search("2 bedroom apartment under 800000 in Berlin for sale"))
                parts.append(line)

            parts.append("\nIf you'd like, I can refine the search or show more details for any listing.")
            return "\n\n".join(parts)


        def search(user_prompt: str) -> Dict[str, Any]:
            """Top-level search function: parse -> run -> format response."""
            filters = parse_user_query(user_prompt)
            results = hybrid_search(filters)
            text = generate_ai_response(user_prompt, filters, results)
            return {"filters": filters, "results": results, "response": text}


        if __name__ == "__main__":
            print(search("2 bedroom apartment under 800000 in Berlin for sale"))
