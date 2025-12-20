from dotenv import load_dotenv
load_dotenv()

import os
import re
from typing import Dict, Any, List

from .database import db

USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"

print(f"[search_engine] USE_REAL_AI={USE_REAL_AI}")


def parse_user_query(prompt: str) -> Dict[str, Any]:
    """Extract simple filters from a natural language prompt.

    For development (USE_REAL_AI=False) this uses simple regex/keyword matching.
    Extracted filters: bedrooms, max_price, max_rent, city, available_for_sale, available_for_rent
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

    # city: naive check for 'in CityName'
    m4 = re.search(r"in\s+([A-Za-z\- ]{2,30})", prompt, re.I)
    if m4:
        filters["city"] = m4.group(1).strip()

    # availability
    if re.search(r"for sale|buy|purchase", prompt, re.I):
        filters["available_for_sale"] = True
    if re.search(r"for rent|rent|rental", prompt, re.I):
        filters["available_for_rent"] = True

    print(f"[search_engine] Extracted filters: {filters}")
    return filters


def hybrid_search(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query the database with structured filters and return top 10 results.

    This function does not perform vector similarity in dev mode but is ready
    to be extended to include embedding-based retrieval.
    """
    print(f"[search_engine] Running hybrid_search with filters: {filters}")
    sql = "SELECT * FROM listings WHERE is_active = TRUE"
    params: List[Any] = []

    if "max_price" in filters:
        sql += " AND price <= %s"
        params.append(filters["max_price"])
    if "bedrooms" in filters:
        sql += " AND bedrooms >= %s"
        params.append(filters["bedrooms"])
    if "city" in filters:
        sql += " AND LOWER(city) = LOWER(%s)"
        params.append(filters["city"])
    if filters.get("available_for_sale") is True:
        sql += " AND available_for_sale = TRUE"
    if filters.get("available_for_rent") is True:
        sql += " AND available_for_rent = TRUE"

    sql += " ORDER BY price ASC NULLS LAST LIMIT 10"

    try:
        cur = db.get_cursor()
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        print(f"[search_engine] Found {len(rows)} results")
        return rows
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
        return "No listings matched your query."

    parts = [f"Found {len(listings)} listings matching your filters:"]
    for r in listings:
        parts.append(f"- {r.get('id')}: {r.get('city')}, {r.get('price')} EUR, {r.get('bedrooms')} bd, {r.get('bathrooms')} ba")

    return "\n".join(parts)


def search(user_prompt: str) -> Dict[str, Any]:
    """Top-level search function: parse -> run -> format response."""
    filters = parse_user_query(user_prompt)
    results = hybrid_search(filters)
    text = generate_ai_response(user_prompt, filters, results)
    return {"filters": filters, "results": results, "response": text}


if __name__ == "__main__":
    print(search("2 bedroom apartment under 800000 in Berlin for sale"))
