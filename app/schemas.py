# app/schemas.py
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Enums
class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class BudgetPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# Base schemas
class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# User schemas
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

# Category schemas
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

# Transaction schemas
class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    date: datetime
    description: Optional[str] = None
    type: TransactionType

class TransactionCreate(TransactionBase):
    category_id: Optional[int] = None

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[datetime] = None
    description: Optional[str] = None
    category_id: Optional[int] = None

class TransactionResponse(BaseResponse, TransactionBase):
    user_id: int
    category_id: Optional[int]
    category: Optional[CategoryResponse]
    updated_at: Optional[datetime]

# Budget schemas
class BudgetBase(BaseModel):
    amount: Decimal = Field(..., ge=0)
    period: BudgetPeriod
    start_date: datetime
    end_date: Optional[datetime] = None

class BudgetCreate(BudgetBase):
    category_id: int

class BudgetUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0)
    period: Optional[BudgetPeriod] = None
    end_date: Optional[datetime] = None

class BudgetResponse(BaseResponse, BudgetBase):
    user_id: int
    category_id: int
    category: CategoryResponse
    spent_amount: Optional[Decimal] = 0
    remaining_amount: Optional[Decimal] = 0

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Statistics
class DashboardStats(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    most_expensive_category: Optional[str] = None
    transactions_count: int
    categories_count: int

# Pagination
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int