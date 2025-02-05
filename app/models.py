# app/models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# --- Project Model ---
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    tasks = relationship("Task", back_populates="project")
    users = relationship("User", back_populates="project_rel")

# --- Task Model ---
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    project = relationship("Project", back_populates="tasks")

# --- User Model ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., 'worker', 'analyst', 'admin'
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project_rel = relationship("Project", back_populates="users")
    daily_entries = relationship("DailyEntry", back_populates="owner")

# --- DailyEntry Model ---
# The hours_worked will be computed automatically (as the difference between finish and check‑in times)
class DailyEntry(Base):
    __tablename__ = "daily_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    hours_worked = Column(Float, nullable=False)  # computed automatically
    start_time = Column(DateTime, nullable=True)
    finish_time = Column(DateTime, nullable=True)
    check_in_photo = Column(String, nullable=True)
    check_out_photo = Column(String, nullable=True)
    date = Column(Date, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="daily_entries")
    task = relationship("Task")
