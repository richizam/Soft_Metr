# app/routes/data_routes.py
# app/routes/data_routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.data_entry_service import create_daily_entry
from app.models import DailyEntry
from pydantic import BaseModel
from datetime import datetime, date

router = APIRouter()

class DailyEntryResponse(BaseModel):
    id: int
    user_id: int
    task_id: int = None
    hours_worked: float
    start_time: datetime = None
    finish_time: datetime = None
    check_in_photo: str = None
    check_out_photo: str = None

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/daily-entry", response_model=DailyEntryResponse)
async def add_daily_entry(
    user_id: int = Form(...),
    task_id: int = Form(...),
    hours_worked: float = Form(...),
    start_time: str = Form(...),
    finish_time: str = Form(...),
    check_in_photo: UploadFile = File(None),
    check_out_photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        start_time_dt = datetime.fromisoformat(start_time)
        finish_time_dt = datetime.fromisoformat(finish_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    
    check_in_photo_path = None
    check_out_photo_path = None

    if check_in_photo:
        check_in_photo_path = f"photos/{check_in_photo.filename}"
        with open(check_in_photo_path, "wb") as f:
            content = await check_in_photo.read()
            f.write(content)
    if check_out_photo:
        check_out_photo_path = f"photos/{check_out_photo.filename}"
        with open(check_out_photo_path, "wb") as f:
            content = await check_out_photo.read()
            f.write(content)

    try:
        entry = create_daily_entry(
            db=db,
            user_id=user_id,
            task_id=task_id,
            hours_worked=hours_worked,
            start_time=start_time_dt,
            finish_time=finish_time_dt,
            check_in_photo=check_in_photo_path,
            check_out_photo=check_out_photo_path
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return entry

@router.get("/daily-entry/today")
def get_daily_entry_today(user_id: int, db: Session = Depends(get_db)):
    today = date.today()
    entry = db.query(DailyEntry).filter(DailyEntry.user_id == user_id, DailyEntry.date == today).first()
    if entry:
        return {"exists": True}
    return {"exists": False}

@router.get("/projects/{project_id}/tasks")
def get_tasks(project_id: int, db: Session = Depends(get_db)):
    from app.models import Task
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks
