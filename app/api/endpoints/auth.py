from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register():
    return {"message": "Register endpoint", "version": "2.1.0"}

@router.post("/login")
async def login():
    return {"message": "Login endpoint", "version": "2.1.0"}

@router.get("/me")
async def read_users_me():
    return {"message": "Get current user", "version": "2.1.0"}
