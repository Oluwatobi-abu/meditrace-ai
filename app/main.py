from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, patients, records, prescriptions, vaccinations, labs, ai, emergency
import os

# Create all database tables on startup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database table creation note: {e}")

app = FastAPI(
    title="MediTrace AI",
    description="AI-powered emergency health record platform for Africa",
    version="1.0.0"
)

# CORS — allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Register all routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(records.router)
app.include_router(prescriptions.router)
app.include_router(vaccinations.router)
app.include_router(labs.router)
app.include_router(ai.router)
app.include_router(emergency.router)


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}