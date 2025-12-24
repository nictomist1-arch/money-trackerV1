from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app import models, schemas

class TransactionCRUD:
    @staticmethod
    def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[models.Transaction]:
        """Получить транзакцию по ID с проверкой владельца"""
        return db.query(models.Transaction).filter(
            and_(
                models.Transaction.id == transaction_id,
                models.Transaction.user_id == user_id
            )
        ).first()

    @staticmethod
    def get_transactions(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[models.Transaction]:
        """Получить список транзакций с фильтрацией"""
        query = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id
        )
        
        # Применяем фильтры если есть
        if filters:
            if filters.get('start_date'):
                query = query.filter(models.Transaction.date >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(models.Transaction.date <= filters['end_date'])
            if filters.get('category_id'):
                query = query.filter(models.Transaction.category_id == filters['category_id'])
            if filters.get('type'):
                query = query.filter(models.Transaction.type == filters['type'])
            if filters.get('min_amount'):
                query = query.filter(models.Transaction.amount >= filters['min_amount'])
            if filters.get('max_amount'):
                query = query.filter(models.Transaction.amount <= filters['max_amount'])
        
        return query.order_by(desc(models.Transaction.date)).offset(skip).limit(limit).all()

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
        user_id: int,
        transaction_update: schemas.TransactionUpdate
    ) -> Optional[models.Transaction]:
        """Обновить транзакцию"""
        db_transaction = TransactionCRUD.get_transaction(db, transaction_id, user_id)
        
        if db_transaction:
            update_data = transaction_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(db_transaction, field, value)
            
            db.commit()
            db.refresh(db_transaction)
        
        return db_transaction

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
        """Удалить транзакцию"""
        db_transaction = TransactionCRUD.get_transaction(db, transaction_id, user_id)
        
        if db_transaction:
            db.delete(db_transaction)
            db.commit()
            return True
        
        return False

    @staticmethod
    def get_transaction_stats(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Получить статистику по транзакциям"""
        query = db.query(
            models.Transaction.type,
            func.count(models.Transaction.id).label('count'),
            func.sum(models.Transaction.amount).label('total'),
            func.avg(models.Transaction.amount).label('average')
        ).filter(
            models.Transaction.user_id == user_id
        )
        
        if start_date:
            query = query.filter(models.Transaction.date >= start_date)
        if end_date:
            query = query.filter(models.Transaction.date <= end_date)
        
        stats = query.group_by(models.Transaction.type).all()
        
        result = {
            'total_income': Decimal('0'),
            'total_expense': Decimal('0'),
            'income_count': 0,
            'expense_count': 0,
            'net_balance': Decimal('0'),
            'total_transactions': 0
        }
        
        for stat in stats:
            if stat.type == 'income':
                result['total_income'] = stat.total or Decimal('0')
                result['income_count'] = stat.count or 0
            elif stat.type == 'expense':
                result['total_expense'] = stat.total or Decimal('0')
                result['expense_count'] = stat.count or 0
        
        result['net_balance'] = result['total_income'] - result['total_expense']
        result['total_transactions'] = result['income_count'] + result['expense_count']
        
        return result

    @staticmethod
    def get_recent_transactions(
        db: Session,
        user_id: int,
        days: int = 30,
        limit: int = 50
    ) -> List[models.Transaction]:
        """Получить последние транзакции за указанное количество дней"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return db.query(models.Transaction).filter(
            and_(
                models.Transaction.user_id == user_id,
                models.Transaction.date >= start_date
            )
        ).order_by(desc(models.Transaction.date)).limit(limit).all()

    @staticmethod
    def get_transactions_by_category(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Получить транзакции сгруппированные по категориям"""
        query = db.query(
            models.Category.name,
            models.Category.icon,
            models.Transaction.type,
            func.sum(models.Transaction.amount).label('total'),
            func.count(models.Transaction.id).label('count')
        ).join(
            models.Category,
            models.Transaction.category_id == models.Category.id
        ).filter(
            models.Transaction.user_id == user_id
        )
        
        if start_date:
            query = query.filter(models.Transaction.date >= start_date)
        if end_date:
            query = query.filter(models.Transaction.date <= end_date)
        
        return query.group_by(
            models.Category.name,
            models.Category.icon,
            models.Transaction.type
        ).all()