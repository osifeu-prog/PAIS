Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "⚛️ REACT FRONTEND - Prediction Point System" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "🔗 Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "🎯 Lottery API: http://localhost:8000/api/v1/lottery/health" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nLogs:`n" -ForegroundColor Gray

# הגדרת environment variables
$env:CI = "false"
$env:NODE_OPTIONS = "--openssl-legacy-provider"
npm start
