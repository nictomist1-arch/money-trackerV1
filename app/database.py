# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

def get_database_url() -> str:
    """
    Получаем URL базы данных.
    На Render используем DATABASE_URL, локально собираем из компонентов.
    """
    # Пробуем получить полный DATABASE_URL из переменных окружения
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Parse the database URL to ensure it's valid
        return database_url
    
    # Если нет DATABASE_URL, собираем из компонентов
    # Это для локальной разработки
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    
    # Обрабатываем порт - преобразуем в число или используем по умолчанию
    port_str = os.getenv("POSTGRES_PORT", "5432")
    try:
        port = int(port_str) if port_str else 5432
    except ValueError:
        port = 5432
    
    db = os.getenv("POSTGRES_DB", "money_tracker")
    
    # Формируем URL
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Получаем URL базы данных
DATABASE_URL = get_database_url()

# Проверяем URL (для отладки)
print(f"Database URL: {DATABASE_URL.split('@')[0]}@*****")

# Создаем engine с настройками
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()