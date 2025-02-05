# app/routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import SessionLocal
from app.models import User
from app.services.auth_service import authenticate_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user_id: int
    email: EmailStr
    role: str
    project_id: int = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=LoginResponse)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_req.email, login_req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return LoginResponse(user_id=user.id, email=user.email, role=user.role, project_id=user.project_id)

class CheckEmailRequest(BaseModel):
    email: str  # Accept any string

@router.post("/check_email")
def check_email(check_req: CheckEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == check_req.email).first()
    return {"exists": user is not None}
