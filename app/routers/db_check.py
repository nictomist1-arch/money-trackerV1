from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, check_database_connection

router = APIRouter(prefix="/api/v1/db", tags=["database"])

@router.get("/check")
async def check_db_connection(db: Session = Depends(get_db)):
    """Проверка подключения к базе данных"""
    try:
        # Простой запрос для проверки
        result = db.execute("SELECT version()")
        db_version = result.fetchone()[0]
        
        return {
            "status": "connected",
            "database": "PostgreSQL",
            "version": db_version.split(',')[0] if db_version else "Unknown",
            "message": "✅ База данных подключена успешно"
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "database": "Unknown",
            "version": "Unknown",
            "error": str(e)[:100],  # Обрезаем длинное сообщение
            "message": "❌ Не удалось подключиться к базе данных"
        }

@router.get("/tables")
async def list_tables(db: Session = Depends(get_db)):
    """Список таблиц в базе данных"""
    try:
        # Запрос для получения списка таблиц (PostgreSQL)
        result = db.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = [row[0] for row in result.fetchall()]
        
        return {
            "status": "success",
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        return {
            "status": "error",
            "tables": [],
            "error": str(e)[:100],
            "message": "Не удалось получить список таблиц"
        }