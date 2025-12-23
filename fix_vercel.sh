#!/bin/bash
set -e

echo "🚀 Starting Repo Fix..."

# 1. Move files from frontend/ to root (skipping node_modules/dist/.git)
rsync -av --remove-source-files --exclude 'node_modules' --exclude 'dist' --exclude '.git' frontend/ ./

# 2. Merge .gitignores
if [ -f frontend/.gitignore ]; then
  cat frontend/.gitignore >> .gitignore
  sort -u .gitignore -o .gitignore
fi

# 3. Remove the empty frontend folder
rm -rf frontend

# 4. Fix vite.config.js references
if [ -f vite.config.js ]; then
  sed -i '' "s|frontend/||g" vite.config.js
  sed -i '' -E "s|(root:\\s*['\"])frontend(['\"])|\\1.\\2|g" vite.config.js
fi

# 5. Fix package.json scripts
if [ -f package.json ]; then
  sed -i '' "s|frontend/||g" package.json
fi

# 6. Re-install dependencies
echo "📦 Installing dependencies..."
npm install

# 7. Push to Vercel
echo "💾 Pushing to GitHub..."
git add .
git commit -m "Flatten repo to fix Vercel 404"
git push origin main

echo "✅ SUCCESS! Your site is deploying."
