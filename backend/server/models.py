from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lottery_type = Column(String(50))
    numbers = Column(String(255))
    prediction_date = Column(DateTime, default=func.now())
    draw_date = Column(DateTime)
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="predictions")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(String(50))
    amount = Column(Integer)
    description = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
