# app/main.py
from fastapi import FastAPI
from app.routes import auth_routes, data_routes, project_routes
from app.database import engine, Base

# For development only: drop and recreate tables so that the new schema (including task_id) is applied.
# WARNING: This deletes all data!
#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Project API")

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(data_routes.router, prefix="/data", tags=["Daily Entry"])
app.include_router(project_routes.router, tags=["Projects"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Construction Project API"}

