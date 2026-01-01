# ============================================
# 🤖 סקריפט בדיקה אוטומטית - Railway Deployment
# ============================================

$railwayUrl = "https://pais-production.up.railway.app"
$checkInterval = 10  # שניות בין בדיקות
$maxChecks = 18      # 18 בדיקות = 3 דקות

function Test-Deployment {
    param([string]$url)
    
    try {
        $response = Invoke-WebRequest -Uri "$url/health" -TimeoutSec 5 -ErrorAction Stop
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content
        }
    } catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

Write-Host "🤖 מתחיל ניטור אוטומטי של $railwayUrl" -ForegroundColor Cyan
Write-Host "⏱️  בדיקה כל $checkInterval שניות, סה״כ $maxChecks בדיקות (3 דקות)" -ForegroundColor White

for ($i = 1; $i -le $maxChecks; $i++) {
    Write-Host "`n🔍 בדיקה $i/$maxChecks - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    
    $result = Test-Deployment -url $railwayUrl
    
    if ($result.Success) {
        Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
        Write-Host "📊 Status: $($result.StatusCode)" -ForegroundColor Green
        Write-Host "📄 Response: $($result.Content)" -ForegroundColor DarkGreen
        
        # בדיקת endpoints נוספים אם ה-health עובד
        Write-Host "`n🔗 בודק endpoints נוספים..." -ForegroundColor Yellow
        
        $endpoints = @("/docs", "/api/v1/lottery/health", "/api/v1/stats")
        foreach ($endpoint in $endpoints) {
            try {
                $epTest = Test-Deployment -url "$railwayUrl$endpoint"
                if ($epTest.Success) {
                    Write-Host "   ✅ $endpoint : $($epTest.StatusCode)" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️  $endpoint : לא זמין" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "   ❌ $endpoint : שגיאה" -ForegroundColor Red
            }
        }
        
        break
    } else {
        Write-Host "❌ עדיין לא זמין: $($result.Error)" -ForegroundColor Red
        
        # התקדמות
        $progress = [math]::Round(($i / $maxChecks) * 100)
        Write-Progress -Activity "מחכה ל-Railway Deployment" -Status "בדיקה $i מתוך $maxChecks" -PercentComplete $progress
        
        if ($i -lt $maxChecks) {
            Write-Host "⏳ מחכה $checkInterval שניות..." -ForegroundColor DarkGray
            Start-Sleep -Seconds $checkInterval
        }
    }
}

# תוצאה סופית
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "📊 סיכום בדיקה:" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 סיימתי בדיקה. אפליקציה $(if ($result.Success) {'עובדת!'} else {'עדיין לא זמינה.'})" -ForegroundColor $(if ($result.Success) {'Green'} else {'Yellow'})
