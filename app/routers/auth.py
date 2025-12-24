from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app import models, schemas
from app.auth import (
    get_password_hash, 
    verify_password,
    create_access_token,
    get_current_user
)
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Проверяем, существует ли пользователь с таким username
    existing_username = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем стандартные категории для пользователя
    default_categories = [
        {"name": "Зарплата", "type": "income", "icon": "💰", "color": "#48bb78"},
        {"name": "Продукты", "type": "expense", "icon": "🛒", "color": "#4299e1"},
        {"name": "Транспорт", "type": "expense", "icon": "🚗", "color": "#ed8936"},
        {"name": "Развлечения", "type": "expense", "icon": "🎬", "color": "#9f7aea"},
        {"name": "Здоровье", "type": "expense", "icon": "🏥", "color": "#f56565"},
    ]
    
    for category_data in default_categories:
        category = models.Category(
            user_id=db_user.id,
            **category_data
        )
        db.add(category)
    
    db.commit()
    
    return db_user

@router.post("/login")
async def login(
    credentials: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    user = db.query(models.User).filter(
        models.User.email == credentials.email
    ).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь деактивирован"
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        }
    }

@router.get("/me")
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "is_active": current_user.is_active
    }

@router.get("/test")
async def test_auth():
    """Тестовый эндпоинт аутентификации"""
    return {
        "message": "Auth router работает",
        "endpoints": [
            "POST /api/v1/auth/register",
            "POST /api/v1/auth/login",
            "GET /api/v1/auth/me"
        ]
    }