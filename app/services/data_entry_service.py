# app/services/data_entry_service.py
from sqlalchemy.orm import Session
from app.models import DailyEntry

def create_daily_entry(db: Session, user_id: int, hours_worked: float, work_details: str,
                       check_in_photo: str = None, check_out_photo: str = None):
    entry = DailyEntry(
        user_id=user_id,
        hours_worked=hours_worked,
        work_details=work_details,
        check_in_photo=check_in_photo,
        check_out_photo=check_out_photo
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
