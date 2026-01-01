from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    points: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

# Prediction Schemas
class PredictionBase(BaseModel):
    numbers: str
    lottery_type: str = "Chance"
    draw_date: datetime

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    user_id: int
    prediction_date: datetime
    points_awarded: int
    is_correct: Optional[bool] = None
    
    class Config:
        from_attributes = True

# Market Schemas
class MarketItemBase(BaseModel):
    name: str
    description: str
    price: int
    item_type: str
    stock: int = 100

class MarketItemCreate(MarketItemBase):
    pass

class MarketItemResponse(MarketItemBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseRequest(BaseModel):
    item_id: int
    quantity: int = 1

# Stats Schemas
class SystemStats(BaseModel):
    total_users: int
    total_predictions: int
    total_points_in_circulation: int
    total_market_transactions: int
    average_prediction_accuracy: float

class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    points: int
    predictions: int

class StatsResponse(BaseModel):
    system_stats: SystemStats
    leaderboard: List[LeaderboardEntry]
    timestamp: datetime
