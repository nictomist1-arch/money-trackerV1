# app/main_fixed.py
from fastapi import FastAPI
import os

# Принудительно устанавливаем DATABASE_URL для Render
if os.getenv("RENDER"):
    os.environ["DATABASE_URL"] = "postgresql://ваш_пользователь:ваш_пароль@ваш_хост:5432/ваша_база"

app = FastAPI()

@app.get("/")
def root():
    db_url = os.getenv("DATABASE_URL", "не установлен")
    return {
        "message": "Fixed PostgreSQL connection",
        "database_url": db_url[:50] + "..." if len(db_url) > 50 else db_url,
        "on_render": bool(os.getenv("RENDER"))
    }