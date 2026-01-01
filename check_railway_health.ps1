# ============================================
# 🧪 סקריפט בדיקה מקיף - Railway Healthcheck
# ============================================

param(
    [string]$Url = "https://pais-production.up.railway.app",
    [int]$Timeout = 30
)

Write-Host "🎯 בדיקת Railway Healthcheck Failure" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$endpoints = @(
    @{Path="/health"; Name="בריאות בסיסית"; Expected=200},
    @{Path="/docs"; Name="תיעוד API"; Expected=200},
    @{Path="/openapi.json"; Name="OpenAPI JSON"; Expected=200},
    @{Path="/api/v1/lottery/health"; Name="בריאות Lottery"; Expected=200}
)

Write-Host "`n🔍 בודק endpoints..." -ForegroundColor Yellow

foreach ($endpoint in $endpoints) {
    $fullUrl = "$Url$($endpoint.Path)"
    Write-Host "   🔗 $($endpoint.Name)" -ForegroundColor Gray
    Write-Host "      📍 GET $fullUrl" -ForegroundColor DarkGray
    
    try {
        $response = Invoke-WebRequest -Uri $fullUrl -Method GET -TimeoutSec $Timeout -ErrorAction Stop
        
        if ($response.StatusCode -eq $endpoint.Expected) {
            Write-Host "      ✅ עבר ($($response.StatusCode))" -ForegroundColor Green
        } else {
            Write-Host "      ⚠️ סטטוס לא צפוי: $($response.StatusCode)" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "      ❌ שגיאה: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

# בדיקת זמן תגובה
Write-Host "`n⏱️ בדיקת זמן תגובה..." -ForegroundColor Yellow

try {
    $startTime = Get-Date
    $response = Invoke-RestMethod -Uri "$Url/health" -TimeoutSec 10 -ErrorAction Stop
    $endTime = Get-Date
    $responseTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "   ✅ זמן תגובה: $([Math]::Round($responseTime))ms" -ForegroundColor Green
    Write-Host "   📊 תגובה: $($response | ConvertTo-Json -Compress)" -ForegroundColor DarkGreen
    
} catch {
    Write-Host "   ❌ לא ניתן להגיע ל-health endpoint" -ForegroundColor Red
}

# בדיקת משתני סביבה
Write-Host "`n🔧 בדיקת משתני סביבה מומלצים:" -ForegroundColor Yellow

$envVars = @(
    @{Name="DATABASE_URL"; Description="חיבור ל-PostgreSQL"},
    @{Name="PORT"; Description="פורט האפליקציה"},
    @{Name="ENVIRONMENT"; Description="סביבה (production/development)"},
    @{Name="SECRET_KEY"; Description="מפתח הצפנה"}
)

foreach ($var in $envVars) {
    Write-Host "   🔑 $($var.Name): $($var.Description)" -ForegroundColor Gray
}

Write-Host "`n📝 הנחיות לפתרון בעיות:" -ForegroundColor Cyan
Write-Host "   1. בדוק את Railway Deploy Logs" -ForegroundColor White
Write-Host "   2. ודא ש-DATABASE_URL תקין" -ForegroundColor White
Write-Host "   3. בדוק שהאפליקציה מקשיבה ב-0.0.0.0:8000" -ForegroundColor White
Write-Host "   4. הגדל את healthcheckTimeout ל-60 שניות" -ForegroundColor White

Write-Host "`n🚀 קישורים לניטור:" -ForegroundColor Magenta
Write-Host "   • Railway Dashboard: https://railway.app" -ForegroundColor White
Write-Host "   • Deploy Logs: https://railway.app/project/[project-id]/deployments" -ForegroundColor White
Write-Host "   • Variables: https://railway.app/project/[project-id]/variables" -ForegroundColor White

Write-Host "`n✅ סיום בדיקה!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
