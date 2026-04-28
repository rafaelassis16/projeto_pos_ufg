from fastapi import FastAPI
from app.database.db import Base, engine
from app.routes import task_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(task_routes.router)

@app.get("/")
def read_root():
    return {"status": "ok"}