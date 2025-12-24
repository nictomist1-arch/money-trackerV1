from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from decimal import Decimal
from enum import Enum

# ========== ENUMS ==========
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

# ========== BASE SCHEMAS ==========
class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

# ========== USER SCHEMAS ==========
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseResponse, UserBase):
    is_active: bool

# ========== CATEGORY SCHEMAS ==========
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: CategoryType
    icon: Optional[str] = "💰"
    color: Optional[str] = "#4CAF50"

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(BaseResponse, CategoryBase):
    user_id: int

# ========== TRANSACTION SCHEMAS ==========
class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    date: datetime
    description: Optional[str] = None
    type: TransactionType
    category_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[datetime] = None
    description: Optional[str] = None
    type: Optional[TransactionType] = None
    category_id: Optional[int] = None

class TransactionResponse(BaseResponse, TransactionBase):
    user_id: int
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    updated_at: Optional[datetime] = None

class PaginatedTransactions(PaginatedResponse[TransactionResponse]):
    summary: dict = {}

# ========== AUTH SCHEMAS ==========
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None