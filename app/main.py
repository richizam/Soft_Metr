# app/main.py
from fastapi import FastAPI
from app.routes import auth_routes, data_routes
from app.database import engine, Base

# Create all tables (for development, use Alembic for migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Project API")

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(data_routes.router, prefix="/data", tags=["Daily Entry"])

# Optionally, add a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Construction Project API"}
