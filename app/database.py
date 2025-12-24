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
    На Render используем DATABASE_URL, локально используем PostgreSQL или SQLite.
    """
    # 1. Проверяем DATABASE_URL от Render
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        print(f"🔗 Found DATABASE_URL from environment")
        
        # Render обычно дает URL вида:
        # postgresql://user:password@host:port/database
        # Проверяем и исправляем если нужно
        
        # Если это PostgreSQL URL от Render
        if database_url.startswith("postgres://"):
            # Конвертируем старый формат в новый
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            print(f"🔄 Converted postgres:// to postgresql://")
        
        # Проверяем порт
        try:
            parsed = urllib.parse.urlparse(database_url)
            if not parsed.port:
                # Добавляем стандартный порт PostgreSQL
                if parsed.scheme == "postgresql":
                    database_url = database_url.replace("://", "://", 1)
                    if "@" in database_url:
                        parts = database_url.split("@")
                        database_url = parts[0] + ":5432@" + parts[1]
                        print(f"➕ Added default port 5432")
        except:
            pass
        
        return database_url
    
    # 2. Проверяем, на Render ли мы (через переменную RENDER)
    is_render = os.getenv("RENDER", "").lower() == "true"
    
    if is_render:
        print("⚠️ Running on Render but DATABASE_URL not found!")
        
        # Пробуем собрать URL из отдельных переменных
        user = os.getenv("PGUSER", "postgres")
        password = os.getenv("PGPASSWORD", "")
        host = os.getenv("PGHOST", "")
        port = os.getenv("PGPORT", "5432")
        database = os.getenv("PGDATABASE", "money_tracker")
        
        if all([user, password, host, database]):
            url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            print(f"🔗 Built database URL from PG* variables")
            return url
    
    # 3. Для локальной разработки - пробуем PostgreSQL
    print("🏠 Local development mode")
    
    # Пробуем подключиться к локальному PostgreSQL
    local_pg_url = "postgresql://postgres:postgres@localhost:5432/money_tracker"
    
    # Проверяем, доступен ли локальный PostgreSQL
    try:
        test_engine = create_engine(local_pg_url)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Local PostgreSQL is available")
        return local_pg_url
    except:
        print("⚠️ Local PostgreSQL not available, using SQLite")
        # Fallback на SQLite
        return "sqlite:///./money_tracker.db"

# Получаем URL базы данных
DATABASE_URL = get_database_url()

# Логируем (без пароля)
def get_safe_url(url):
    """Возвращает безопасную версию URL без пароля"""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.password:
            # Заменяем пароль звездочками
            safe_netloc = parsed.hostname
            if parsed.port:
                safe_netloc += f":{parsed.port}"
            safe_url = urllib.parse.urlunparse(
                (parsed.scheme, safe_netloc, parsed.path, 
                 parsed.params, parsed.query, parsed.fragment)
            )
            return safe_url.replace("://", "://***:***@")
    except:
        pass
    return url

safe_url = get_safe_url(DATABASE_URL)
print(f"📊 Using database: {safe_url}")

# Определяем, используем ли мы SQLite
IS_SQLITE = DATABASE_URL.startswith("sqlite")
print(f"🗄️ Database type: {'SQLite' if IS_SQLITE else 'PostgreSQL'}")

try:
    if IS_SQLITE:
        # Настройки для SQLite
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        # Настройки для PostgreSQL
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                'connect_timeout': 10,
                'application_name': 'money_tracker_api'
            }
        )
    
    print("✅ Database engine created successfully")
    
except Exception as e:
    print(f"❌ Error creating database engine: {e}")
    
    # Финальный fallback на SQLite
    print("🔄 Using SQLite as final fallback")
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

def check_database_connection() -> tuple:
    """Проверка подключения к базе данных"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        
        # Пытаемся определить тип БД
        try:
            db.execute(text("SELECT version()"))
            db_type = "PostgreSQL"
        except:
            db_type = "SQLite"
        
        db.close()
        
        return "✅ Подключена", db_type, True
        
    except Exception as e:
        error_msg = str(e)
        
        # Определяем тип ошибки
        if "OperationalError" in error_msg or "connection" in error_msg.lower():
            return "❌ Ошибка подключения", "Неизвестно", False
        elif IS_SQLITE:
            return "✅ Используется SQLite (fallback)", "SQLite", True
        else:
            return f"❌ Ошибка: {error_msg[:50]}...", "Ошибка", False