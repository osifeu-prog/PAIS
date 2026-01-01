# =========================================
# 🎰 סקריפט הדגמה - אינטגרציה עם מפעל הפיס
# =========================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🎰 הדגמת אינטגרציה עם מפעל הפיס" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000/api/v1/lottery"

Write-Host "`n🔍 בדיקת שירות הלוטו..." -ForegroundColor Blue
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health"
    Write-Host "   ✅ שירות לוטו פעיל" -ForegroundColor Green
} catch {
    Write-Host "   ❌ שירות לוטו לא זמין" -ForegroundColor Red
    exit 1
}

Write-Host "`n📊 קבלת הגרלות אחרונות..." -ForegroundColor Blue
try {
    $lastDraws = Invoke-RestMethod -Uri "$baseUrl/last-draws"
    Write-Host "   ✅ קיבלתי $($lastDraws.count) הגרלות" -ForegroundColor Green
    $lastDraws.draws | ForEach-Object {
        Write-Host "   🎫 תאריך: $($_.date), מספרים: $($_.numbers -join ', '), מיוחד: $($_.special_number)" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ לא ניתן לקבל הגרלות" -ForegroundColor Red
}

Write-Host "`n📈 ניתוח סטטיסטי..." -ForegroundColor Blue
try {
    $analysis = Invoke-RestMethod -Uri "$baseUrl/analysis"
    Write-Host "   ✅ ניתוח סטטיסטי התקבל" -ForegroundColor Green
    Write-Host "   🔥 מספרים חמים: $($analysis.analysis.hot_numbers -join ', ')" -ForegroundColor Yellow
    Write-Host "   ❄️  מספרים קרים: $($analysis.analysis.cold_numbers -join ', ')" -ForegroundColor Blue
} catch {
    Write-Host "   ❌ לא ניתן לקבל ניתוח" -ForegroundColor Red
}

Write-Host "`n🔮 קבלת תחזית..." -ForegroundColor Blue
try {
    $prediction = Invoke-RestMethod -Uri "$baseUrl/prediction"
    Write-Host "   ✅ תחזית התקבלה" -ForegroundColor Green
    Write-Host "   🎯 מספרים מומלצים: $($prediction.prediction.recommended_numbers -join ', ')" -ForegroundColor Magenta
    Write-Host "   📊 ביטחון: $($prediction.prediction.confidence_score * 100)%" -ForegroundColor White
    Write-Host "   🧠 אסטרטגיה: $($prediction.prediction.strategy)" -ForegroundColor White
} catch {
    Write-Host "   ❌ לא ניתן לקבל תחזית" -ForegroundColor Red
}

Write-Host "`n🎲 סימולציית הימור..." -ForegroundColor Blue
try {
    $betData = @{
        numbers = @(12, 24, 36, 48, 55)
        bet_amount = 10
    } | ConvertTo-Json
    
    $simulation = Invoke-RestMethod -Uri "$baseUrl/simulate-bet" -Method Post -Body $betData -ContentType "application/json"
    Write-Host "   ✅ סימולציה הושלמה" -ForegroundColor Green
    
    if ($simulation.is_winner) {
        Write-Host "   🎉 זכית! סכום: $($simulation.prize_won)" -ForegroundColor Green
    } else {
        Write-Host "   😢 לא זכית הפעם. הפסד: $($simulation.bet_amount)" -ForegroundColor Red
    }
    
    Write-Host "   📊 מספרים שלך: $($simulation.user_numbers -join ', ')" -ForegroundColor White
    Write-Host "   🏆 מספרים מנצחים: $($simulation.winning_numbers -join ', ')" -ForegroundColor White
    Write-Host "   🤝 התאמות: $($simulation.matches)" -ForegroundColor White
} catch {
    Write-Host "   ❌ לא ניתן להריץ סימולציה" -ForegroundColor Red
}

Write-Host "`n🎯 יצירת תחזית במערכת..." -ForegroundColor Blue
try {
    $predictionUrl = "$baseUrl/create-prediction-from-lottery?title=תחזית%20לוטו%20ראשונה&description=תחזית%20מבוססת%20AI&points_staked=100&user_id=1"
    $createdPrediction = Invoke-RestMethod -Uri $predictionUrl -Method Post
    Write-Host "   ✅ תחזית נוצרה במערכת!" -ForegroundColor Green
    Write-Host "   📝 כותרת: $($createdPrediction.prediction_created.title)" -ForegroundColor White
    Write-Host "   🎯 מספרים: $($createdPrediction.prediction_created.predicted_numbers -join ', ')" -ForegroundColor White
    Write-Host "   💰 נקודות שהושקעו: $($createdPrediction.prediction_created.points_staked)" -ForegroundColor White
} catch {
    Write-Host "   ❌ לא ניתן ליצור תחזית" -ForegroundColor Red
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "🎉 הדגמה הושלמה בהצלחה!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n🌐 כתובות נוספות:" -ForegroundColor Yellow
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Lottery Health: http://localhost:8000/api/v1/lottery/health" -ForegroundColor White
Write-Host "   Lottery Analysis: http://localhost:8000/api/v1/lottery/analysis" -ForegroundColor White

Write-Host "`n🚀 מה הלאה:" -ForegroundColor Magenta
Write-Host "   1. פתח http://localhost:8000/docs וראה את endpoints החדשים" -ForegroundColor Gray
Write-Host "   2. נסה את ה-API דרך ה-docs" -ForegroundColor Gray
Write-Host "   3. המשך לפיתוח אלגוריתמים מתקדמים יותר" -ForegroundColor Gray
Write-Host "   4. הוסף חיבור ל-API אמיתי של מפעל הפיס" -ForegroundColor Gray

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "✅ שלב 4 הושלם - אינטגרציה עם מפעל הפיס!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
