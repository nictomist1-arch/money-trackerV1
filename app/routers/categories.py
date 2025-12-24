from fastapi import APIRouter 
 
router = APIRouter(prefix="/categories", tags=["categories"]) 
 
@router.get("/test") 
def test_categories(): 
    return {"message": "Categories router works!"} 
