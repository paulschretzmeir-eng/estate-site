# How to Apply European Standards Migration to Supabase

## Quick Steps

### 1. Navigate to Supabase Dashboard

Go to https://app.supabase.com and sign in to your account.

### 2. Open Your Project

Click on your project (the one with the EstateGPT data).

### 3. Go to SQL Editor

In the left sidebar, click **SQL Editor** (or navigate to the SQL section).

### 4. Create New Query

Click **New Query** (or similar button to create a new SQL script).

### 5. Paste the Migration SQL

Copy and paste the following SQL into the editor:

```sql
-- Drop old listings table
DROP TABLE IF EXISTS listings CASCADE;

-- Create new table with European standards schema
CREATE TABLE listings (
    id VARCHAR(100) PRIMARY KEY,
    price INTEGER,
    rent_price INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    sqm INTEGER,
    available_for_sale BOOLEAN DEFAULT FALSE,
    available_for_rent BOOLEAN DEFAULT FALSE,
    address TEXT,
    city VARCHAR(100),
    description TEXT,
    nearby_amenities TEXT[],
    construction_status VARCHAR(50) DEFAULT 'completed',
    listing_url TEXT,
    image_urls TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast queries
CREATE INDEX idx_listings_city ON listings(city);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_rent_price ON listings(rent_price);
CREATE INDEX idx_listings_bedrooms ON listings(bedrooms);
CREATE INDEX idx_listings_available_sale ON listings(available_for_sale);
CREATE INDEX idx_listings_available_rent ON listings(available_for_rent);
```

### 6. Execute the Query

Click **Run** (or press Ctrl+Enter / Cmd+Enter) to execute the SQL.

You should see a success message like: `Successfully executed 6 statements`

### 7. Verify the Table Was Created

Go to **Table Editor** in the left sidebar and verify that the `listings` table exists with these columns:
- id (varchar)
- price (int)
- rent_price (int)
- bedrooms (int)
- bathrooms (int)
- sqm (int)
- available_for_sale (bool)
- available_for_rent (bool)
- address (text)
- city (varchar)
- description (text)
- nearby_amenities (text[])
- construction_status (varchar)
- listing_url (text)
- image_urls (text[])
- created_at (timestamp)

### 8. Populate with New Data

Once the migration is complete, run this command in your terminal:

```bash
python scripts/populate_listings.py
```

This will:
- Load 200 Romanian listings from the seed file
- Insert them into the new schema
- Verify the population

Expected output:
```
✅ SUCCESS! Database populated with 200 Romanian listings
```

## Troubleshooting

### Error: "relation "listings" already exists"

This means the table already exists. You can either:
- Use the `DROP TABLE IF EXISTS listings CASCADE;` command first (included in the SQL above)
- Or manually delete the table first via the Table Editor

### Error: "permission denied"

Your Supabase user role may not have sufficient permissions. Ask the project owner or use the `postgres` role in Supabase.

### Error: "column "sqm" does not exist"

The old schema is still being used. Run the migration SQL again, making sure the DROP statement executes first.

### The `populate_listings.py` script still fails

1. Verify the table was created: Go to Table Editor and look for `listings`
2. Verify the columns exist, especially `sqm` and the new schema
3. Make sure your `.env` has correct `SUPABASE_URL` and `SUPABASE_KEY`

## What Changed

| Field | Old Type | New Type | Reason |
|-------|----------|----------|--------|
| bathrooms | DECIMAL(3,1) | INTEGER | European real estate counts rooms, not fractions |
| sqft | DECIMAL | sqm INTEGER | Europe uses square meters, not square feet |
| price | ? | INTEGER EUR | Clarified as whole EUR amounts |
| rent_price | ? | INTEGER EUR | Clarified as whole EUR amounts |

## Next Steps

After populating the database with the new schema:

1. **Update Frontend**: Ensure your React components expect the new field names:
   - Use `sqm` instead of `sqft`
   - Display `bathrooms` as integers (no decimal points)
   - Show prices with "€" prefix and "m²" suffix for area

2. **Test Backend**: Run a search test:
   ```bash
   curl -X POST http://localhost:5000/api/search \
     -H "Content-Type: application/json" \
     -d '{"prompt":"2 bedroom apartment in Bucharest under 300000"}'
   ```

3. **Verify Frontend**: Test searching and viewing listings in the web app

## See Also

- [SCHEMA_CHANGES.md](SCHEMA_CHANGES.md) - Detailed schema documentation
- [database/migrations/001_european_standards.sql](database/migrations/001_european_standards.sql) - Migration SQL file
- [scripts/populate_listings.py](scripts/populate_listings.py) - Population script
