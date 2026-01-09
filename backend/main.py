from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.api.v1.api import api_router

# יצירת טבלאות במסד הנתונים
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prediction Point API",
    description="API for managing predictions and user points with JWT authentication",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# הגדרת CORS מלאה
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# הכללת routers דרך api_router המאוחד
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Prediction Point API",
        "status": "online",
        "version": "2.1.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
