from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
import re
from typing import Any, Dict, List

from database import db


USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"


def parse_user_query(prompt: str) -> Dict[str, Any]:
    """Extract simple filters from a natural language prompt.

    Returns a dict possibly containing: bedrooms, bathrooms, max_price, min_price,
    city, available_for_sale, available_for_rent, construction_status, semantic_keywords.
    """
    filters: Dict[str, Any] = {}
    text = prompt or ""

    m = re.search(r"(\d+)\s*(?:bed|beds|bedroom|bedrooms)", text, re.I)
    if m:
        filters["bedrooms"] = int(m.group(1))

    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:bath|baths|bathroom|bathrooms)", text, re.I)
    if m:
        try:
            filters["bathrooms"] = float(m.group(1))
        except ValueError:
            pass

    m = re.search(r"(?:under|<|less than|max)\s*\$?(\d+[\d,]*)", text, re.I)
    if m:
        filters["max_price"] = int(m.group(1).replace(",", ""))
    else:
        m2 = re.search(r"\$\s*(\d+[\d,]*)", text)
        if m2:
            filters["max_price"] = int(m2.group(1).replace(",", ""))

    m = re.search(r"(?:at least|min)\s*\$?(\d+[\d,]*)", text, re.I)
    if m:
        filters["min_price"] = int(m.group(1).replace(",", ""))

    m = re.search(r"\bin\s+([A-Za-z\- ]{2,30})\b", text, re.I)
    if m:
        filters["city"] = m.group(1).strip()

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

    m = re.search(r"(?:near|around)\s+([A-Za-z\- ]{2,30})", text, re.I)
    if m and not filters.get("city"):
        filters["city"] = m.group(1).strip()

    return filters


def hybrid_search(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run a structured search via Supabase and return a list of dicts."""
    try:
        client = db.get_cursor()
        query = client.table("listings").select("*")

        query = query.eq("is_active", True)

        if filters.get("max_price") is not None:
            query = query.lte("price", filters["max_price"])
        if filters.get("min_price") is not None:
            query = query.gte("price", filters["min_price"])
        if filters.get("bedrooms") is not None:
            query = query.gte("bedrooms", filters["bedrooms"])
        if filters.get("bathrooms") is not None:
            query = query.gte("bathrooms", filters["bathrooms"])
        if filters.get("city"):
            query = query.ilike("city", filters["city"].strip())
        if filters.get("available_for_sale") is True:
            query = query.eq("available_for_sale", True)
        if filters.get("available_for_rent") is True:
            query = query.eq("available_for_rent", True)
        if filters.get("construction_status"):
            query = query.eq("construction_status", filters["construction_status"])

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
    """Return a user-friendly summary of listings."""
    if USE_REAL_AI:
        return "(AI response not implemented)"

    if not listings:
        return (
            "No listings matched your query. "
            "Try broadening price range or removing strict filters."
        )

    parts = [f"I found {len(listings)} listings matching your filters:\n"]
    for r in listings:
        city = r.get("city") or "Unknown"
        beds = r.get("bedrooms") or "-"
        baths = r.get("bathrooms") or "-"
        price = r.get("price")
        rent = r.get("rent_price")
        line = f"• {city} — {beds} bd • {baths} ba"
        if price is not None:
            try:
                line += f" • {int(price):,} EUR (sale)"
            except Exception:
                line += f" • {price} EUR (sale)"
        if rent is not None:
            try:
                line += f" • {int(rent):,} EUR/month (rent)"
            except Exception:
                line += f" • {rent} EUR/month (rent)"
        parts.append(line)
    return "\n\n".join(parts)


def search(user_prompt: str) -> Dict[str, Any]:
    filters = parse_user_query(user_prompt)
    results = hybrid_search(filters)
    text = generate_ai_response(user_prompt, filters, results)
    return {"filters": filters, "results": results, "response": text}


if __name__ == "__main__":
    print(search("2 bedroom apartment under 800000 in Berlin for sale near park"))
