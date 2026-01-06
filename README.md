📋 PAIS - Prediction Point API | מסמך מעקב פרויקט
🎯 מטרת הפרויקט
פיתוח מערכת מלאה לניהול תחזיות (Prediction Point) עם API, מסד נתונים, וממשק משתמש. הפרויקט מתארח ב-Railway ומתעדכן אוטומטית עם כל דחיפה ל-GitHub.

🔄 נוהל עבודה
קבלת פקודה - אתה מקבל ממני פקודת PowerShell מוכנה להעתקה

הרצה ושיתוף פלט - מריץ את הפקודה ומשתף את כל הפלט

אימות ותיקון - אני מאמת את התוצאות ונותן פקודות תיקון אם נדרש

עדכון README - מעדכן מסמך זה עם הסטטוס החדש

דחיפה ל-GitHub - מעלה את כל השינויים ל-repository

📊 סטטוס נוכחי (עדכון אחרון: 06.01.2026)
✅ מה הושלם
API בסיסי - FastAPI עם endpoints עיקריים

פריסה ל-Railway - המערכת פעילה בכתובת: https://pais-production.up.railway.app

תיעוד API אוטומטי - Swagger UI זמין ב: /docs

מסד נתונים - SQLite עם טבלאות users ו-predictions

משתני סביבה - הוגדרו ב-Railway:

DATABASE_URL - חיבור למסד נתונים

ENVIRONMENT - סביבת ריצה (production)

PORT - פורט האזנה

SECRET_KEY - מפתח הצפנה

🚧 מה נשאר להשלמה
Frontend - ממשק משתמש ב-React (תיקיית frontend קיימת אך ריקה)

Authentication - מערכת הרשאות ומשתמשים

Testing - בדיקות אוטומטיות ל-API

Monitoring - מערכת ניטור וביצועים

Documentation - תיעוד מפורט למפתחים

🌐 פרטי פריסה - Railway
🔗 קישורים חיים
API Production: https://pais-production.up.railway.app

תיעוד API: https://pais-production.up.railway.app/docs

בריאות מערכת: https://pais-production.up.railway.app/health

GitHub Repository: https://github.com/osifeu-prog/PAIS

⚙️ תצורת Railway (Service Variables)
text
DATABASE_URL    : הוגדר (חיבור למסד נתונים)
ENVIRONMENT     : production
PORT            : הוגדר
SECRET_KEY      : הוגדר
📁 מבנה הפרויקט הנוכחי
text
C:\Users\Giga Store\Downloads\
├── PAIS-Final/                 # ליבת הפרויקט
│   ├── backend/
│   │   └── main.py            # FastAPI application (גרסה 1.0.0)
│   ├── requirements.txt       # תלויות Python
│   ├── railway.toml          # הגדרות פריסה ל-Railway
│   └── .gitignore            # קבצים להתעלמות
├── frontend/                  # ממשק משתמש עתידי (React)
└── README.md                 # קובץ זה
🔌 נקודות קצה פעילות (API Endpoints)
Method	נתיב	תיאור	סטטוס
GET	/	דף הבית	✅ פעיל
GET	/health	בדיקת בריאות המערכת	✅ פעיל
GET	/api/users	קבלת רשימת משתמשים	✅ פעיל
POST	/api/users	יצירת משתמש חדש	✅ פעיל
GET	/api/users/{user_id}	קבלת משתמש ספציפי	✅ פעיל
POST	/api/predictions	יצירת תחזית חדשה	✅ פעיל
GET	/api/predictions	קבלת כל התחזיות	✅ פעיל
GET	/api/predictions/{prediction_id}	קבלת תחזית ספציפית	✅ פעיל
PUT	/api/predictions/{prediction_id}	עדכון תחזית	✅ פעיל
🚀 הוראות הרצה מקומית
powershell
# התקנת תלויות
cd "C:\Users\Giga Store\Downloads\PAIS-Final"
pip install -r requirements.txt

# הרצת השרת
cd backend
uvicorn main:app --reload

# הגעה לתיעוד API
# http://localhost:8000/docs
📈 שלבים עתידיים
שלב 1: הרחבת ה-API
הוספת endpoints לסטטיסטיקות

שיפור מערכת הניקוד (points)

הוספת חיפוש וסינון מתקדם

שלב 2: פיתוח Frontend
יצרת ממשק React בסיסי

חיבור ל-API

עיצוב responsive

שלב 3: אבטחה
הוספת JWT authentication

הגבלת גישה לפי הרשאות

הגנה מפני התקפות נפוצות

שלב 4: ניטור ובדיקות
הוספת logging מתקדם

יצירת בדיקות אוטומטיות

ניטור ביצועים

🔧 פתרון בעיות נפוצות
בעיית Git Authentication
powershell
# אם git push נכשל:
git remote set-url origin https://[YOUR_TOKEN]@github.com/osifeu-prog/PAIS.git
git push origin main
בעיות ב-Railway
בדוק את ה-Logs ב-Railway Dashboard

וודא שכל ה-Variables הוגדרו נכון

חכה 1-2 דקות אחרי דחיפה לעדכון

📞 תמיכה וקשר
דיווח באגים: GitHub Issues

עדכוני סטטוס: מסמך README זה

נוהל עבודה: העדפה על פקודות PowerShell בודדות ופשוטות

הערה חשובה: מסמך זה מתעדכן לאחר כל שינוי משמעותי בפרויקט. עדכון אחרון בוצע לאחר השלמת פריסת ה-API הבסיסי ל-Railway והגדרת משתני הסביבה הנדרשים. השיחה הבאה תתמקד בהרחבת ה-API או בפיתוח ה-frontend לפי בחירתך.**

💾 פקודה ליצירת קובץ זה
powershell
cd "C:\Users\Giga Store\Downloads"
@'
[הדבק כאן את כל התוכן שלמעלה]
'@ | Out-File "README.md" -Encoding UTF8
Write-Host "✅ README.md נוצר בהצלחה!" -ForegroundColor Green
פרויקט PAIS נמצא על המסלול הנכון. בשיחה הבאה נוכל להתמקד בכל אחת מהמשימות שנותרו ברשימה. 🚀

