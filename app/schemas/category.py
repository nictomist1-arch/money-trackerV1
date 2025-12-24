from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

from .base import BaseResponse

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: CategoryType
    icon: Optional[str] = "💰"
    color: Optional[str] = "#4CAF50"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[CategoryType] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class CategoryResponse(BaseResponse, CategoryBase):
    user_id: int
    
    class Config:
        from_attributes = True