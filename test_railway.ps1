# סקריפט בדיקה ל-Railway deployment
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚂 בדיקת Railway Deployment" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Cyan

$railwayUrl = "https://pais-production.up.railway.app"

Write-Host "🌐 בדיקת המערכת החיה ב-Railway..." -ForegroundColor Yellow
Write-Host "   URL: $railwayUrl" -ForegroundColor Gray

# המתנה קצרה לבנייה
Write-Host "⏳ מתן זמן ל-Railway לבנות (30 שניות)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

$endpoints = @(
    @{Name="בריאות מערכת"; Path="/health"},
    @{Name="בריאות Lottery API"; Path="/api/v1/lottery/health"},
    @{Name="תרגום (עברית)"; Path="/api/v1/translate?key=app_title"}
)

foreach ($endpoint in $endpoints) {
    $url = "$railwayUrl$($endpoint.Path)"
    try {
        Write-Host "`n🔗 בודק: $($endpoint.Name)" -ForegroundColor Gray
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 15 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host "   🟢 עובד! (סטטוס: $($response.StatusCode))" -ForegroundColor Green
            
            if ($response.Headers['Content-Type'] -like '*json*') {
                $json = $response.Content | ConvertFrom-Json
                Write-Host "   📊 תגובה: $(($json | ConvertTo-Json -Compress))" -ForegroundColor DarkGreen
            }
        }
    } catch {
        Write-Host "   🔴 שגיאה: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "📊 פתח את לוח הבקרה של Railway:" -ForegroundColor Yellow
Write-Host "https://railway.app/project/$(railway project)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
