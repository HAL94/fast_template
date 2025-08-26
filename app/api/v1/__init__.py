from fastapi import APIRouter
from .todos.router import router as todos_router
from .auth.router import router as auth_router

v1_router = APIRouter(prefix="/v1")

@v1_router.get("/welcome")
def welcome():
    return {"Welcome": "to your seed project"}


v1_router.include_router(todos_router)
v1_router.include_router(auth_router)
