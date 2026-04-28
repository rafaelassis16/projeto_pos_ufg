from fastapi import APIRouter

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.get("/")
def get_tasks():
    return [{"id": 1, "title": "First task"}]
