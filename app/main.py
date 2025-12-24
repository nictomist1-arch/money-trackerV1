from fastapi import FastAPI, Request, Depends
from app.routers import transactions
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os
import datetime

from app.database import engine, get_db, check_database_connection
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("🚀 Starting MoneyTracker API...")
    print(f"📅 Started at: {datetime.datetime.now()}")
    
    try:
        # Пытаемся создать таблицы
        print("🔄 Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create tables: {str(e)[:100]}")
    
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
    
    # Определяем стиль в зависимости от статуса
    db_status_class = ""
    db_icon = ""
    
    if "✅" in db_status:
        db_status_class = "db-success"
        db_icon = "✅"
    elif "⚠️" in db_status:
        db_status_class = "db-warning"
        db_icon = "⚠️"
    else:
        db_status_class = "db-error"
        db_icon = "❌"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MoneyTracker API</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .card {{
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .logo {{
                font-size: 48px;
                margin-bottom: 20px;
                color: #667eea;
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
            
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            
            .status-card {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                border: 2px solid #e9ecef;
            }}
            
            .status-label {{
                font-size: 0.9rem;
                color: #6c757d;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .status-value {{
                font-size: 1.8rem;
                font-weight: bold;
                color: #2d3748;
            }}
            
            .db-status {{
                padding: 20px;
                margin: 30px 0;
                border-radius: 10px;
                font-size: 16px;
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .db-success {{
                background: #d4edda;
                border: 2px solid #28a745;
                color: #155724;
            }}
            
            .db-warning {{
                background: #fff3cd;
                border: 2px solid #ffc107;
                color: #856404;
            }}
            
            .db-error {{
                background: #f8d7da;
                border: 2px solid #dc3545;
                color: #721c24;
            }}
            
            .buttons {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                justify-content: center;
                margin: 40px 0;
            }}
            
            .btn {{
                display: inline-flex;
                align-items: center;
                gap: 10px;
                padding: 15px 30px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }}
            
            .btn-primary {{
                background: #007bff;
                color: white;
                border-color: #007bff;
            }}
            
            .btn-primary:hover {{
                background: #0056b3;
                border-color: #0056b3;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 123, 255, 0.3);
            }}
            
            .btn-secondary {{
                background: #6c757d;
                color: white;
                border-color: #6c757d;
            }}
            
            .btn-secondary:hover {{
                background: #545b62;
                border-color: #545b62;
                transform: translateY(-2px);
            }}
            
            .btn-success {{
                background: #28a745;
                color: white;
                border-color: #28a745;
            }}
            
            .code-section {{
                margin: 40px 0;
                padding: 30px;
                background: #f8f9fa;
                border-radius: 15px;
            }}
            
            .code-block {{
                background: #2d3748;
                color: #e2e8f0;
                padding: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                overflow-x: auto;
                margin: 20px 0;
                line-height: 1.5;
            }}
            
            .endpoints {{
                margin-top: 40px;
            }}
            
            .endpoint {{
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }}
            
            .method {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 15px;
                min-width: 70px;
                text-align: center;
            }}
            
            .get {{ background: #28a745; color: white; }}
            .post {{ background: #007bff; color: white; }}
            .put {{ background: #fd7e14; color: white; }}
            .delete {{ background: #dc3545; color: white; }}
            
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #e9ecef;
                color: #6c757d;
                font-size: 0.9rem;
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
                
                .status-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <!-- Заголовок -->
                <div class="header">
                    <div class="logo">
                        <i class="fas fa-money-bill-wave"></i>
                    </div>
                    <h1>MoneyTracker API</h1>
                    <p class="subtitle">API для отслеживания личных финансов</p>
                </div>
                
                <!-- Сетка статуса -->
                <div class="status-grid">
                    <div class="status-card">
                        <div class="status-label">Статус</div>
                        <div class="status-value" style="color: #28a745;">Работает ✅</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Версия</div>
                        <div class="status-value">2.0.0</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Режим</div>
                        <div class="status-value">{'Разработка' if os.getenv('DEBUG') == 'true' else 'Продакшн'}</div>
                    </div>
                    <div class="status-card">
                        <div class="status-label">Платформа</div>
                        <div class="status-value">Render.com</div>
                    </div>
                </div>
                
                <!-- Статус БД -->
                <div class="db-status {db_status_class}">
                    <div style="font-size: 24px;">{db_icon}</div>
                    <div>
                        <strong>База данных:</strong> {db_status}
                    </div>
                </div>
                
                <!-- Кнопки действий -->
                <div class="buttons">
                    <a href="/api/docs" class="btn btn-primary" target="_blank">
                        <i class="fas fa-book"></i> API Документация
                    </a>
                    <a href="/health" class="btn btn-secondary">
                        <i class="fas fa-heartbeat"></i> Проверка здоровья
                    </a>
                    <a href="/api/v1/db/check" class="btn btn-success">
                        <i class="fas fa-database"></i> Проверить БД
                    </a>
                </div>
                
                <!-- Примеры API -->
                <div class="code-section">
                    <h3><i class="fas fa-code"></i> Примеры использования API</h3>
                    
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
                </div>
                
                <!-- Доступные эндпоинты -->
                <div class="endpoints">
                    <h3><i class="fas fa-list"></i> Доступные эндпоинты</h3>
                    
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
                    
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/v1/db/check</code>
                        <span>— Проверить подключение к БД</span>
                    </div>
                </div>
                
                <!-- Футер -->
                <div class="footer">
                    <p>© 2024 MoneyTracker API • Развернуто на Render.com</p>
                    <p>FastAPI • PostgreSQL • SQLAlchemy • Pydantic</p>
                    <p style="margin-top: 10px; font-size: 0.8rem; color: #adb5bd;">
                        <i class="fas fa-info-circle"></i> Время запуска: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            // Обновляем время
            function updateTime() {{
                const timeElement = document.querySelector('.footer p:last-child');
                if (timeElement) {{
                    const now = new Date();
                    timeElement.innerHTML = `<i class="fas fa-info-circle"></i> Обновлено: ${{now.toLocaleString('ru-RU')}}`;
                }}
            }}
            
            // Обновляем время каждую минуту
            setInterval(updateTime, 60000);
            
            // Копирование кода при клике
            document.querySelectorAll('.code-block').forEach(block => {{
                block.addEventListener('click', function() {{
                    const text = this.textContent;
                    navigator.clipboard.writeText(text).then(() => {{
                        const originalText = this.textContent;
                        this.textContent = '✅ Код скопирован в буфер обмена!';
                        setTimeout(() => {{
                            this.textContent = originalText;
                        }}, 2000);
                    }});
                }});
            }});
            
            // Проверка статуса API
            async function checkApiStatus() {{
                try {{
                    const response = await fetch('/health');
                    if (response.ok) {{
                        console.log('✅ API работает нормально');
                    }}
                }} catch (error) {{
                    console.log('⚠️ Не удалось проверить статус API');
                }}
            }}
            
            // Проверяем при загрузке
            window.addEventListener('load', checkApiStatus);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    db_status = check_database_connection()
    is_healthy = "✅" in db_status
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "money-tracker-api",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "components": {
            "database": {
                "status": "connected" if is_healthy else "disconnected",
                "message": db_status
            },
            "api": {
                "status": "operational",
                "uptime": "100%"
            }
        },
        "links": {
            "documentation": "/api/docs",
            "database_check": "/api/v1/db/check",
            "status_page": "/api/v1/status"
        }
    }

# Импортируем и подключаем роутеры
try:
    from app.routers import auth, transactions, categories, db_check
    
    app.include_router(auth.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)
    app.include_router(db_check.router)
    
    print("✅ All routers loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Could not import some routers: {e}")
    
    # Создаем базовые роутеры
    from fastapi import APIRouter
    
    @app.get("/api/v1/db/check")
    async def check_db():
        db_status = check_database_connection()
        return {
            "database": "PostgreSQL" if "postgresql" in os.getenv("DATABASE_URL", "") else "SQLite",
            "status": "connected" if "✅" in db_status else "disconnected",
            "message": db_status
        }

@app.get("/api/v1/status")
async def get_status():
    """Статус системы"""
    return {
        "service": "MoneyTracker API",
        "version": "2.0.0",
        "status": "operational",
        "environment": "production" if os.getenv("DEBUG") != "true" else "development",
        "database": check_database_connection(),
        "endpoints_available": True,
        "documentation": "/api/docs"
    }
app.include_router(transactions.router)

# Тестовый эндпоинт
@app.get("/api/test")
async def test_api():
    return {
        "message": "API работает корректно!",
        "database": check_database_connection(),
        "timestamp": datetime.datetime.now().isoformat()
    }