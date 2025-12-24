from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

from .base import BaseResponse

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

class UserResponse(BaseResponse, UserBase):
    is_active: bool
    
    class Config:
        from_attributes = True