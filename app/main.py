# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app import models
from app.routers import auth, transactions, categories, budgets
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("Starting MoneyTracker API...")
    
    # Создаем таблицы (в продакшене используем миграции)
    if settings.DEBUG:
        models.Base.metadata.create_all(bind=engine)
    
    print("Database tables created")
    yield
    print("Shutting down MoneyTracker API...")

app = FastAPI(
    title="MoneyTracker API",
    description="API для отслеживания личных финансов",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Регистрируем маршруты
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(budgets.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "MoneyTracker - Управление финансами"}
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Страница дашборда"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Дашборд"}
    )

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья приложения"""
    try:
        # Проверяем подключение к БД
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "money-tracker-api",
        "version": "2.0.0",
        "database": db_status
    }

@app.get("/api/v1/status")
async def get_status():
    """Информация о статусе API"""
    return {
        "service": "MoneyTracker API",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/api/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "transactions": "/api/v1/transactions",
            "categories": "/api/v1/categories",
            "budgets": "/api/v1/budgets"
        }
    }