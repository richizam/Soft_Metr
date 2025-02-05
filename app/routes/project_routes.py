#app/routes/data_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Task

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/projects/{project_id}/tasks")
def get_tasks(project_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks
