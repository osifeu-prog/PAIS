# PowerShell deploy script for Railway
Write-Host "🚀 Starting Railway deployment..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$basePath = "C:\Users\Giga Store\Downloads\PAIS-main\PAIS-main"
$backendPath = "$basePath\backend"
$frontendPath = "$basePath\frontend-simple"

# Build React
Write-Host "🔨 Building React..." -ForegroundColor Yellow
cd $frontendPath
npm run build

# Copy to backend
Write-Host "📁 Copying to backend/static..." -ForegroundColor Yellow
cd $basePath
if (Test-Path "backend/static") {
    Remove-Item -Path "backend/static" -Recurse -Force
}
New-Item -ItemType Directory -Path "backend/static" -Force
Copy-Item -Path "frontend-simple/build/*" -Destination "backend/static" -Recurse

# Git push
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
git add .
git commit -m "🚀 Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin main

Write-Host "✅ Pushed to GitHub!" -ForegroundColor Green
Write-Host "🚂 Railway will start building automatically" -ForegroundColor Magenta
Write-Host "🌐 Live app: https://pais-production.up.railway.app" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan
