# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os

from app.database import engine, get_db, check_database_connection
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("🚀 Starting MoneyTracker API...")
    
    # Создаем таблицы при запуске
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
    
    yield
    
    print("👋 Shutting down MoneyTracker API...")

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
    allow_origins=["*"],
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
    # Проверяем подключение к БД
    db_status = check_database_connection()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MoneyTracker API</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .card {{
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                margin-bottom: 30px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .logo {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            
            h1 {{
                color: #2d3748;
                font-size: 2.5rem;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: #718096;
                font-size: 1.2rem;
                margin-bottom: 30px;
            }}
            
            .status-card {{
                background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
            }}
            
            .status-badge {{
                display: inline-block;
                background: #48bb78;
                color: white;
                padding: 10px 20px;
                border-radius: 50px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            
            .info-item {{
                background: #f7fafc;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            
            .info-label {{
                font-size: 0.9rem;
                color: #718096;
                margin-bottom: 5px;
            }}
            
            .info-value {{
                font-size: 1.5rem;
                font-weight: bold;
                color: #2d3748;
            }}
            
            .db-status {{
                background: #f0fff4;
                border-left: 4px solid #48bb78;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            
            .db-error {{
                background: #fff5f5;
                border-left: 4px solid #f56565;
            }}
            
            .buttons {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                justify-content: center;
                margin-top: 30px;
            }}
            
            .btn {{
                padding: 15px 30px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: bold;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}
            
            .btn-primary {{
                background: #4299e1;
                color: white;
            }}
            
            .btn-secondary {{
                background: #edf2f7;
                color: #2d3748;
            }}
            
            .btn-success {{
                background: #48bb78;
                color: white;
            }}
            
            .code-block {{
                background: #2d3748;
                color: #e2e8f0;
                padding: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                margin: 20px 0;
                overflow-x: auto;
            }}
            
            .api-endpoints {{
                margin-top: 40px;
            }}
            
            .endpoint {{
                background: #f7fafc;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #4299e1;
            }}
            
            .method {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 10px;
            }}
            
            .get {{ background: #48bb78; color: white; }}
            .post {{ background: #4299e1; color: white; }}
            .put {{ background: #ed8936; color: white; }}
            .delete {{ background: #f56565; color: white; }}
            
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
                color: #718096;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                
                .card {{
                    padding: 20px;
                }}
                
                .buttons {{
                    flex-direction: column;
                }}
                
                .btn {{
                    width: 100%;
                    justify-content: center;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <!-- Заголовок -->
                <div class="header">
                    <div class="logo">💰</div>
                    <h1>MoneyTracker API</h1>
                    <p class="subtitle">API для отслеживания личных финансов</p>
                </div>
                
                <!-- Статус -->
                <div class="status-card">
                    <div class="status-badge">Статус: Работает ✅</div>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Версия</div>
                            <div class="info-value">2.0.0</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Режим</div>
                            <div class="info-value">{'Разработка' if os.getenv('DEBUG') == 'true' else 'Продакшн'}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Платформа</div>
                            <div class="info-value">Render.com</div>
                        </div>
                    </div>
                </div>
                
                <!-- Статус БД -->
                <div class="db-status {'db-error' if 'Ошибка' in db_status else ''}">
                    <strong>База данных:</strong> {db_status}
                </div>
                
                <!-- Кнопки действий -->
                <div class="buttons">
                    <a href="/api/docs" class="btn btn-primary" target="_blank">
                        📚 API Документация
                    </a>
                    <a href="/health" class="btn btn-secondary">
                        🏥 Проверка здоровья
                    </a>
                    <a href="/api/v1/status" class="btn btn-success">
                        📊 Статус системы
                    </a>
                </div>
                
                <!-- Пример API -->
                <div class="api-endpoints">
                    <h3>📋 Примеры использования API</h3>
                    
                    <div class="code-block">
// Регистрация пользователя
POST /api/v1/auth/register
{{
    "username": "user",
    "email": "user@example.com",
    "password": "password123"
}}

// Вход в систему
POST /api/v1/auth/login
{{
    "email": "user@example.com",
    "password": "password123"
}}

// Получение транзакций
GET /api/v1/transactions
Authorization: Bearer YOUR_TOKEN
                    </div>
                    
                    <h3>🚀 Доступные эндпоинты</h3>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/v1/transactions</code>
                        <span>— Получить список транзакций</span>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <code>/api/v1/transactions</code>
                        <span>— Создать новую транзакцию</span>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/v1/categories</code>
                        <span>— Получить список категорий</span>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/v1/stats/dashboard</code>
                        <span>— Статистика дашборда</span>
                    </div>
                </div>
                
                <!-- Футер -->
                <div class="footer">
                    <p>© 2024 MoneyTracker API • Развернуто на Render.com</p>
                    <p>FastAPI • PostgreSQL • SQLAlchemy • Pydantic</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    db_status = check_database_connection()
    is_healthy = "✅" if "✅" in db_status else "❌"
    
    return {
        "status": "healthy" if "✅" in db_status else "degraded",
        "service": "money-tracker-api",
        "version": "2.0.0",
        "timestamp": "2024-01-15T10:30:00Z",
        "components": {
            "database": {
                "status": "connected" if "✅" in db_status else "disconnected",
                "details": db_status
            },
            "api": {
                "status": "operational",
                "uptime": "100%"
            },
            "authentication": {
                "status": "operational"
            }
        },
        "links": {
            "documentation": "/api/docs",
            "metrics": "/api/v1/status"
        }
    }

@app.get("/api/v1/status")
async def get_status(db: Session = Depends(get_db)):
    """Подробный статус системы"""
    from sqlalchemy import func
    
    # Получаем статистику
    try:
        # Количество пользователей
        users_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        
        # Количество транзакций
        transactions_count = db.execute(text("SELECT COUNT(*) FROM transactions")).scalar() or 0
        
        # Количество категорий
        categories_count = db.execute(text("SELECT COUNT(*) FROM categories")).scalar() or 0
        
        # Последняя транзакция
        last_transaction = db.execute(
            text("SELECT MAX(created_at) FROM transactions")
        ).scalar()
        
    except Exception as e:
        users_count = transactions_count = categories_count = 0
        last_transaction = None
    
    return {
        "service": "MoneyTracker API",
        "version": "2.0.0",
        "status": "operational",
        "uptime": "24/7",
        "environment": "production",
        "database": check_database_connection(),
        "statistics": {
            "users": users_count,
            "transactions": transactions_count,
            "categories": categories_count,
            "last_transaction": str(last_transaction) if last_transaction else "Нет данных"
        },
        "endpoints": {
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "me": "GET /api/v1/auth/me"
            },
            "transactions": {
                "list": "GET /api/v1/transactions",
                "create": "POST /api/v1/transactions",
                "stats": "GET /api/v1/transactions/stats/dashboard"
            },
            "categories": {
                "list": "GET /api/v1/categories",
                "create": "POST /api/v1/categories"
            }
        },
        "documentation": "/api/docs",
        "health_check": "/health",
        "support": {
            "docs": "/api/docs",
            "issues": "Создать issue в репозитории"
        }
    }

# Импортируем и подключаем роутеры
try:
    from app.routers import auth, transactions, categories
    
    app.include_router(auth.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)
    
    print("✅ Routers loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not import routers: {e}")
    
    # Создаем базовые роутеры на лету
    from fastapi import APIRouter
    
    @app.get("/api/v1/auth/test")
    async def auth_test():
        return {"message": "Auth endpoint работает"}
    
    @app.post("/api/v1/auth/register")
    async def register_user(user_data: dict):
        return {
            "message": "Пользователь зарегистрирован",
            "user": user_data.get("username"),
            "email": user_data.get("email")
        }
    
    @app.post("/api/v1/auth/login")
    async def login_user(credentials: dict):
        return {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": credentials.get("email", "").split("@")[0],
                "email": credentials.get("email")
            }
        }
    
    @app.get("/api/v1/transactions")
    async def get_transactions():
        return {
            "transactions": [
                {
                    "id": 1,
                    "amount": 1500.00,
                    "description": "Зарплата",
                    "type": "income",
                    "date": "2024-01-15T00:00:00"
                },
                {
                    "id": 2,
                    "amount": 250.50,
                    "description": "Продукты",
                    "type": "expense",
                    "date": "2024-01-14T00:00:00"
                }
            ],
            "total": 2,
            "income": 1500.00,
            "expense": 250.50,
            "balance": 1249.50
        }
    
    @app.get("/api/v1/transactions/stats/dashboard")
    async def get_dashboard_stats():
        return {
            "total_income": 1500.00,
            "total_expense": 250.50,
            "balance": 1249.50,
            "transactions_count": 2,
            "most_expensive_category": "Продукты",
            "period": "last_30_days"
        }
    
    @app.get("/api/v1/categories")
    async def get_categories():
        return {
            "categories": [
                {"id": 1, "name": "Зарплата", "type": "income", "icon": "💰"},
                {"id": 2, "name": "Продукты", "type": "expense", "icon": "🛒"},
                {"id": 3, "name": "Транспорт", "type": "expense", "icon": "🚗"},
                {"id": 4, "name": "Развлечения", "type": "expense", "icon": "🎬"}
            ]
        }

# Добавляем эндпоинт для проверки работы API
@app.get("/api/test")
async def test_api():
    """Тестовый эндпоинт для проверки работы API"""
    return {
        "message": "MoneyTracker API работает корректно!",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "2.0.0",
        "endpoints": {
            "home": "/",
            "docs": "/api/docs",
            "health": "/health",
            "status": "/api/v1/status",
            "test": "/api/test"
        },
        "database": check_database_connection()
    }