from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    numbers = Column(String(100), nullable=False)
    lottery_type = Column(String(50), default="Chance")
    prediction_date = Column(DateTime, default=datetime.utcnow)
    draw_date = Column(DateTime, nullable=False)
    points_awarded = Column(Integer, default=0)
    is_correct = Column(Boolean, default=None, nullable=True)
    
    user = relationship("User", back_populates="predictions")

class MarketItem(Base):
    __tablename__ = "market_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    item_type = Column(String(50))
    stock = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, prediction, reward, etc.
    amount = Column(Integer, nullable=False)
    description = Column(Text)
    reference_id = Column(Integer, nullable=True)  # ID of prediction/market item
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
