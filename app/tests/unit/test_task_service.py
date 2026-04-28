import pytest
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskCreate

def test_service_create_task(db):
    task_data = TaskCreate(title="Service Task", description="Testing service")
    task = TaskService.create_task(db, task_data)
    assert task.id is not None
    assert task.title == "Service Task"
    assert task.priority == "Baixa" # Advisor says Baixa for this text

def test_service_get_task(db):
    task_data = TaskCreate(title="Get Task")
    task_created = TaskService.create_task(db, task_data)
    task_fetched = TaskService.get_task(db, task_created.id)
    assert task_fetched.id == task_created.id

def test_service_delete_task(db):
    task_data = TaskCreate(title="Delete Task")
    task = TaskService.create_task(db, task_data)
    success = TaskService.delete_task(db, task.id)
    assert success is True
    assert TaskService.get_task(db, task.id) is None
