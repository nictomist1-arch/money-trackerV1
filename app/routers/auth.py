from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/test")
def test_auth():
    return {"message": "Auth router works!"}
from fastapi import APIRouter, HTTPException, status
from app import schemas

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register")
async def register(user: schemas.UserCreate):
    """Регистрация пользователя (заглушка)"""
    return {
        "message": "User registered successfully",
        "username": user.username,
        "email": user.email
    }

@router.post("/login")
async def login(credentials: schemas.UserLogin):
    """Вход пользователя (заглушка)"""
    return {
        "access_token": "test_token",
        "token_type": "bearer"
    }

@router.get("/test")
async def test_auth():
    """Тестовый эндпоинт"""
    return {"message": "Auth router работает"}