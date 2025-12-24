from fastapi import APIRouter 
 
router = APIRouter(prefix="/transactions", tags=["transactions"]) 
 
@router.get("/test") 
def test_transactions(): 
    return {"message": "Transactions router works!"} 
