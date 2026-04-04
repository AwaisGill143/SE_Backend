"""
CareerLaunch AI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base, get_db
from app.routers import users, jobs, learning_paths, assessments, interviews, health
from app.middleware.error_handler import error_handling_middleware

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Application startup")
    # Startup logic here
    yield
    logger.info("Application shutdown")
    # Shutdown logic here

# Initialize FastAPI app
app = FastAPI(
    title="CareerLaunch AI Backend",
    description="AI-powered platform for job interview preparation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
app.middleware("http")(error_handling_middleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Job Parser"])
app.include_router(learning_paths.router, prefix="/api/v1/learning-paths", tags=["Learning Paths"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(interviews.router, prefix="/api/v1/interviews", tags=["Interviews"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CareerLaunch AI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
