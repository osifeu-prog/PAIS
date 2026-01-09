from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.prediction import PredictionCreate, PredictionUpdate, Prediction, PredictionWithUser
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.post("/", response_model=Prediction, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_data: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prediction = Prediction(
        title=prediction_data.title,
        description=prediction_data.description,
        predicted_outcome=prediction_data.predicted_outcome,
        user_id=current_user.id,
        status="pending"
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

@router.get("/", response_model=List[PredictionWithUser])
async def read_predictions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    predictions = db.query(Prediction).join(User).offset(skip).limit(limit).all()
    return predictions

@router.get("/{prediction_id}", response_model=PredictionWithUser)
async def read_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if db_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return db_prediction

@router.put("/{prediction_id}", response_model=Prediction)
async def update_prediction(
    prediction_id: int,
    prediction_update: PredictionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if db_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if db_prediction.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if prediction_update.title is not None:
        db_prediction.title = prediction_update.title
    if prediction_update.description is not None:
        db_prediction.description = prediction_update.description
    if prediction_update.predicted_outcome is not None:
        db_prediction.predicted_outcome = prediction_update.predicted_outcome
    if prediction_update.actual_outcome is not None:
        db_prediction.actual_outcome = prediction_update.actual_outcome
    if prediction_update.status is not None:
        db_prediction.status = prediction_update.status
    
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if db_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if db_prediction.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(db_prediction)
    db.commit()
    return None
