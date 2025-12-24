from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="MoneyTracker API", version="1.0.0", lifespan=lifespan)

from app.routers import auth, transactions, categories
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(categories.router)

@app.get("/")
def read_root():
    return {"message": "API works without routers!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}