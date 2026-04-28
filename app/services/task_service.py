from sqlalchemy.orm import Session
from app.models.task_model import Task
from app.schemas.task_schema import TaskCreate
from app.services.priority_advisor import PriorityAdvisor

class TaskService:
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate):
        if not task_data.priority or task_data.priority == "Baixa":
            task_data.priority = PriorityAdvisor.advise(task_data.title, task_data.description)
        
        db_task = Task(**task_data.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_task(db: Session, task_id: int):
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks(db: Session):
        return db.query(Task).all()

    @staticmethod
    def delete_task(db: Session, task_id: int):
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if db_task:
            db.delete(db_task)
            db.commit()
            return True
        return False
