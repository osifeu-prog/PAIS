# Prediction Point System - Phase 3 Next Steps
# ============================================

Write-Host "🎯 PHASE 3: IMPLEMENTING FEATURES" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

cd "C:\Users\Giga Store\Downloads\PAIS-main\PAIS-main"

# 1. בדיקת סטטוס
Write-Host "`n[1] System Status:" -ForegroundColor Green
docker-compose ps

# 2. אתחול database (אם לא נעשה)
Write-Host "`n[2] Initialize Database (if not done):" -ForegroundColor Green
Write-Host "   POST http://localhost:8000/api/v1/init-db" -ForegroundColor Gray

# 3. בדיקת endpoints
Write-Host "`n[3] Testing endpoints:" -ForegroundColor Green
$testUrls = @(
    "http://localhost:8000/",
    "http://localhost:8000/api/v1/test",
    "http://localhost:8000/health",
    "http://localhost:8000/api/v1/stats"
)

foreach ($url in $testUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5
        Write-Host "   ✅ $url" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $url" -ForegroundColor Red
    }
}

# 4. יצירת routers (סקריפטים לדוגמה)
Write-Host "`n[4] Create router files:" -ForegroundColor Green
Write-Host "   • Create auth.py in backend/routers/" -ForegroundColor White
Write-Host "   • Create users.py in backend/routers/" -ForegroundColor White
Write-Host "   • Create predictions.py in backend/routers/" -ForegroundColor White
Write-Host "   • Create market.py in backend/routers/" -ForegroundColor White

# 5. עדכון main.py לכלול routers
Write-Host "`n[5] Update main.py to include routers:" -ForegroundColor Green
Write-Host "   • Uncomment router imports" -ForegroundColor White
Write-Host "   • Uncomment app.include_router() lines" -ForegroundColor White

Write-Host "`n📋 Ready to implement real features!" -ForegroundColor Magenta
Write-Host "======================================" -ForegroundColor Magenta
