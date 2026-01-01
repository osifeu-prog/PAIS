Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "⚛️ React Frontend" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nLogs:`n" -ForegroundColor Gray

# הגדר environment variable כדי למנוע בעיות
$env:CI = "false"
$env:NODE_OPTIONS = "--openssl-legacy-provider"
npm start
