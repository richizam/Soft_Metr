import os
import random
from datetime import datetime, timedelta, date
from app.database import SessionLocal, engine, Base
from app.models import User, Project, Task, DailyEntry
from app.services.auth_service import get_password_hash

def seed():
    session = SessionLocal()
    # Clear existing data (for testing only!)
    session.query(DailyEntry).delete()
    session.query(User).delete()
    session.query(Task).delete()
    session.query(Project).delete()
    session.commit()

    # --- Create a Project ---
    project = Project(name="Project Alpha")
    session.add(project)
    session.commit()  # commit to generate project.id

    # --- Create Tasks ---
    task_names = [
        "Excavation", "Concrete Pouring", "Framing", 
        "Plumbing Installation", "Electrical Wiring"
    ]
    tasks = []
    for i, name in enumerate(task_names, start=1):
        task = Task(project_id=project.id, name=name, description=f"Task {i}: {name} details")
        session.add(task)
        tasks.append(task)
    session.commit()

    # --- Create 20 Worker Accounts ---
    num_workers = 20
    workers = []
    for i in range(1, num_workers + 1):
        email = f"worker{i}@example.com"
        hashed_password = get_password_hash("password")
        user = User(email=email, password_hash=hashed_password, role="worker", project_id=project.id)
        session.add(user)
        workers.append(user)

    # --- Create an Admin Account ---
    admin_email = "admin@example.com"
    admin_password = get_password_hash("adminpass")
    admin_user = User(email=admin_email, password_hash=admin_password, role="admin", project_id=project.id)
    session.add(admin_user)
    session.commit()

    # --- Generate Fake Daily Entries for Workers ---
    # For the past 30 days, each worker has a 70% chance of having submitted an entry
    today = date.today()
    for worker in workers:
        for n in range(30):
            entry_date = today - timedelta(days=n)
            if random.random() < 0.7:
                # Pick a random task
                task = random.choice(tasks)
                # Random start time between 7:00 and 9:00 AM on that day
                start_hour = random.randint(7, 9)
                start_minute = random.randint(0, 59)
                start_time = datetime.combine(entry_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
                # Random work duration between 4 and 12 hours
                duration_hours = random.uniform(4, 12)
                finish_time = start_time + timedelta(hours=duration_hours)
                hours_worked = round(duration_hours, 2)
                # Fake photo paths (for testing only)
                check_in_photo = f"photos/{worker.email}_entry_{entry_date}_in.jpg"
                check_out_photo = f"photos/{worker.email}_entry_{entry_date}_out.jpg"
                entry = DailyEntry(
                    user_id=worker.id,
                    task_id=task.id,
                    hours_worked=hours_worked,
                    start_time=start_time,
                    finish_time=finish_time,
                    check_in_photo=check_in_photo,
                    check_out_photo=check_out_photo,
                    date=entry_date
                )
                session.add(entry)
    session.commit()
    print("Seeding complete. Created:")
    print(f"  1 Project: {project.name} (id: {project.id})")
    print(f"  {len(tasks)} Tasks")
    print(f"  {num_workers} Worker accounts (worker1@example.com ... worker{num_workers}@example.com, password: 'password')")
    print("  1 Admin account (admin@example.com, password: 'adminpass')")
    print("  Multiple daily entries per worker for the past 30 days.")
    session.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed()
