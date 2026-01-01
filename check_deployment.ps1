# ============================================
# 🧪 סקריפט בדיקה אוטומטית - Railway Deployment
# ============================================

$url = "https://pais-production.up.railway.app"
$maxAttempts = 30  # 30 ניסיונות = 5 דקות
$delaySeconds = 10

Write-Host "🎯 בדיקת Railway Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🌐 URL: $url" -ForegroundColor White
Write-Host "⏱️  בדיקה כל $delaySeconds שניות, סהכ 5 דקות" -ForegroundColor White

$attempt = 1
$success = $false

while ($attempt -le $maxAttempts -and -not $success) {
    Write-Host "`n🔍 ניסיון $attempt/$maxAttempts..." -ForegroundColor Gray
    
    try {
        # בדיקת health endpoint
        $response = Invoke-WebRequest -Uri "$url/health" -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $success = $true
            Write-Host "✅ SUCCESS! Health check passed!" -ForegroundColor Green
            Write-Host "📊 Status Code: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "📄 Response: $($response.Content)" -ForegroundColor DarkGreen
            
            # בדיקת endpoints נוספים
            Write-Host "`n🔗 בדיקת endpoints נוספים:" -ForegroundColor Yellow
            
            $endpoints = @("/docs", "/api/v1/lottery/health", "/api/v1/stats")
            foreach ($endpoint in $endpoints) {
                try {
                    $epResponse = Invoke-WebRequest -Uri "$url$endpoint" -TimeoutSec 5 -ErrorAction Stop
                    Write-Host "   ✅ $endpoint : $($epResponse.StatusCode)" -ForegroundColor Green
                } catch {
                    Write-Host "   ⚠️  $endpoint : לא זמין" -ForegroundColor Yellow
                }
            }
            
            break
        } else {
            Write-Host "⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch [System.Net.WebException] {
        Write-Host "❌ Connection failed: $($_.Exception.Message)" -ForegroundColor Red
    } catch {
        Write-Host "❒ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # התקדמות
    $progress = [math]::Round(($attempt / $maxAttempts) * 100)
    Write-Progress -Activity "Checking Railway Deployment" -Status "Attempt $attempt of $maxAttempts" -PercentComplete $progress
    
    if ($attempt -lt $maxAttempts) {
        Write-Host "⏳ מחכה $delaySeconds שניות לפני ניסיון הבא..." -ForegroundColor DarkGray
        Start-Sleep -Seconds $delaySeconds
    }
    
    $attempt++
}

# תוצאה סופית
Write-Host "`n==========================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "🚀 האפליקציה עובדת ב: $url" -ForegroundColor White
    Write-Host "📚 API Docs: $url/docs" -ForegroundColor White
    
    # הצגת QR code ל-URL
    $qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=$url"
    Write-Host "📱 QR Code: $qrUrl" -ForegroundColor Gray
    
} else {
    Write-Host "❌ DEPLOYMENT FAILED או עדיין לא מוכן" -ForegroundColor Red
    Write-Host "🔧 מה לעשות עכשיו:" -ForegroundColor Yellow
    Write-Host "   1. בדוק את Railway Deploy Logs" -ForegroundColor White
    Write-Host "   2. ודא שה-DATABASE_URL מוגדר ב-Railway Variables" -ForegroundColor White
    Write-Host "   3. חכה עוד 5 דקות ואריץ שוב" -ForegroundColor White
}

Write-Host "==========================================" -ForegroundColor Cyan
