# app/models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., 'worker', 'analyst', 'admin'
    project_id = Column(Integer, nullable=True)  # Optional: link to a project

    # Relationship
    daily_entries = relationship("DailyEntry", back_populates="owner")

class DailyEntry(Base):
    __tablename__ = "daily_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=datetime.utcnow)
    hours_worked = Column(Float, nullable=False)
    work_details = Column(String, nullable=False)
    check_in_photo = Column(String, nullable=True)  # store file path or URL
    check_out_photo = Column(String, nullable=True)  # store file path or URL

    # Relationship
    owner = relationship("User", back_populates="daily_entries")
