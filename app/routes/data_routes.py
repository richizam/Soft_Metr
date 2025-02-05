# app/routes/data_routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.data_entry_service import create_daily_entry

router = APIRouter()

# Pydantic model for a simple response (optional)
from pydantic import BaseModel
class DailyEntryResponse(BaseModel):
    id: int
    user_id: int
    hours_worked: float
    work_details: str
    check_in_photo: str = None
    check_out_photo: str = None

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/daily-entry", response_model=DailyEntryResponse)
async def add_daily_entry(
    user_id: int = Form(...),
    hours_worked: float = Form(...),
    work_details: str = Form(...),
    check_in_photo: UploadFile = File(None),
    check_out_photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Here we simply save the file to disk. In production, consider storing on S3 or similar.
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

    entry = create_daily_entry(
        db=db,
        user_id=user_id,
        hours_worked=hours_worked,
        work_details=work_details,
        check_in_photo=check_in_photo_path,
        check_out_photo=check_out_photo_path
    )
    return DailyEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        hours_worked=entry.hours_worked,
        work_details=entry.work_details,
        check_in_photo=entry.check_in_photo,
        check_out_photo=entry.check_out_photo
    )
