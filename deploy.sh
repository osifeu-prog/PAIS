#!/bin/bash
echo "🚀 התחלת דחיפה ל-Railway..."
cd "$(dirname "$0")"

echo "🔨 בונה React frontend..."
cd frontend-simple
npm run build

echo "📁 מעתיק build ל-backend..."
cd ..
if [ -d "backend/static" ]; then
    rm -rf backend/static
fi
mkdir -p backend/static
cp -r frontend-simple/build/* backend/static/

echo "📦 דוחף ל-GitHub..."
git add .
git commit -m "🚀 Update: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo "✅ נדחף! Railway יתחיל לבנות אוטומטית"
echo "🌐 האפליקציה: https://pais-production.up.railway.app"
