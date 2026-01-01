# ============================================
# 🧪 סקריפט בדיקה מקיף - Prediction Point System
# ============================================

Write-Host "🎯 התחלת בדיקה מקיפה של המערכת" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$baseUrl = "https://pais-production.up.railway.app"
$localUrl = "http://localhost:8000"

# בחירת URL לבדיקה
$useLocal = $false
if ($useLocal) {
    $apiUrl = $localUrl
    Write-Host "🔧 בדיקה מקומית: $apiUrl" -ForegroundColor Yellow
} else {
    $apiUrl = $baseUrl
    Write-Host "🌐 בדיקה חיה: $apiUrl" -ForegroundColor Green
}

# רשימת כל נקודות הקצה לבדיקה
$endpoints = @(
    # בריאות בסיסית
    @{Name="בריאות מערכת"; Path="/health"; Method="GET"},
    @{Name="בריאות Lottery API"; Path="/api/v1/lottery/health"; Method="GET"},
    @{Name="תיעוד API (Docs)"; Path="/docs"; Method="GET"},
    @{Name="OpenAPI JSON"; Path="/openapi.json"; Method="GET"},
    
    # Lottery API
    @{Name="תחזית לוטו"; Path="/api/v1/lottery/prediction"; Method="GET"},
    @{Name="ניתוח לוטו"; Path="/api/v1/lottery/analysis"; Method="GET"},
    @{Name="הגרלות אחרונות"; Path="/api/v1/lottery/last-draws"; Method="GET"},
    
    # מערכת משתמשים
    @{Name="סטטיסטיקות מערכת"; Path="/api/v1/stats"; Method="GET"},
    @{Name="רשימת משתמשים"; Path="/api/v1/users"; Method="GET"},
    
    # Predictions
    @{Name="רשימת חיזויים"; Path="/api/v1/predictions"; Method="GET"},
    
    # Market
    @{Name="פריטי שוק"; Path="/api/v1/market"; Method="GET"},
    
    # Ledger
    @{Name="יתרת נקודות"; Path="/api/v1/ledger/balance"; Method="GET"; Auth=$true},
    @{Name="היסטוריית עסקאות"; Path="/api/v1/ledger/transactions"; Method="GET"; Auth=$true}
)

# סטטיסטיקות
$totalTests = $endpoints.Count
$passedTests = 0
$failedTests = 0

Write-Host "`n🔍 מתחיל בדיקת $totalTests endpoints..." -ForegroundColor Cyan

foreach ($endpoint in $endpoints) {
    $url = "$apiUrl$($endpoint.Path)"
    $testName = $endpoint.Name
    
    Write-Host "`n   🔗 $testName" -ForegroundColor Gray
    Write-Host "      📍 $($endpoint.Method) $url" -ForegroundColor DarkGray
    
    try {
        # אם דורש authentication, דלג
        if ($endpoint.Auth -eq $true) {
            Write-Host "      ⏭️ דורש authentication - מדלג" -ForegroundColor Yellow
            continue
        }
        
        # ביצוע הבקשה
        if ($endpoint.Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 30 -ErrorAction Stop
        } else {
            $response = Invoke-WebRequest -Uri $url -Method $endpoint.Method -TimeoutSec 30 -ErrorAction Stop
        }
        
        # בדיקת תגובה
        if ($response.StatusCode -eq 200) {
            $passedTests++
            Write-Host "      ✅ עבר ($($response.StatusCode))" -ForegroundColor Green
            
            # הצגת תקציר תגובה
            if ($response.Headers['Content-Type'] -like '*json*') {
                try {
                    $json = $response.Content | ConvertFrom-Json
                    $summary = ($json | ConvertTo-Json -Compress -Depth 1)
                    if ($summary.Length -gt 100) {
                        $summary = $summary.Substring(0, 100) + "..."
                    }
                    Write-Host "      📊 תגובה: $summary" -ForegroundColor DarkGreen
                } catch {
                    Write-Host "      📄 תוכן: $($response.Content.Substring(0, [Math]::Min(150, $response.Content.Length)))..." -ForegroundColor DarkGreen
                }
            }
        } else {
            $failedTests++
            Write-Host "      ⚠️ סטטוס: $($response.StatusCode)" -ForegroundColor Yellow
        }
        
    } catch {
        $failedTests++
        $errorMsg = $_.Exception.Message
        Write-Host "      ❌ שגיאה: $errorMsg" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

# סיכום
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "📊 סיכום בדיקות:" -ForegroundColor Yellow
Write-Host "   ✅ עברו: $passedTests" -ForegroundColor Green
Write-Host "   ❌ נכשלו: $failedTests" -ForegroundColor Red
Write-Host "   ⏭️ דולגו: $($totalTests - $passedTests - $failedTests)" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan

# בדיקות נוספות
Write-Host "`n🔧 בדיקות נוספות:" -ForegroundColor Cyan

# בדיקת זמן תגובה
try {
    $startTime = Get-Date
    $healthResponse = Invoke-RestMethod -Uri "$apiUrl/health" -TimeoutSec 10 -ErrorAction Stop
    $endTime = Get-Date
    $responseTime = ($endTime - $startTime).TotalMilliseconds
    Write-Host "   ⏱️ זמן תגובת /health: $([Math]::Round($responseTime))ms" -ForegroundColor Green
} catch {
    Write-Host "   ⏱️ לא ניתן למדוד זמן תגובה" -ForegroundColor Red
}

# הצגת קישורים חשובים
Write-Host "`n🔗 קישורים חשובים:" -ForegroundColor Cyan
Write-Host "   🌐 אפליקציה חיה: $baseUrl" -ForegroundColor White
Write-Host "   📚 תיעוד API: $baseUrl/docs" -ForegroundColor White
Write-Host "   🚂 Railway Dashboard: https://railway.app" -ForegroundColor White
Write-Host "   📁 GitHub Repo: https://github.com/osifeu-prog/PAIS" -ForegroundColor White

Write-Host "`n🎯 סיום בדיקה מקיפה!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
