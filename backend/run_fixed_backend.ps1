Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎯 FASTAPI BACKEND עם LOTTERY API" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🌐 API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "❤️ Health: http://localhost:8000/health" -ForegroundColor Yellow
Write-Host "🎰 Lottery: http://localhost:8000/api/v1/lottery/health" -ForegroundColor Yellow
Write-Host "🔮 Prediction: http://localhost:8000/api/v1/lottery/prediction" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nLogs:`n" -ForegroundColor Gray

# הפעלת ה-backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
