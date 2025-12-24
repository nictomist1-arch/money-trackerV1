# app/schemas/transaction.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base import PaginatedResponse, BaseResponse

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Сумма транзакции (должна быть > 0)")
    date: datetime = Field(..., description="Дата и время транзакции")
    description: Optional[str] = Field(None, max_length=500, description="Описание транзакции")
    type: TransactionType = Field(..., description="Тип транзакции: income или expense")
    category_id: Optional[int] = Field(None, description="ID категории")

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Сумма должна быть больше 0')
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[TransactionType] = None
    category_id: Optional[int] = None

class TransactionResponse(BaseResponse, TransactionBase):
    user_id: int
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Для фильтрации
class TransactionFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[int] = None
    type: Optional[TransactionType] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None

# Для пагинации
class PaginatedTransactions(PaginatedResponse[TransactionResponse]):
    summary: dict = {}

# Статистика
class TransactionStats(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    transaction_count: int
    average_transaction: Decimal