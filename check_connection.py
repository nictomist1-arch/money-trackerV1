#!/usr/bin/env python3
"""
Скрипт для проверки подключения к PostgreSQL на Render
"""
import os
import psycopg2
from urllib.parse import urlparse

def test_postgresql_connection():
    """Тестирует подключение к PostgreSQL"""
    
    print("🔍 Проверка подключения к PostgreSQL...")
    
    # Получаем DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return False
    
    print(f"📊 DATABASE_URL: {database_url[:50]}...")
    
    try:
        # Парсим URL
        parsed = urlparse(database_url)
        
        # Подключаемся
        print(f"🔗 Подключаюсь к {parsed.hostname}:{parsed.port or 5432}...")
        
        conn = psycopg2.connect(
            dbname=parsed.path[1:],  # Убираем первый '/'
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            connect_timeout=10
        )
        
        # Проверяем подключение
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ Подключение успешно!")
        print(f"📋 PostgreSQL версия: {version}")
        
        # Проверяем таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Таблиц в базе: {len(tables)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    # Загружаем .env файл если есть
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_postgresql_connection()
    
    if not success:
        print("\n🔄 Пробую альтернативные методы...")
        
        # Пробуем через отдельные переменные
        pg_vars = {
            'PGHOST': os.getenv("PGHOST"),
            'PGPORT': os.getenv("PGPORT"),
            'PGDATABASE': os.getenv("PGDATABASE"),
            'PGUSER': os.getenv("PGUSER"),
            'PGPASSWORD': os.getenv("PGPASSWORD")
        }
        
        print(f"📋 PG* переменные: {pg_vars}")
        
        if all(pg_vars.values()):
            print("✅ Все PG* переменные найдены!")
        else:
            print("❌ Не все PG* переменные установлены")