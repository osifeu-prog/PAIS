Write-Host "🚀 Starting PAIS Server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "`nServer will be available at:" -ForegroundColor Cyan
Write-Host "• http://localhost:8000" -ForegroundColor White
Write-Host "• http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n" -ForegroundColor Gray

uvicorn main:app --reload --host 0.0.0.0 --port 8000
