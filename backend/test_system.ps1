Write-Host "🧪 PAIS System Test" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

# בדיקת endpoints
$baseUrl = "http://localhost:8000"
$endpoints = @(
    @{Name="Root"; Path="/"},
    @{Name="Health"; Path="/health"},
    @{Name="Docs"; Path="/docs"},
    @{Name="Auth Register"; Path="/api/v1/auth/register"},
    @{Name="Auth Login"; Path="/api/v1/auth/login"}
)

foreach ($endpoint in $endpoints) {
    $url = $baseUrl + $endpoint.Path
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -ErrorAction SilentlyContinue
        Write-Host "✅ $($endpoint.Name) - זמין" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($endpoint.Name) - לא זמין" -ForegroundColor Red
    }
}

Write-Host "`n📊 בדיקת התחברות:" -ForegroundColor Cyan
Write-Host "להתחברות ידנית, הרץ:" -ForegroundColor Gray
Write-Host "`$headers = @{'accept'='application/json';'Authorization'='Bearer YOUR_TOKEN'}" -ForegroundColor Gray
Write-Host "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/me' -Headers `$headers" -ForegroundColor Gray
