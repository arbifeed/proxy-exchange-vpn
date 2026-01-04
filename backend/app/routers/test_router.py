from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/hello")
def hello():
    return {"message": "Привет! Это работает!"}
