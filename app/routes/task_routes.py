from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db import get_db
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskCreate, TaskUpdate, Task as TaskSchema

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return TaskService.create_task(db, task)

@router.get("/", response_model=List[TaskSchema])
def get_tasks(
    completed: Optional[bool] = Query(None, description="Filtrar por status de conclusão"),
    db: Session = Depends(get_db)
):
    return TaskService.get_tasks(db, completed=completed)

@router.get("/{task_id}", response_model=TaskSchema)
def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = TaskService.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return db_task

@router.put("/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = TaskService.update_task(db, task_id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return db_task

@router.patch("/{task_id}/complete", response_model=TaskSchema)
def patch_task_complete(task_id: int, completed: bool = True, db: Session = Depends(get_db)):
    db_task = TaskService.patch_task_completion(db, task_id, completed)
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"msg": "Tarefa deletada"}

@router.get("/test/status")
def test_tasks_status():
    return {"msg": "rota de tarefas funcionando"}
