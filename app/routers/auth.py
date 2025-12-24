from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/test")
def test_auth():
    return {"message": "Auth router works!"}
