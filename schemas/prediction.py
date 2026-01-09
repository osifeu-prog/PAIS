from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PredictionBase(BaseModel):
    title: str
    description: Optional[str] = None
    predicted_outcome: str

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
