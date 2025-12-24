import os
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    """
    Получаем URL базы данных.
    На Render используем DATABASE_URL, локально собираем из компонентов.
    """
    # Пробуем получить полный DATABASE_URL из переменных окружения
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Проверяем и исправляем URL если нужно
        try:
            # Парсим URL для проверки
            parsed = urllib.parse.urlparse(database_url)
            
            # Если порт пустой, добавляем стандартный
            if not parsed.port:
                if parsed.scheme == 'postgresql':
                    new_url = database_url.replace('@', ':5432@')
                    print(f"Fixed database URL (added port 5432)")
                    return new_url
            
            return database_url
        except Exception as e:
            print(f"Error parsing DATABASE_URL: {e}")
    
    # Если нет DATABASE_URL, собираем из компонентов (для локальной разработки)
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    
    # Обрабатываем порт
    port_str = os.getenv("POSTGRES_PORT", "5432")
    try:
        port = int(port_str) if port_str and port_str.lower() != 'none' else 5432
    except ValueError:
        port = 5432
    
    db = os.getenv("POSTGRES_DB", "money_tracker")
    
    # Формируем URL
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Получаем URL базы данных
DATABASE_URL = get_database_url()

# Логируем URL (без пароля для безопасности)
safe_url = DATABASE_URL.split('@')[0] + '@' + '***'
print(f"Database URL: {safe_url}")

# Создаем engine с настройками для корректной работы с UTF-8
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False,
        # Настройки для корректной работы с кодировкой
        connect_args={
            'client_encoding': 'utf8'
        } if DATABASE_URL.startswith('postgresql') else {}
    )
    
    print("✅ Database engine created successfully")
    
except Exception as e:
    print(f"❌ Error creating database engine: {e}")
    
    # Fallback: используем SQLite для тестирования
    print("⚠️ Using SQLite as fallback database")
    DATABASE_URL = "sqlite:///./money_tracker.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
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

def check_database_connection() -> str:
    """Проверка подключения к базе данных"""
    try:
        db = SessionLocal()
        # Используем text() для текстового SQL выражения
        result = db.execute(text("SELECT 1"))
        db.close()
        
        # Проверяем результат
        if result.scalar() == 1:
            return "✅ Подключена"
        else:
            return "⚠️ Подключена, но непредвиденный результат"
            
    except Exception as e:
        error_msg = str(e)
        
        # Упрощаем сообщение об ошибке
        if "password authentication failed" in error_msg.lower():
            return "❌ Ошибка аутентификации: неверный пароль"
        elif "connection" in error_msg.lower():
            return "❌ Ошибка подключения к серверу БД"
        elif "does not exist" in error_msg.lower():
            return "❌ База данных не существует"
        elif "utf-8" in error_msg.lower():
            return "⚠️ Проблемы с кодировкой (используется fallback SQLite)"
        else:
            # Обрезаем длинные сообщения
            if len(error_msg) > 50:
                error_msg = error_msg[:50] + "..."
            return f"❌ Ошибка: {error_msg}"