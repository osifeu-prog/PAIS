from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    points = Column(Float, default=1000.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    event_type = Column(String)  # sports, politics, finance, etc.
    predicted_outcome = Column(String)
    actual_outcome = Column(String, nullable=True)
    confidence = Column(Float, default=0.5)  # 0.0 to 1.0
    points_staked = Column(Float, default=0.0)
    points_awarded = Column(Float, nullable=True)
    status = Column(String, default="pending")  # pending, success, failed
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketItem(Base):
    __tablename__ = "market_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    seller_id = Column(Integer, index=True)
    buyer_id = Column(Integer, index=True, nullable=True)
    price = Column(Float)
    category = Column(String)
    status = Column(String, default="available")  # available, sold, pending
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String)  # prediction, market, bonus, transfer
    amount = Column(Float)
    description = Column(String)
    reference_id = Column(Integer, nullable=True)  # ID of prediction/market item
    created_at = Column(DateTime, default=datetime.utcnow)
