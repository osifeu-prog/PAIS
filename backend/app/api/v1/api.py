from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, predictions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# TODO: הוסף כאן את שאר הראוטרים
