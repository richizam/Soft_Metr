# app/routes/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import User, DailyEntry
router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/workers")
def get_workers(project_id: int, db: Session = Depends(get_db)):
    workers = db.query(User).filter(User.project_id == project_id, User.role == "worker").all()
    return [{"id": w.id, "email": w.email} for w in workers]
@router.get("/worker/{worker_id}")
def get_worker_details(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(User).filter(User.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    entries = db.query(DailyEntry).filter(DailyEntry.user_id == worker_id).all()
    entries_data = []
    for entry in entries:
        entries_data.append({
            "id": entry.id,
            "date": entry.date.isoformat() if entry.date else "",
            "hours_worked": entry.hours_worked,
            "start_time": entry.start_time.isoformat() if entry.start_time else "",
            "finish_time": entry.finish_time.isoformat() if entry.finish_time else "",
            "check_in_photo": entry.check_in_photo,
            "check_out_photo": entry.check_out_photo,
        })
    return {"worker": {"id": worker.id, "email": worker.email}, "entries": entries_data}
@router.get("/analytics")
def get_analytics(project_id: int, db: Session = Depends(get_db)):
    avg_hours = db.query(func.avg(DailyEntry.hours_worked)).join(User, DailyEntry.user_id == User.id).filter(User.project_id == project_id, User.role == "worker").scalar()
    max_hours = db.query(func.max(DailyEntry.hours_worked)).join(User, DailyEntry.user_id == User.id).filter(User.project_id == project_id, User.role == "worker").scalar()
    top_workers = (db.query(User.email, func.sum(DailyEntry.hours_worked).label("total_hours")).join(DailyEntry, DailyEntry.user_id == User.id).filter(User.project_id == project_id, User.role == "worker").group_by(User.id).order_by(func.sum(DailyEntry.hours_worked).desc()).limit(10).all())
    return {"average_hours": avg_hours if avg_hours else 0, "max_hours": max_hours if max_hours else 0, "top_workers": [{"email": tw[0], "total_hours": tw[1]} for tw in top_workers]}
