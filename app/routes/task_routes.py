from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskCreate, Task as TaskSchema

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return TaskService.create_task(db, task)

@router.get("/", response_model=List[TaskSchema])
def get_tasks(db: Session = Depends(get_db)):
    return TaskService.get_tasks(db)

@router.get("/{task_id}", response_model=TaskSchema)
def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = TaskService.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"msg": "Tarefa deletada"}

@router.get("/test")
def test_tasks():
    return {"msg": "rota de tarefas funcionando"}
