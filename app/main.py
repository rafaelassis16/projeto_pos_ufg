from fastapi import FastAPI
from app.database.db import Base, engine
from app.models.task_model import Task
from app.routes import task_routes

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(task_routes.router)

@app.get("/")
def read_root():
    return {"status": "ok"}