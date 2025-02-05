# seed.py
import os
from app.database import SessionLocal, engine, Base
from app.models import User, Project, Task
from app.services.auth_service import get_password_hash

def seed():
    session = SessionLocal()
    
    # Optional: Clear existing data (for testing only!)
    session.query(User).delete()
    session.query(Task).delete()
    session.query(Project).delete()
    session.commit()

    # --- Create a Project ---
    project = Project(name="Project Alpha")
    session.add(project)
    session.commit()  # Commit to get the project.id

    # --- Create some Tasks for the Project ---
    task_names = [
        "Excavation", "Concrete Pouring", "Framing", "Plumbing Installation", "Electrical Wiring"
    ]
    tasks = []
    for i, name in enumerate(task_names, start=1):
        task = Task(project_id=project.id, name=name, description=f"Task {i}: {name} details")
        tasks.append(task)
        session.add(task)
    session.commit()

    # --- Create 20 Worker Accounts ---
    for i in range(1, 21):
        email = f"worker{i}@example.com"
        hashed_password = get_password_hash("password")
        user = User(
            email=email,
            password_hash=hashed_password,
            role="worker",
            project_id=project.id
        )
        session.add(user)

    # --- Create an Admin Account ---
    admin_email = "admin@example.com"
    admin_password = get_password_hash("adminpass")
    admin_user = User(
        email=admin_email,
        password_hash=admin_password,
        role="admin",
        project_id=project.id
    )
    session.add(admin_user)
    session.commit()

    print("Seeding complete. Created:")
    print(f"  1 Project: {project.name} (id: {project.id})")
    print(f"  {len(tasks)} Tasks")
    print("  20 Worker accounts (worker1@example.com ... worker20@example.com, password: 'password')")
    print("  1 Admin account (admin@example.com, password: 'adminpass')")
    session.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed()
