# =========================================
# 🚀 הפעלה מהירה - Prediction Point System
# =========================================

# עצירת תהליכים קודמים
taskkill /f /im python.exe 2>nul
Start-Sleep 2

# הפעלת Backend
Start-Process cmd.exe -ArgumentList '/k "cd /d ""C:\Users\Giga Store\Downloads\PAIS-main\PAIS-main\backend"" && python -m uvicorn main:app --host 0.0.0.0 --port 8000"'

# פתיחת דפדפן
Start-Sleep 5
Start-Process "http://localhost:8000/docs"

Write-Host "========================================"
Write-Host "✅ המערכת מופעלת!"
Write-Host "   API: http://localhost:8000"
Write-Host "   Docs: http://localhost:8000/docs"
Write-Host "========================================"
