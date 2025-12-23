# Frontend Developer Guide - EstateGPT Schema Changes

## Quick Reference: What Changed?

### Field Names
- `sqft` → `sqm` (square meters, not feet)
- Everything else stays the same

### Data Types
- `bathrooms`: Now **INTEGER** (was decimal like 2.5)
  - Display as: "2 baths" (not "2.5 baths")
- `sqm`: **INTEGER** square meters
  - Display as: "95 m²"

---

## Listing Object Structure

```javascript
{
  id: "uuid",
  bedrooms: 2,           // integer: 0-5
  bathrooms: 2,          // integer: 1-4 (NOW INTEGER, NOT DECIMAL!)
  sqm: 95,               // integer: 35-400 (NEW FIELD! was 'sqft')
  price: 250000,         // integer: EUR (for sale)
  rent_price: 1200,      // integer: EUR/month (for rent)
  available_for_sale: true,
  available_for_rent: false,
  construction_status: "completed",
  city: "Bucharest",
  address: "...",
  description: "...",
  nearby_amenities: ["metro station", "supermarket", ...],
  listing_url: "...",
  image_urls: ["...", "...", ...],
  created_at: "2024-01-15T10:30:00Z"
}
```

---

## Display Code Examples

### Before (Old Schema)
```javascript
// ❌ DON'T DO THIS ANYMORE
`${listing.bathrooms} baths`  // Would show "2.5 baths" ❌
`${listing.sqft} sqft`        // Old field doesn't exist ❌
```

### After (New Schema)
```javascript
// ✅ DO THIS NOW

// Bathrooms display
const bathrooms = listing.bathrooms === 1 ? "1 bath" : `${listing.bathrooms} baths`;

// Area display with European unit
const area = `${listing.sqm} m²`;

// Price display (sale)
const salePrice = listing.price 
  ? `€${listing.price.toLocaleString('en-US')}` 
  : 'Contact for price';

// Rent display
const rentPrice = listing.rent_price 
  ? `€${listing.rent_price.toLocaleString('en-US')}/mo` 
  : 'Not available';

// Combined property info
const propertyInfo = `${listing.bedrooms} bed, ${bathrooms}, ${area}`;
// Output: "2 bed, 2 baths, 95 m²"
```

---

## Component Updates Needed

### PropertyCard Component
```javascript
// OLD
<div className="size">{listing.sqft} sqft</div>
<div className="baths">{listing.bathrooms} baths</div>

// NEW
<div className="size">{listing.sqm} m²</div>
<div className="baths">{listing.bathrooms} bath{listing.bathrooms !== 1 ? 's' : ''}</div>
```

### SearchBar / Filter Component
```javascript
// If you have any hardcoded examples mentioning sqft or decimal bathrooms:
// OLD
"Find apartments with 2.5 baths..."

// NEW
"Find apartments with 2 or 3 baths..."
```

### SearchResults Display
```javascript
// OLD listing display
<span>{listing.sqft} sqft</span>
<span>{listing.bathrooms} baths</span>

// NEW listing display  
<span>{listing.sqm} m²</span>
<span>{listing.bathrooms} bath{listing.bathrooms !== 1 ? 's' : ''}</span>
```

---

## API Response Format

When the backend returns search results, listings will look like:

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "bedrooms": 2,
      "bathrooms": 2,
      "sqm": 95,
      "price": 250000,
      "rent_price": null,
      "available_for_sale": true,
      "available_for_rent": false,
      "city": "Bucharest",
      "description": "Modern 2-bed apartment...",
      "nearby_amenities": ["metro station", "supermarket", "gym"],
      ...
    }
  ]
}
```

**Key Points**:
- `sqm` is present (look for this, not `sqft`)
- `bathrooms` is an integer (1, 2, 3, 4)
- All prices in EUR (no currency suffix in API)

---

## Testing Checklist

- [ ] Search returns listings with `sqm` field
- [ ] Search returns listings with `bathrooms` as integers
- [ ] PropertyCard displays "X m²" (not "X sqft")
- [ ] PropertyCard displays bathrooms without decimals
- [ ] Price displays with "€" prefix
- [ ] Rent displays with "€" and "/mo" suffix
- [ ] No "undefined" fields appear in UI
- [ ] Filter controls work with integer bathrooms (no 2.5, etc.)

---

## Migration Checklist for Devs

- [ ] Database migration applied (`listings` table recreated)
- [ ] `populate_listings.py` ran successfully (200 rows inserted)
- [ ] API backend tested and returns new schema
- [ ] Frontend components updated to use `sqm` instead of `sqft`
- [ ] Frontend components display bathrooms as integers
- [ ] Property card layout looks correct with m² instead of sqft
- [ ] Search filters work correctly
- [ ] Deployed to production

---

## Still Using Old Field Names?

If your code references `sqft`, you'll get:
```
Cannot read property 'sqft' of undefined
```

**Fix**: Replace `listing.sqft` with `listing.sqm`

If bathrooms shows as decimal (e.g., "2.5"):
- Check that your API is returning the new schema
- Verify the migration was applied to Supabase
- Check `database/schema.sql` shows `bathrooms INTEGER`

---

## Locale-Specific Formatting

### Number Formatting (Prices)
```javascript
// For Romanian/European format
const formatted = listing.price.toLocaleString('ro-RO');
// Output: "250.000"

// For US-style (with commas)
const formatted = listing.price.toLocaleString('en-US');
// Output: "250,000"

// Display with EUR
const display = `€${listing.price.toLocaleString('en-US')}`;
// Output: "€250,000"
```

### Area Unit
Always display with "m²" (square meters), never "sqft"
```javascript
const area = `${listing.sqm} m²`;
// Output: "95 m²"
```

---

## Support

If you have questions about the schema changes:
1. Read [SCHEMA_CHANGES.md](SCHEMA_CHANGES.md) for complete schema documentation
2. Check [MIGRATION_STEPS.md](MIGRATION_STEPS.md) for migration details
3. Review [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) for overview
