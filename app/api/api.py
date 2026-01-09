from fastapi import APIRouter
from app.api.endpoints import auth, predictions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
