# Prediction Point System - Continuation Script
# =============================================

Write-Host "🎯 PREDICTION POINT SYSTEM - READY" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

cd "C:\Users\Giga Store\Downloads\PAIS-main\PAIS-main"

# Check status
Write-Host "`n📊 Service Status:" -ForegroundColor Green
docker-compose ps

# Quick test
Write-Host "`n🧪 Quick API Test:" -ForegroundColor Green
$testUrls = @("http://localhost:8000/", "http://localhost:8000/api/v1/test", "http://localhost:8000/api/v1/stats")

foreach ($url in $testUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5
        Write-Host "✅ $url : OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $url : FAILED" -ForegroundColor Red
    }
}

# Open interfaces
Write-Host "`n🌐 Opening interfaces..." -ForegroundColor Green
Start-Process "http://localhost:8000/docs"
Start-Process "http://localhost:3000"

Write-Host "`n📋 Ready for Phase 3: Database & Features" -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host "• Add PostgreSQL database" -ForegroundColor White
Write-Host "• Implement user authentication" -ForegroundColor White
Write-Host "• Create prediction models" -ForegroundColor White
Write-Host "• Build points system" -ForegroundColor White
