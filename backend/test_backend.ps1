Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🧪 בדיקת Backend אחרי תיקון הייבוא" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

try {
    python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
} catch {
    Write-Host "❌ שגיאה: $_" -ForegroundColor Red
    Write-Host "פתרון בעיות:"
    Write-Host "1. בדוק את קובץ translations.py קיים"
    Write-Host "2. בדוק שאין שגיאות תחביר ב-main.py"
    Write-Host "3. הרץ: python -c 'from translations import translations; print(translations[\"app_title\"][\"he\"])'"
    pause
}
