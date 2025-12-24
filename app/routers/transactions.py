# app/routers/transactions.py
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
from app.crud import transaction as crud_transaction

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("/", response_model=List[schemas.TransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category_id: Optional[int] = None,
    type: Optional[schemas.TransactionType] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить список транзакций пользователя.
    
    Возможна фильтрация по:
    - Дате (start_date, end_date)
    - Категории (category_id)
    - Типу (income/expense)
    - Сумме (min_amount, max_amount)
    """
    transactions = crud_transaction.get_transactions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        type=type,
        min_amount=min_amount,
        max_amount=max_amount
    )
    return transactions

@router.post("/", 
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создать новую транзакцию.
    
    Поля:
    - **amount**: Сумма (должна быть больше 0)
    - **date**: Дата транзакции
    - **description**: Описание (опционально)
    - **type**: Тип (income или expense)
    - **category_id**: ID категории (опционально)
    """
    # Проверяем, существует ли категория (если указана)
    if transaction.category_id:
        category = db.query(models.Category).filter(
            and_(
                models.Category.id == transaction.category_id,
                models.Category.user_id == current_user.id
            )
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с ID {transaction.category_id} не найдена"
            )
        
        # Проверяем соответствие типа категории и транзакции
        if category.type.value != transaction.type.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Тип категории '{category.type}' не соответствует типу транзакции '{transaction.type}'"
            )
    
    # Создаем транзакцию
    db_transaction = crud_transaction.create_transaction(
        db=db,
        transaction=transaction,
        user_id=current_user.id
    )
    
    return db_transaction

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить транзакцию по ID.
    
    Пользователь может получить только свои транзакции.
    """
    transaction = crud_transaction.get_transaction(db, transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена"
        )
    
    # Проверяем, принадлежит ли транзакция текущему пользователю
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой транзакции"
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновить транзакцию.
    
    Пользователь может обновить только свои транзакции.
    """
    transaction = crud_transaction.get_transaction(db, transaction_id)
    
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена"
        )
    
    # Проверяем категорию (если указана)
    if transaction_update.category_id:
        category = db.query(models.Category).filter(
            and_(
                models.Category.id == transaction_update.category_id,
                models.Category.user_id == current_user.id
            )
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с ID {transaction_update.category_id} не найдена"
            )
    
    updated_transaction = crud_transaction.update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction_update=transaction_update
    )
    
    return updated_transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удалить транзакцию.
    
    Пользователь может удалить только свои транзакции.
    """
    transaction = crud_transaction.get_transaction(db, transaction_id)
    
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена"
        )
    
    crud_transaction.delete_transaction(db, transaction_id)

@router.get("/stats/dashboard")
def get_dashboard_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить статистику для дашборда.
    
    Включает:
    - Общий доход
    - Общий расход
    - Баланс
    - Самую дорогую категорию
    - Количество транзакций
    """
    if not start_date:
        # По умолчанию за последние 30 дней
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Общий доход
    total_income = db.query(func.sum(models.Transaction.amount)).filter(
        and_(
            models.Transaction.user_id == current_user.id,
            models.Transaction.type == "income",
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date
        )
    ).scalar() or Decimal('0')
    
    # Общий расход
    total_expense = db.query(func.sum(models.Transaction.amount)).filter(
        and_(
            models.Transaction.user_id == current_user.id,
            models.Transaction.type == "expense",
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date
        )
    ).scalar() or Decimal('0')
    
    # Баланс
    balance = total_income - total_expense
    
    # Самая дорогая категория расходов
    most_expensive_category = db.query(
        models.Category.name,
        func.sum(models.Transaction.amount).label("total")
    ).join(
        models.Transaction,
        models.Transaction.category_id == models.Category.id
    ).filter(
        and_(
            models.Transaction.user_id == current_user.id,
            models.Transaction.type == "expense",
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date
        )
    ).group_by(models.Category.name).order_by(desc("total")).first()
    
    # Количество транзакций
    transactions_count = db.query(func.count(models.Transaction.id)).filter(
        and_(
            models.Transaction.user_id == current_user.id,
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date
        )
    ).scalar() or 0
    
    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "balance": float(balance),
        "most_expensive_category": most_expensive_category[0] if most_expensive_category else None,
        "transactions_count": transactions_count,
        "start_date": start_date,
        "end_date": end_date
    }