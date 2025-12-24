# app/crud/transaction.py
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app import models, schemas

class TransactionCRUD:
    @staticmethod
    def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
        """Получить транзакцию по ID"""
        return db.query(models.Transaction).filter(
            models.Transaction.id == transaction_id
        ).first()

    @staticmethod
    def get_transactions(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_id: Optional[int] = None,
        type: Optional[str] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None
    ) -> List[models.Transaction]:
        """Получить список транзакций пользователя с фильтрацией"""
        query = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id
        )
        
        # Применяем фильтры
        if start_date:
            query = query.filter(models.Transaction.date >= start_date)
        if end_date:
            query = query.filter(models.Transaction.date <= end_date)
        if category_id:
            query = query.filter(models.Transaction.category_id == category_id)
        if type:
            query = query.filter(models.Transaction.type == type)
        if min_amount:
            query = query.filter(models.Transaction.amount >= min_amount)
        if max_amount:
            query = query.filter(models.Transaction.amount <= max_amount)
        
        return query.order_by(
            models.Transaction.date.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create_transaction(
        db: Session,
        transaction: schemas.TransactionCreate,
        user_id: int
    ) -> models.Transaction:
        """Создать новую транзакцию"""
        db_transaction = models.Transaction(
            **transaction.dict(),
            user_id=user_id
        )
        
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        return db_transaction

    @staticmethod
    def update_transaction(
        db: Session,
        transaction_id: int,
        transaction_update: schemas.TransactionUpdate
    ) -> Optional[models.Transaction]:
        """Обновить транзакцию"""
        db_transaction = db.query(models.Transaction).filter(
            models.Transaction.id == transaction_id
        ).first()
        
        if db_transaction:
            update_data = transaction_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(db_transaction, field, value)
            
            db.commit()
            db.refresh(db_transaction)
        
        return db_transaction

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        """Удалить транзакцию"""
        db_transaction = db.query(models.Transaction).filter(
            models.Transaction.id == transaction_id
        ).first()
        
        if db_transaction:
            db.delete(db_transaction)
            db.commit()
            return True
        
        return False