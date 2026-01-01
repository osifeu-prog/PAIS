Write-Host "הפעלת Prediction Point System עם Lottery..." -ForegroundColor Green
Write-Host "Backend API ירוץ על: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Lottery API: http://localhost:8000/api/v1/lottery/health" -ForegroundColor Cyan
Write-Host ""
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
