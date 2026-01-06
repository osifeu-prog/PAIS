from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.database import init_db

# יבוא הראוטרים החדשים
from app.api.v1.endpoints import auth
# TODO: נוסיף כאן את הראוטרים הקיימים כשנעדכן אותם

@asynccontextmanager
async def lifespan(app: FastAPI):
    # אתחול בזמן ההרצה
    print("🔄 Initializing database...")
    init_db()
    print("✅ Database initialized!")
    yield
    # נקיון בזמן הכיבוי
    print("🔄 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Prediction Point API with Authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
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

# TODO: נוסיף כאן את הראוטרים הישנים כשנעדכן אותם ל-v2

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
