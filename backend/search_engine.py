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
