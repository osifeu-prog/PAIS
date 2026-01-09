from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register")
async def register():
    return {"message": "Register endpoint - to be implemented"}

@router.post("/login")
async def login():
    return {"message": "Login endpoint - to be implemented"}

@router.get("/me")
async def read_users_me():
    return {"message": "Get current user endpoint - to be implemented"}
