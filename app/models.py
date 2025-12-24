# app/models.py
from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, 
    String, Text, DateTime, Float, Numeric, 
    Enum, CheckConstraint, Index, func
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Category(Base):
    """Модель категории расходов/доходов"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum('income', 'expense', name='category_type'), nullable=False)
    icon = Column(String(50), default="💰")
    color = Column(String(7), default="#4CAF50")  # HEX цвет
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")

    # Индексы
    __table_args__ = (
        Index('ix_categories_user_type', 'user_id', 'type'),
        UniqueConstraint('user_id', 'name', name='unique_user_category'),
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"


class Transaction(Base):
    """Модель транзакции (расход/доход)"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    description = Column(Text)
    type = Column(Enum('income', 'expense', name='transaction_type'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    # Индексы и ограничения
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
        Index('ix_transactions_user_date', 'user_id', 'date'),
        Index('ix_transactions_category_date', 'category_id', 'date'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, type='{self.type}')>"


class Budget(Base):
    """Модель бюджета на категорию"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    period = Column(Enum('daily', 'weekly', 'monthly', 'yearly', name='budget_period'), nullable=False, default='monthly')
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    # Индексы и ограничения
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_budget_amount'),
        CheckConstraint('end_date IS NULL OR end_date > start_date', name='check_budget_dates'),
        UniqueConstraint('user_id', 'category_id', 'period', name='unique_user_category_period'),
        Index('ix_budgets_user_period', 'user_id', 'period'),
    )

    def __repr__(self):
        return f"<Budget(id={self.id}, amount={self.amount}, period='{self.period}')>"