from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
import sqlite3
import os

# הגדרת האפליקציה
app = FastAPI(
    title="Prediction Point API",
    description="Simple prediction system",
    version="1.0.0"
)

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# פונקציה ליצירת מסד הנתונים SQLite
def init_db():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()

    # טבלת משתמשים
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 1000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # טבלת תחזיות
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            predicted_value REAL,
            actual_value REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# אתחול DB
init_db()

# מודלים של Pydantic
class UserCreate(BaseModel):
    username: str
    email: str

class PredictionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    predicted_value: float

class PredictionUpdate(BaseModel):
    actual_value: Optional[float] = None
    status: Optional[str] = None

# פונקציה לחיבור ל-DB
def get_db_connection():
    conn = sqlite3.connect('predictions.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== ENDPOINTS ==========

@app.get("/")
async def root():
    return {
        "message": "Prediction Point API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": "prediction-point-api"
    }

# משתמשים
@app.post("/api/users")
async def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (user.username, user.email)
        )
        conn.commit()
        user_id = cursor.lastrowid

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        new_user = cursor.fetchone()
        return dict(new_user)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        conn.close()

@app.get("/api/users")
async def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()

    return [dict(user) for user in users]

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(user)

# תחזיות
@app.post("/api/predictions")
async def create_prediction(prediction: PredictionCreate, user_id: int = 1):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO predictions 
               (user_id, title, description, predicted_value, status) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, prediction.title, prediction.description, 
             prediction.predicted_value, 'pending')
        )
        conn.commit()
        pred_id = cursor.lastrowid

        cursor.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,))
        new_pred = cursor.fetchone()
        return dict(new_pred)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/predictions")
async def get_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, u.username 
        FROM predictions p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    predictions = cursor.fetchall()
    conn.close()

    return [dict(pred) for pred in predictions]

@app.get("/api/predictions/{prediction_id}")
async def get_prediction(prediction_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT p.*, u.username FROM predictions p LEFT JOIN users u ON p.user_id = u.id WHERE p.id = ?",
        (prediction_id,)
    )
    prediction = cursor.fetchone()
    conn.close()

    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return dict(prediction)

@app.put("/api/predictions/{prediction_id}")
async def update_prediction(prediction_id: int, update: PredictionUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # בדיקה אם התחזית קיימת
        cursor.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Prediction not found")

        # עדכון הערכים
        if update.actual_value is not None:
            cursor.execute(
                "UPDATE predictions SET actual_value = ? WHERE id = ?",
                (update.actual_value, prediction_id)
            )
        
        if update.status:
            cursor.execute(
                "UPDATE predictions SET status = ? WHERE id = ?",
                (update.status, prediction_id)
            )

        conn.commit()

        # שליפת הנתונים המעודכנים
        cursor.execute(
            "SELECT p.*, u.username FROM predictions p LEFT JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (prediction_id,)
        )
        updated_pred = cursor.fetchone()
        return dict(updated_pred)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
