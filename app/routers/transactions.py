from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("/")
async def get_transactions():
    """Получить транзакции (заглушка)"""
    return {"message": "Transactions endpoint работает"}

@router.get("/test")
async def test_transactions():
    """Тестовый эндпоинт"""
    return {"message": "Transactions router работает!"}