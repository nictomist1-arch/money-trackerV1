from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
 
# Простой путь для SQLite на Windows 
engine = create_engine("sqlite:///money_tracker.db", connect_args={"check_same_thread": False}) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base() 
 
def get_db(): 
    db = SessionLocal() 
    try: 
        yield db 
    finally: 
        db.close() 
