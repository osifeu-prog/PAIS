from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db
from app.api.v1.endpoints import auth, users, predictions

# אתחול מסד הנתונים
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Prediction Point API with Authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# הרשמת הראוטרים
app.include_router(auth.router, prefix="/api/v1")
# TODO: הוסף כאן את שאר הראוטרים לאחר שתיצור אותם

@app.get("/")
async def root():
    return {
        "message": "Welcome to PAIS - Prediction Point API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
