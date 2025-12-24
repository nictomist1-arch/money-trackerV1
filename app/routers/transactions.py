from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("/", response_model=schemas.PaginatedTransactions)
def get_transactions(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=200, description="Количество возвращаемых записей"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата (фильтр)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (фильтр)"),
    category_id: Optional[int] = Query(None, description="ID категории (фильтр)"),
    type: Optional[schemas.TransactionType] = Query(None, description="Тип транзакции: income/expense"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Минимальная сумма"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Максимальная сумма"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить список транзакций с возможностью фильтрации.
    """
    # Строим запрос
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    )
    
    # Применяем фильтры
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
    if type:
        query = query.filter(models.Transaction.type == type.value)
    if min_amount:
        query = query.filter(models.Transaction.amount >= min_amount)
    if max_amount:
        query = query.filter(models.Transaction.amount <= max_amount)
    
    # Получаем общее количество
    total = query.count()
    
    # Получаем данные с пагинацией
    transactions = query.order_by(
        desc(models.Transaction.date)
    ).offset(skip).limit(limit).all()
    
    # Преобразуем в response
    items = []
    for transaction in transactions:
        transaction_dict = schemas.TransactionResponse.from_orm(transaction)
        
        # Добавляем информацию о категории
        if transaction.category:
            transaction_dict.category_name = transaction.category.name
            transaction_dict.category_icon = transaction.category.icon
        
        items.append(transaction_dict)
    
    # Рассчитываем статистику
    income_query = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == 'income'
    )
    expense_query = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == 'expense'
    )
    
    if start_date:
        income_query = income_query.filter(models.Transaction.date >= start_date)
        expense_query = expense_query.filter(models.Transaction.date >= start_date)
    if end_date:
        income_query = income_query.filter(models.Transaction.date <= end_date)
        expense_query = expense_query.filter(models.Transaction.date <= end_date)
    
    total_income = income_query.scalar() or Decimal('0')
    total_expense = expense_query.scalar() or Decimal('0')
    
    # Рассчитываем пагинацию
    pages = (total + limit - 1) // limit if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": limit,
        "pages": pages,
        "summary": {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_balance": float(total_income - total_expense),
            "transaction_count": total
        }
    }

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
    """
    # Проверяем категорию если указана
    if transaction.category_id:
        category = db.query(models.Category).filter(
            models.Category.id == transaction.category_id,
            models.Category.user_id == current_user.id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с ID {transaction.category_id} не найдена"
            )
        
        # Проверяем соответствие типа
        if category.type != transaction.type.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Тип категории '{category.type}' "
                    f"не соответствует типу транзакции '{transaction.type}'"
                )
            )
    
    # Создаем транзакцию
    db_transaction = models.Transaction(
        **transaction.dict(),
        user_id=current_user.id
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Форматируем ответ
    response = schemas.TransactionResponse.from_orm(db_transaction)
    
    if db_transaction.category:
        response.category_name = db_transaction.category.name
        response.category_icon = db_transaction.category.icon
    
    return response

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int = Path(..., description="ID транзакции"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить транзакцию по ID.
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена"
        )
    
    response = schemas.TransactionResponse.from_orm(transaction)
    
    if transaction.category:
        response.category_name = transaction.category.name
        response.category_icon = transaction.category.icon
    
    return response

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int = Path(..., description="ID транзакции"),
    transaction_update: schemas.TransactionUpdate = Depends(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновить транзакцию.
    """
    # Находим транзакцию
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена"
        )
    
    # Проверяем категорию если указана
    if transaction_update.category_id is not None:
        category = db.query(models.Category).filter(
            models.Category.id == transaction_update.category_id,
            models.Category.user_id == current_user.id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с ID {transaction_update.category_id} не найдена"
            )
        
        # Проверяем соответствие типа
        transaction_type = (
            transaction_update.type.value 
            if transaction_update.type 
            else transaction.type
        )
        
        if category.type != transaction_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Тип категории '{category.type}' "
                    f"не соответствует типу транзакции '{transaction_type}'"
                )
            )
    
    # Обновляем поля
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    # Форматируем ответ
    response = schemas.TransactionResponse.from_orm(transaction)
    
    if transaction.category:
        response.category_name = transaction.category.name
        response.category_icon = transaction.category.icon
    
    return response

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int = Path(..., description="ID транзакции"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удалить транзакцию.
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена"
        )
    
    db.delete(transaction)
    db.commit()

@router.get("/stats/summary")
def get_transaction_stats(
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить статистику по транзакциям.
    """
    # Запросы для статистики
    income_query = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == 'income'
    )
    
    expense_query = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == 'expense'
    )
    
    count_query = db.query(func.count(models.Transaction.id)).filter(
        models.Transaction.user_id == current_user.id
    )
    
    # Применяем фильтры по дате
    if start_date:
        income_query = income_query.filter(models.Transaction.date >= start_date)
        expense_query = expense_query.filter(models.Transaction.date >= start_date)
        count_query = count_query.filter(models.Transaction.date >= start_date)
    
    if end_date:
        income_query = income_query.filter(models.Transaction.date <= end_date)
        expense_query = expense_query.filter(models.Transaction.date <= end_date)
        count_query = count_query.filter(models.Transaction.date <= end_date)
    
    total_income = income_query.scalar() or Decimal('0')
    total_expense = expense_query.scalar() or Decimal('0')
    transaction_count = count_query.scalar() or 0
    
    # Рассчитываем среднее
    total_amount = total_income + total_expense
    average_transaction = (
        total_amount / transaction_count 
        if transaction_count > 0 
        else Decimal('0')
    )
    
    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net_balance": float(total_income - total_expense),
        "transaction_count": transaction_count,
        "average_transaction": float(average_transaction),
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }

# ИСПРАВЛЕННЫЙ ЭНДПОИНТ: Используем Path для days в URL
@router.get("/recent/{days}")
def get_recent_transactions(
    days: int = Path(..., ge=1, le=365, description="Количество дней"),
    limit: int = Query(50, ge=1, le=200, description="Лимит записей"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить последние транзакции за указанное количество дней.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.date >= start_date
    ).order_by(
        desc(models.Transaction.date)
    ).limit(limit).all()
    
    items = []
    for transaction in transactions:
        transaction_dict = schemas.TransactionResponse.from_orm(transaction)
        
        if transaction.category:
            transaction_dict.category_name = transaction.category.name
            transaction_dict.category_icon = transaction.category.icon
        
        items.append(transaction_dict)
    
    return {
        "transactions": items,
        "count": len(items),
        "days": days,
        "limit": limit
    }

@router.get("/by-category")
def get_transactions_by_category(
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получить транзакции по категориям.
    """
    query = db.query(
        models.Category.name,
        models.Category.icon,
        models.Transaction.type,
        func.sum(models.Transaction.amount).label('total'),
        func.count(models.Transaction.id).label('count')
    ).join(
        models.Transaction,
        models.Transaction.category_id == models.Category.id
    ).filter(
        models.Transaction.user_id == current_user.id
    )
    
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)
    
    results = query.group_by(
        models.Category.name,
        models.Category.icon,
        models.Transaction.type
    ).all()
    
    categories = []
    for name, icon, type_, total, count in results:
        categories.append({
            "name": name,
            "icon": icon,
            "type": type_,
            "total": float(total) if total else 0.0,
            "count": count or 0
        })
    
    return {
        "categories": categories,
        "count": len(categories),
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }