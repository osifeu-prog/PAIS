from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PredictionBase(BaseModel):
    title: str
    description: Optional[str] = None
    predicted_outcome: str

class PredictionCreate(PredictionBase):
    pass

class PredictionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    predicted_outcome: Optional[str] = None
    actual_outcome: Optional[str] = None
    status: Optional[str] = None

class PredictionInDBBase(PredictionBase):
    id: int
    actual_outcome: Optional[str] = None
    status: str
    user_id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Prediction(PredictionInDBBase):
    pass

class PredictionWithUser(PredictionInDBBase):
    from app.schemas.user import UserResponse
    user: UserResponse
