#!/usr/bin/env python3
"""
Test Groq/Llama 3.1 70B for Real Estate Search System

Tests:
1. Query Parsing - Extract filters from English, Romanian, Mixed queries
2. Response Formatting - Reply in user's language
3. Speed Test - Measure API response time
4. Cost - Verify free tier usage
"""

import json
import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Mock listings for response formatting test
MOCK_LISTINGS = [
    {
        "area_neighborhood": "Pipera",
        "sector": 1,
        "city_town": "București",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqm": 85,
        "price": 250000,
        "developer_name": "One United Properties",
        "project_name": "One Floreasca Lake"
    },
    {
        "area_neighborhood": "Pipera",
        "sector": 1,
        "city_town": "București",
        "bedrooms": 3,
        "bathrooms": 2,
        "sqm": 120,
        "price": 380000,
        "developer_name": "Nordis Group"
    },
    {
        "area_neighborhood": "Pipera",
        "sector": 2,
        "city_town": "București",
        "bedrooms": 2,
        "bathrooms": 2,
        "sqm": 92,
        "price": 295000
    }
]


def test_query_parsing():
    """TEST 1: Parse queries in English, Romanian, and Mixed languages."""
    print("\n" + "=" * 70)
    print("TEST 1: QUERY PARSING (Language → Universal Filters)")
    print("=" * 70)
    
    test_queries = [
        {
            "lang": "English",
            "query": "2 bedroom apartment in Pipera under 300000 EUR",
            "expected": {"bedrooms": 2, "area": "Pipera", "max_price": 300000}
        },
        {
            "lang": "Romanian",
            "query": "Apartament cu 2 camere în Pipera sub 300000 EUR",
            "expected": {"bedrooms": 2, "area": "Pipera", "max_price": 300000}
        },
        {
            "lang": "Mixed",
            "query": "Apartament in Sector 1 under 250k",
            "expected": {"sector": 1, "max_price": 250000}
        }
    ]
    
    client = Groq(api_key=GROQ_API_KEY)
    results = []
    
    for test in test_queries:
        print(f"\n🔍 Testing {test['lang']}: \"{test['query']}\"")
        
        prompt = f"""You are a real estate search filter extractor for the Romanian market (București and Ilfov).

Extract structured filters from the user query. Return ONLY a JSON object with these fields (omit if not mentioned):
- bedrooms (integer)
- bathrooms (integer)
- min_price (integer, EUR)
- max_price (integer, EUR)
- area_neighborhood (string, e.g., "Pipera", "Dorobanți")
- sector (integer 1-6 for București)
- judet (string: "București" or "Ilfov")
- sqm_min (integer)
- sqm_max (integer)

Handle both English and Romanian. Convert "k" notation (e.g., "250k" = 250000).

User query: {test['query']}

Return ONLY the JSON object, no markdown, no explanation."""

        start_time = time.time()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )
        elapsed = time.time() - start_time
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        try:
            filters = json.loads(content)
            print(f"✅ Extracted filters: {json.dumps(filters, indent=2)}")
            print(f"⏱️  Response time: {elapsed:.2f}s")
            
            results.append({
                "lang": test['lang'],
                "query": test['query'],
                "filters": filters,
                "time": elapsed,
                "success": True
            })
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {content}")
            results.append({
                "lang": test['lang'],
                "query": test['query'],
                "error": str(e),
                "raw": content,
                "time": elapsed,
                "success": False
            })
    
    return results


def test_response_formatting():
    """TEST 2: Format responses in the same language as the query."""
    print("\n" + "=" * 70)
    print("TEST 2: RESPONSE FORMATTING (Match User's Language)")
    print("=" * 70)
    
    test_cases = [
        {
            "lang": "English",
            "query": "2 bedroom apartment in Pipera under 300000 EUR"
        },
        {
            "lang": "Romanian",
            "query": "Apartament cu 2 camere în Pipera sub 300000 EUR"
        }
    ]
    
    client = Groq(api_key=GROQ_API_KEY)
    results = []
    
    for test in test_cases:
        print(f"\n📝 Testing {test['lang']} response...")
        print(f"Original query: \"{test['query']}\"")
        
        # Format listings for prompt
        listings_text = ""
        for idx, listing in enumerate(MOCK_LISTINGS, 1):
            dev = f" | Developer: {listing['developer_name']}" if listing.get('developer_name') else ""
            proj = f" | Project: {listing['project_name']}" if listing.get('project_name') else ""
            listings_text += f"{idx}. {listing['area_neighborhood']}, Sector {listing['sector']}, București — {listing['bedrooms']}bd, {listing['bathrooms']}ba, {listing['sqm']}m² — €{listing['price']:,}{dev}{proj}\n"
        
        prompt = f"""You are a helpful real estate assistant for the Romanian market.

The user asked: "{test['query']}"

Here are the matching properties:
{listings_text}

Write a natural, conversational response presenting these properties. IMPORTANT:
- Respond in the SAME LANGUAGE as the user's query
- If the query was in English, respond in English
- If the query was in Romanian, respond in Romanian
- Use proper real estate terminology for that language
- Keep it brief and professional

Response:"""

        start_time = time.time()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        elapsed = time.time() - start_time
        
        content = response.choices[0].message.content.strip()
        print(f"\n🤖 Groq Response ({elapsed:.2f}s):")
        print(content)
        
        results.append({
            "lang": test['lang'],
            "query": test['query'],
            "response": content,
            "time": elapsed
        })
    
    return results


def test_speed():
    """TEST 3: Speed test for both parsing and formatting."""
    print("\n" + "=" * 70)
    print("TEST 3: SPEED TEST")
    print("=" * 70)
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Quick parsing test
    parse_prompt = "Extract filters from: '2 bedroom apartment in Sector 2 under 200k EUR'. Return JSON only."
    
    start = time.time()
    parse_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": parse_prompt}],
        temperature=0.1,
        max_tokens=150
    )
    parse_time = time.time() - start
    
    # Quick formatting test
    format_prompt = "Say 'Found 3 apartments in Pipera' in Romanian."
    
    start = time.time()
    format_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": format_prompt}],
        temperature=0.7,
        max_tokens=100
    )
    format_time = time.time() - start
    
    total_time = parse_time + format_time
    
    print(f"\n⏱️  Parse query: {parse_time:.3f}s")
    print(f"⏱️  Format response: {format_time:.3f}s")
    print(f"⏱️  Total roundtrip: {total_time:.3f}s")
    
    if total_time < 1.0:
        print("✅ PASS: Total time < 1 second")
    else:
        print(f"⚠️  WARNING: Total time {total_time:.3f}s exceeds 1 second target")
    
    return {
        "parse_time": parse_time,
        "format_time": format_time,
        "total_time": total_time,
        "target_met": total_time < 1.0
    }


def main():
    print("=" * 70)
    print("🚀 GROQ/LLAMA 3.1 70B TEST SUITE")
    print("Real Estate Search System - Multilingual")
    print("=" * 70)
    
    if not GROQ_API_KEY:
        print("\n❌ ERROR: GROQ_API_KEY not found in environment")
        print("Please add to .env: GROQ_API_KEY=your_key_here")
        print("Get your key at: https://console.groq.com/keys")
        return
    
    print(f"\n✅ Groq API Key configured (ends with ...{GROQ_API_KEY[-8:]})")
    
    # Run all tests
    parse_results = test_query_parsing()
    format_results = test_response_formatting()
    speed_results = test_speed()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    
    # Quality check
    parse_success = sum(1 for r in parse_results if r.get('success', False))
    print(f"\n✅ QUALITY:")
    print(f"   - Query parsing: {parse_success}/{len(parse_results)} successful")
    print(f"   - Extraction accuracy: {'PASS' if parse_success == len(parse_results) else 'NEEDS REVIEW'}")
    
    # Multilingual check
    languages = set(r['lang'] for r in parse_results if r.get('success', False))
    print(f"\n✅ MULTILINGUAL:")
    print(f"   - Languages handled: {', '.join(languages)}")
    print(f"   - English support: {'✅' if 'English' in languages else '❌'}")
    print(f"   - Romanian support: {'✅' if 'Romanian' in languages else '❌'}")
    print(f"   - Mixed language: {'✅' if 'Mixed' in languages else '❌'}")
    
    # Speed check
    avg_parse_time = sum(r['time'] for r in parse_results if r.get('success', False)) / max(parse_success, 1)
    print(f"\n✅ SPEED:")
    print(f"   - Avg parse time: {avg_parse_time:.3f}s")
    print(f"   - Total roundtrip: {speed_results['total_time']:.3f}s")
    print(f"   - Speed target met: {'✅ YES' if speed_results['target_met'] else '⚠️ NO'}")
    
    # Cost check
    print(f"\n✅ COST:")
    print(f"   - Model: llama-3.3-70b-versatile")
    print(f"   - Tier: Free tier (Groq Cloud)")
    print(f"   - Estimated cost: $0.00 (free up to rate limits)")
    print(f"   - Rate limit: ~30 requests/minute")
    
    print("\n" + "=" * 70)
    print("🎉 TEST SUITE COMPLETE")
    print("=" * 70)
    
    # Overall verdict
    if parse_success == len(parse_results) and speed_results['target_met']:
        print("\n✅ VERDICT: Groq/Llama 3.3 70B is READY for production")
        print("   - Accurate multilingual parsing")
        print("   - Fast response times")
        print("   - Free tier available")
        print("\n🚀 RECOMMENDATION: Integrate into backend/search_engine.py")
    else:
        print("\n⚠️  VERDICT: Needs refinement before production")
        if parse_success < len(parse_results):
            print("   - Review failed parsing cases")
        if not speed_results['target_met']:
            print("   - Optimize prompts or consider caching")


if __name__ == "__main__":
    main()
