# PowerShell script for quick deployment to Railway

Write-Host "🚀 Starting Railway deployment..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Build React
Write-Host "🔨 Building React frontend..." -ForegroundColor Yellow
cd "frontend-simple"
npm run build

# Copy to backend
Write-Host "📁 Copying build to backend/static..." -ForegroundColor Yellow
cd ..
if (Test-Path "backend/static") {
    Remove-Item -Path "backend/static" -Recurse -Force
}
New-Item -ItemType Directory -Path "backend/static" -Force
Copy-Item -Path "frontend-simple/build/*" -Destination "backend/static" -Recurse

# Push to GitHub (triggers Railway auto-deploy)
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
git add .
git commit -m "🚀 Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin main

Write-Host "✅ Pushed to GitHub! Railway will start building automatically" -ForegroundColor Green
Write-Host "🌐 Live app: https://pais-production.up.railway.app" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan
