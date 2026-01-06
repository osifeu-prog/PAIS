Write-Host "🧪 Testing Authentication System..." -ForegroundColor Cyan

# שלב 1: רישום משתמש חדש
Write-Host "`n1. Testing registration..." -ForegroundColor Yellow
$registerBody = @{
    username = "testuser2"
    email = "test2@example.com"
    password = "password123"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method Post -Body $registerBody -ContentType "application/json"
    Write-Host "✅ Registration successful! User ID: $($registerResponse.id)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Registration failed (maybe user exists): $_" -ForegroundColor Yellow
}

# שלב 2: התחברות
Write-Host "`n2. Testing login..." -ForegroundColor Yellow
$loginBody = @{
    username = "testuser"
    password = "password123"
    grant_type = ""
    scope = ""
    client_id = ""
    client_secret = ""
}

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    Write-Host "✅ Login successful!" -ForegroundColor Green
    $token = $loginResponse.access_token
    Write-Host "Token: $($token.Substring(0, 50))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Login failed: $_" -ForegroundColor Red
    exit 1
}

# שלב 3: בדיקת /me endpoint
Write-Host "`n3. Testing /me endpoint..." -ForegroundColor Yellow
$headers = @{
    "accept" = "application/json"
    "Authorization" = "Bearer $token"
}

try {
    $meResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method Get -Headers $headers
    Write-Host "✅ /me endpoint successful!" -ForegroundColor Green
    Write-Host "User: $($meResponse.username) (ID: $($meResponse.id))" -ForegroundColor Green
} catch {
    Write-Host "❌ /me endpoint failed: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Authentication system test complete!" -ForegroundColor Green
