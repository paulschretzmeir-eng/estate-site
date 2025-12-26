# Database Setup Instructions

## Step 1: Update .env file
1. Open `.env` file
2. Replace `[MY-PASSWORD]` with your actual Supabase database password
3. Save the file

## Step 2: Run the schema in Supabase
1. Go to your Supabase Dashboard: https://supabase.com/dashboard/project/ycfmrloksqrbyfmivpbu
2. Click "SQL Editor" in the left sidebar
3. Click "New Query"
4. Copy all contents from `database/schema.sql`
5. Paste into the SQL Editor
6. Click "Run" (or press Ctrl+Enter)
7. You should see: "Success. No rows returned"

## Step 3: Verify it worked
1. Click "Table Editor" in left sidebar
2. You should see a table called "listings"
3. Click it to see all columns

## ✅ Done!
Your database is ready for backend code.

## Notes
- The table is empty (0 rows)
- Data will be added later by the Python backend
- Backend will pull from real estate APIs

## Security Reminder
- Never commit your `.env` file to GitHub
- Your `.gitignore` should include `.env`
- Keep your password private and secure