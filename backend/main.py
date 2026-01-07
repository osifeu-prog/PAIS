from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.api.v1.endpoints import auth

# יצירת טבלאות במסד הנתונים
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prediction Point API",
    description="API for managing predictions and user points with JWT authentication",
    version="2.0.0",
)

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# הכללת routers
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Prediction Point API",
        "status": "online",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
