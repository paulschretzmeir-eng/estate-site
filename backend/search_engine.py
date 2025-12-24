from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import json
import os
import re
from typing import Any, Dict, List

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[search_engine] WARNING: groq package not installed, using fallback regex parsing")

from database import db


USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_CLIENT = None

if GROQ_AVAILABLE and GROQ_API_KEY:
    try:
        GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)
        print("[search_engine] Groq client initialized successfully")
    except Exception as e:
        print(f"[search_engine] Failed to initialize Groq client: {e}")
elif not GROQ_AVAILABLE:
    print("[search_engine] Groq package not available, using fallback regex parsing")
elif not GROQ_API_KEY:
    print("[search_engine] GROQ_API_KEY not set, using fallback regex parsing")


def parse_user_query(prompt: str) -> Dict[str, Any]:
    """Extract filters using Groq/Llama 3.3 70B for multilingual parsing.

    Returns a dict possibly containing: bedrooms, bathrooms, max_price, min_price,
    judet, sector, area_neighborhood, city_town, available_for_sale, available_for_rent,
    construction_status, semantic_keywords.
    """
    if not GROQ_CLIENT:
        print("[search_engine] WARNING: GROQ_API_KEY not configured, using fallback regex")
        return _parse_user_query_fallback(prompt)
    
    try:
        groq_prompt = f"""You are a real estate search filter extractor for the Romanian market (București and Ilfov).

Extract structured filters from the user query. Return ONLY a JSON object with these fields (omit if not mentioned):
- bedrooms (integer)
- bathrooms (integer)
- min_price (integer, EUR)
- max_price (integer, EUR)
- area_neighborhood (string, e.g., "Pipera", "Dorobanți", "Floreasca", "Drumul Taberei")
- sector (integer 1-6 for București)
- judet (string: "București" or "Ilfov")
- city_town (string: specific town/city name)
- sqm_min (integer, minimum square meters)
- sqm_max (integer, maximum square meters)
- available_for_sale (boolean, true if user wants to buy)
- available_for_rent (boolean, true if user wants to rent)
- construction_status (string: "pre_construction", "under_construction", or "completed")
- semantic_keywords (array of strings: amenities like "park", "school", "metro", "gym")

Handle both English and Romanian queries. Convert "k" notation (e.g., "250k" = 250000).
Romanian translations: camere=bedrooms, băi=bathrooms, apartament=apartment, casă=house

User query: {prompt}

Return ONLY the JSON object, no markdown, no explanation."""

        response = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": groq_prompt}],
            temperature=0.1,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        filters = json.loads(content)
        print(f"[search_engine] Groq extracted filters: {filters}")
        return filters
        
    except Exception as e:
        print(f"[search_engine] Groq parsing error: {e}, falling back to regex")
        return _parse_user_query_fallback(prompt)


def _parse_user_query_fallback(prompt: str) -> Dict[str, Any]:
    """Fallback regex-based parsing if Groq is unavailable."""
    filters: Dict[str, Any] = {}
    text = prompt or ""

    m = re.search(r"(\d+)\s*(?:bed|beds|bedroom|bedrooms|camere|camera)", text, re.I)
    if m:
        filters["bedrooms"] = int(m.group(1))

    m = re.search(r"(\d+)\s*(?:bath|baths|bathroom|bathrooms|băi|baie)", text, re.I)
    if m:
        try:
            filters["bathrooms"] = int(m.group(1))
        except ValueError:
            pass

    m = re.search(r"(?:under|<|less than|max|sub)\s*€?\s*(\d+[\d,]*k?)", text, re.I)
    if m:
        price_str = m.group(1).replace(",", "")
        if price_str.endswith("k"):
            filters["max_price"] = int(price_str[:-1]) * 1000
        else:
            filters["max_price"] = int(price_str)

    m = re.search(r"(?:at least|min)\s*€?\s*(\d+[\d,]*k?)", text, re.I)
    if m:
        price_str = m.group(1).replace(",", "")
        if price_str.endswith("k"):
            filters["min_price"] = int(price_str[:-1]) * 1000
        else:
            filters["min_price"] = int(price_str)

    m = re.search(r"sector\s*(\d+)", text, re.I)
    if m:
        sector_num = int(m.group(1))
        if 1 <= sector_num <= 6:
            filters["sector"] = sector_num

    if re.search(r"ilfov", text, re.I):
        filters["judet"] = "Ilfov"
    elif re.search(r"(buchare|bucuresti|bucurești)", text, re.I):
        filters["judet"] = "București"

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

    m = re.search(r"\b(?:in|în)\s+([A-Za-zăîâșțĂÎÂȘȚ\- ]{2,30})\b", text, re.I)
    if m and "area_neighborhood" not in filters:
        filters["city_town"] = m.group(1).strip()

    if re.search(r"for sale|buy|purchase|vânzare|cumpăr", text, re.I):
        filters["available_for_sale"] = True
    if re.search(r"for rent|rent|rental|închiriere|chirie", text, re.I):
        filters["available_for_rent"] = True

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

        # Execute and sort - get more than 15 to check for overflow
        query = query.order("price", desc=False).limit(50)
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
        
        # Return all results (will be limited to 15 in search() function)
        return data

    except Exception as e:
        print(f"[search_engine] Search error: {e}")
        return []


def _get_overflow_suggestions(filters: Dict[str, Any], is_romanian: bool = False) -> str:
    """Analyze missing filters and suggest specific improvements."""
    suggestions = []
    
    # Check for missing price filter
    if not filters.get("max_price") and not filters.get("min_price"):
        if is_romanian:
            suggestions.append("adăugarea unui preț maxim (ex: 'sub 200k EUR')")
        else:
            suggestions.append("adding a price limit (e.g., 'under 200k')")
    
    # Check for missing bedroom filter
    if not filters.get("bedrooms"):
        if is_romanian:
            suggestions.append("specificarea numărului de camere (ex: '2 camere')")
        else:
            suggestions.append("specifying the number of rooms (e.g., '2 bedrooms')")
    
    # Check for missing neighborhood (but has city/judet)
    if not filters.get("area_neighborhood") and (filters.get("judet") or filters.get("city_town")):
        if is_romanian:
            suggestions.append("alegerea unui cartier specific (ex: 'Floreasca', 'Pipera')")
        else:
            suggestions.append("choosing a specific neighborhood (e.g., 'Floreasca', 'Pipera')")
    
    # Check for missing size filter
    if not filters.get("sqm_min") and not filters.get("sqm_max"):
        if is_romanian:
            suggestions.append("specificarea suprafeței minime (ex: 'peste 80 mp')")
        else:
            suggestions.append("specifying a minimum size (e.g., 'over 80 sqm')")
    
    # Combine suggestions
    if not suggestions:
        return ""
    
    if is_romanian:
        if len(suggestions) == 1:
            return suggestions[0]
        elif len(suggestions) == 2:
            return f"{suggestions[0]} sau {suggestions[1]}"
        else:
            return ", ".join(suggestions[:-1]) + f" sau {suggestions[-1]}"
    else:
        if len(suggestions) == 1:
            return suggestions[0]
        elif len(suggestions) == 2:
            return f"{suggestions[0]} or {suggestions[1]}"
        else:
            return ", ".join(suggestions[:-1]) + f", or {suggestions[-1]}"


def generate_ai_response(prompt: str, filters: Dict[str, Any], listings: List[Dict[str, Any]], overflow_count: int = 0, total_matches: int = 0) -> str:
    """Generate natural language response using Groq, matching user's language."""
    if not GROQ_CLIENT:
        return _generate_ai_response_fallback(prompt, filters, listings, overflow_count, total_matches)
    
    if not listings:
        # Use Groq to generate "no results" message in user's language
        try:
            no_results_prompt = f"""The user searched for: "{prompt}"

No properties matched their search. Write a brief, helpful message in the SAME LANGUAGE as their query:
- If English query → English response
- If Romanian query → Romanian response

Suggest they try broadening their search (price range, location, etc.). Keep it conversational and brief (2-3 sentences)."""

            response = GROQ_CLIENT.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": no_results_prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[search_engine] Groq response error: {e}")
            return "No listings matched your query. Try broadening your search."
    
    # Add overflow messaging for 15+ results with smart suggestions
    overflow_suffix = ""
    if overflow_count > 0:
        is_romanian = "romanian" in prompt.lower() or any(word in prompt.lower() for word in ["apartament", "camere", "în"])
        suggestions = _get_overflow_suggestions(filters, is_romanian)
        
        if is_romanian:
            base_msg = f"\n\nAm găsit cele mai bune 15 rezultate din {total_matches} proprietăți găsite. Mai am {overflow_count} proprietăți disponibile."
            if suggestions:
                overflow_suffix = base_msg + f" Pentru a restrânge căutarea, încercați {suggestions}."
            else:
                overflow_suffix = base_msg + " Doriți să le vedeți pe celelalte?"
        else:
            base_msg = f"\n\nI've found the 15 best matches out of {total_matches} properties, but I have {overflow_count} more."
            if suggestions:
                overflow_suffix = base_msg + f" To narrow this down, try {suggestions}."
            else:
                overflow_suffix = base_msg + " Would you like to see the others?"
    
    try:
        # Format listings for Groq
        listings_text = ""
        for idx, r in enumerate(listings, 1):
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
            dev = r.get("developer_name")
            proj = r.get("project_name")
            
            line = f"{idx}. {location} — {beds} bd, {baths} ba, {sqm}m²"
            if price is not None:
                line += f" — €{int(price):,}"
            if dev:
                line += f" | Dev: {dev}"
            if proj:
                line += f" | Project: {proj}"
            listings_text += line + "\n"
        
        groq_prompt = f"""You are a helpful real estate assistant for the Romanian market.

The user asked: "{prompt}"

Here are the matching properties:
{listings_text}

Write a natural, conversational response presenting these properties. CRITICAL RULES:
- Respond in the SAME LANGUAGE as the user's query
- If query was in English → respond in English
- If query was in Romanian → respond in Romanian  
- If query was mixed → use Romanian
- Use proper real estate terminology for that language
- Mention 2-3 top properties naturally
- Keep it brief and professional (3-4 sentences)
- Include key details: location, size, price

Response:"""

        response = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": groq_prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip() + overflow_suffix
        
    except Exception as e:
        print(f"[search_engine] Groq response generation error: {e}")
        return _generate_ai_response_fallback(prompt, filters, listings)


def _generate_ai_response_fallback(prompt: str, filters: Dict[str, Any], listings: List[Dict[str, Any]], overflow_count: int = 0, total_matches: int = 0) -> str:
    """Fallback template-based response if Groq is unavailable."""
    if not listings:
        return "No listings matched your query. Try broadening price range or removing strict filters."

    # Build overflow message with smart suggestions
    overflow_msg = ""
    if overflow_count > 0:
        is_romanian = "romanian" in prompt.lower() or any(word in prompt.lower() for word in ["apartament", "camere", "în"])
        suggestions = _get_overflow_suggestions(filters, is_romanian)
        
        if is_romanian:
            base_msg = f"\n\nAm găsit cele mai bune 15 rezultate din {total_matches} proprietăți. Mai am {overflow_count} disponibile."
            if suggestions:
                overflow_msg = base_msg + f" Pentru a restrânge căutarea, încercați {suggestions}."
            else:
                overflow_msg = base_msg + " Doriți să le vedeți pe celelalte?"
        else:
            base_msg = f"\n\nI've found the 15 best matches out of {total_matches} properties, but I have {overflow_count} more."
            if suggestions:
                overflow_msg = base_msg + f" To narrow this down, try {suggestions}."
            else:
                overflow_msg = base_msg + " Would you like to see the others?"

    parts = [f"I found {len(listings)} listings matching your filters:\n"]
    for r in listings:
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
    return "\n".join(parts) + overflow_msg


def search(user_prompt: str) -> Dict[str, Any]:
    filters = parse_user_query(user_prompt)
    all_results = hybrid_search(filters)
    
    # Enforce Top 15 limit
    total_matches = len(all_results)
    top_15 = all_results[:15]
    overflow_count = max(0, total_matches - 15)
    
    # Generate AI response with overflow messaging
    text = generate_ai_response(user_prompt, filters, top_15, overflow_count, total_matches)
    
    return {
        "filters": filters,
        "results": top_15,
        "response": text,
        "total_matches": total_matches,
        "showing": len(top_15)
    }


if __name__ == "__main__":
    print(search("2 bedroom apartment under 800000 in Berlin for sale near park"))
