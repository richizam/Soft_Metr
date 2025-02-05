# app/main.py
from fastapi import FastAPI
from app.routes import auth_routes, data_routes, project_routes, admin_routes
from app.database import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Construction Project API")
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(data_routes.router, prefix="/data", tags=["Daily Entry"])
app.include_router(project_routes.router, tags=["Projects"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Construction Project API"}
