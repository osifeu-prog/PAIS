from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import func
import datetime
from typing import List, Optional
from pydantic import BaseModel

from database import engine, get_db
from models import Base, User, Prediction, MarketItem, Transaction

# ????? ?????? ???? ???????
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="?? Prediction Point System API",
    description="Advanced prediction and trading platform",
    version="2.0.0"
)

# ????? CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    points: float
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

class PredictionCreate(BaseModel):
    title: str
    description: str
    event_type: str
    predicted_outcome: str
    confidence: float
    points_staked: float
    deadline: datetime.datetime

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    event_type: str
    predicted_outcome: str
    confidence: float
    points_staked: float
    status: str
    deadline: datetime.datetime
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

# Routes ??????? (?????? ??????)
@app.get("/")
async def root():
    return {
        "message": "?? Prediction Point System API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.datetime.utcnow(),
        "database": "SQLite (Active)",
        "endpoints": [
            "/health",
            "/api/v1/test",
            "/api/v1/users",
            "/api/v1/predictions",
            "/api/v1/market",
            "/api/v1/stats",
            "/docs"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow(),
        "service": "prediction-api",
        "database": "SQLite (Connected)",
        "version": "2.0.0"
    }

@app.get("/api/v1/test")
async def api_test():
    return {
        "status": "success",
        "message": "API v2 with database is working! ??",
        "timestamp": datetime.datetime.utcnow(),
        "version": "2.0.0"
    }

# API ?? ???? ??????
@app.get("/api/v1/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).limit(10).all()
    return users

@app.post("/api/v1/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ????? ?? ????? ??? ????
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # ????? ????? ??? (????? - ?? ?????? ????? ??????)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=f"hashed_{user.password}",  # ?? ?????? ?????? ??????
        points=1000.0
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # ????? ???????? ???????
    transaction = Transaction(
        user_id=db_user.id,
        type="bonus",
        amount=1000.0,
        description="Welcome bonus points"
    )
    db.add(transaction)
    db.commit()
    
    return db_user

@app.get("/api/v1/predictions", response_model=List[PredictionResponse])
async def get_predictions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return predictions

@app.post("/api/v1/predictions", response_model=PredictionResponse)
async def create_prediction(
    prediction: PredictionCreate,
    user_id: int = 1,  # ????? - ?? ???? ?-authentication
    db: Session = Depends(get_db)
):
    # ????? ?? ?????? ?? ????? ??????
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.points < prediction.points_staked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points"
        )
    
    # ????? ?????? ??????
    user.points -= prediction.points_staked
    
    # ????? ??????
    db_prediction = Prediction(
        user_id=user_id,
        title=prediction.title,
        description=prediction.description,
        event_type=prediction.event_type,
        predicted_outcome=prediction.predicted_outcome,
        confidence=prediction.confidence,
        points_staked=prediction.points_staked,
        deadline=prediction.deadline
    )
    
    db.add(db_prediction)
    
    # ????? ????????
    transaction = Transaction(
        user_id=user_id,
        type="prediction",
        amount=-prediction.points_staked,
        description=f"Prediction staked: {prediction.title}",
        reference_id=db_prediction.id
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction

@app.get("/api/v1/market")
async def get_market_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    items = db.query(MarketItem).filter(
        MarketItem.status == "available"
    ).order_by(MarketItem.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "count": len(items),
        "note": "Market items from database"
    }

@app.get("/api/v1/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_predictions = db.query(Prediction).count()
    total_points = db.query(func.sum(User.points)).scalar() or 0
    
    # ????? ?????? ??????
    active_predictions = db.query(Prediction).filter(
        Prediction.status == "pending"
    ).count()
    
    # ????? ????? ??????
    avg_points = total_points / total_users if total_users > 0 else 0
    
    return {
        "stats": {
            "total_users": total_users,
            "total_predictions": total_predictions,
            "total_points_in_circulation": total_points,
            "active_predictions": active_predictions,
            "average_points_per_user": round(avg_points, 2)
        },
        "timestamp": datetime.datetime.utcnow(),
        "database_stats": "Live data from SQLite"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


