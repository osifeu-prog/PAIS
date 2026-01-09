from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# TODO: Add predictions router later
# api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
