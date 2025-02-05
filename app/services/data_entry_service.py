# app/services/data_entry_service.py

from sqlalchemy.orm import Session
from app.models import DailyEntry
from datetime import date

def create_daily_entry(db: Session, user_id: int, task_id: int, hours_worked: float,
                       start_time, finish_time,
                       check_in_photo: str = None, check_out_photo: str = None):
    # Check if an entry already exists today for this user
    existing = db.query(DailyEntry).filter(DailyEntry.user_id == user_id, DailyEntry.date == date.today()).first()
    if existing:
        raise Exception("Daily entry already exists for today.")
    entry = DailyEntry(
        user_id=user_id,
        task_id=task_id,
        hours_worked=hours_worked,
        start_time=start_time,
        finish_time=finish_time,
        check_in_photo=check_in_photo,
        check_out_photo=check_out_photo
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
