"""
CareNav Florida - Main Application
Built with Rick Weyenberg and Greg Katz collaborating
Copyright (c) 2026 - MIT License
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import init_db
from app.routers import (
    patients_router,
    chat_router,
    eligibility_router,
    facilities_router,
    tasks_router,
    documents_router,
    bills_router,
    income_phases_router,
    benefit_applications_router,
    contacts_router,
    assets_router,
    medical_router,
    insurance_router,
    selected_facility_router,
    wins_router,
)
from app.routers.knowledge_base import router as knowledge_base_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="CareNav Florida",
    description="Multi-agent AI system for Florida elder care navigation",
    version="1.0.0",
    lifespan=lifespan,
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(patients_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(eligibility_router, prefix="/api")
app.include_router(facilities_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(documents_router)
app.include_router(bills_router, prefix="/api")
app.include_router(income_phases_router, prefix="/api")
app.include_router(benefit_applications_router, prefix="/api")
app.include_router(contacts_router, prefix="/api")
app.include_router(assets_router, prefix="/api")
app.include_router(medical_router)
app.include_router(insurance_router)
app.include_router(selected_facility_router)
app.include_router(wins_router)
app.include_router(knowledge_base_router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "name": "CareNav Florida",
        "version": "1.0.0",
        "description": "Multi-agent AI system for Florida elder care navigation",
        "endpoints": {
            "health": "/healthz",
            "docs": "/docs",
            "patients": "/api/patients",
            "chat": "/api/chat",
            "eligibility": "/api/eligibility",
            "facilities": "/api/facilities",
            "tasks": "/api/tasks",
        }
    }
