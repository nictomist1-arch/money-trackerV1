# app/main.py - Упрощенная версия для тестирования
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("Starting MoneyTracker API...")
    
    # Проверяем переменные окружения
    print(f"DEBUG mode: {os.getenv('DEBUG', 'False')}")
    print(f"DATABASE_URL present: {bool(os.getenv('DATABASE_URL'))}")
    
    # Создаем таблицы (если нужно)
    if os.getenv("DEBUG", "false").lower() == "true":
        try:
            from app.database import engine
            from app import models
            models.Base.metadata.create_all(bind=engine)
            print("Database tables created")
        except Exception as e:
            print(f"Database error: {e}")
    
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
    allow_origins=["*"],  # Временно разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем директории, если их нет
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MoneyTracker API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { text-align: center; }
            h1 { color: #333; }
            .status { background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .success { color: green; }
            .error { color: red; }
            .links a { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💰 MoneyTracker API</h1>
            <p>API для отслеживания личных финансов</p>
            
            <div class="status">
                <h2>Статус: <span class="success">Работает ✅</span></h2>
                <p>Версия: 2.0.0</p>
                <p>База данных: {db_status}</p>
            </div>
            
            <div class="links">
                <a href="/api/docs">API Документация</a>
                <a href="/health">Проверка здоровья</a>
                <a href="/api/v1/status">Статус API</a>
            </div>
            
            <div style="margin-top: 40px;">
                <h3>Быстрый старт:</h3>
                <pre><code># Регистрация пользователя
POST /api/v1/auth/register
{
    "username": "user",
    "email": "user@example.com",
    "password": "password123"
}</code></pre>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Проверяем подключение к БД
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = "Подключена ✅"
        db.close()
    except Exception as e:
        db_status = f"Ошибка: {str(e)[:100]}"
    
    html_content = html_content.replace("{db_status}", db_status)
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = "connected"
        db.close()
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
        "health_check": "/health"
    }

# Импортируем роутеры (делаем это в конце, чтобы сначала проверить базу)
try:
    from app.routers import auth, transactions, categories
    
    app.include_router(auth.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)
    
    print("Routers loaded successfully")
except Exception as e:
    print(f"Warning: Could not load routers: {e}")
    # Создаем временные маршруты для тестирования
    
    @app.get("/api/test")
    async def test_endpoint():
        return {"message": "API работает, но роутеры не загружены", "error": str(e)}
    
    @app.get("/api/v1/auth/test")
    async def test_auth():
        return {"message": "Auth router тестовый эндпоинт"}

# Создаем простую страницу для тестирования
@app.get("/test")
async def test_page(request: Request):
    """Тестовая страница"""
    return templates.TemplateResponse(
        "test.html" if os.path.exists("app/templates/test.html") else "index.html",
        {"request": request, "message": "Test page"}
    )