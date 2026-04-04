"""
CareerLaunch AI Backend - Simplified Version for Local Development
Database-free testing and development
"""
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic configuration (no database)
class Settings:
    ENVIRONMENT = "development"
    DEBUG = True
    LOG_LEVEL = "INFO"
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class JobAnalysisRequest(BaseModel):
    job_description: str

class JobAnalysisResponse(BaseModel):
    id: int
    required_skills: list
    technologies: list
    soft_skills: list
    experience_required: str
    readiness_score: float = 0.0

# Initialize FastAPI app
app = FastAPI(
    title="CareerLaunch AI Backend",
    description="AI-powered platform for job interview preparation",
    version="1.0.0 (Local Dev)",
)

settings = Settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
demo_users = {}
demo_analyses = {}
demo_counter = 0

# ==================== API Routes ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CareerLaunch AI Backend",
        "version": "1.0.0 (Local Development)",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CareerLaunch AI Backend"}

# ==================== User Endpoints ====================

@app.post("/api/v1/users/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    if user_data.email in demo_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    demo_users[user_data.email] = {
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "password": user_data.password,  # Don't do this in production!
    }
    
    logger.info(f"User registered: {user_data.email}")
    return {
        "id": 1,
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "message": "User registered successfully"
    }

@app.post("/api/v1/users/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    if credentials.email not in demo_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = demo_users[credentials.email]
    if user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    logger.info(f"User logged in: {credentials.email}")
    return {
        "access_token": "demo-token-" + credentials.email,
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me", response_model=dict)
async def get_current_user(token: str = None):
    """Get current user profile"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Demo: extract email from token
    if token.startswith("demo-token-"):
        email = token.replace("demo-token-", "")
        if email in demo_users:
            user = demo_users[email]
            return {
                "id": 1,
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"],
                "is_active": True,
            }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )

# ==================== Job Parser Endpoints ====================

@app.post("/api/v1/jobs/analyze", response_model=JobAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_job(job_data: JobAnalysisRequest):
    """Analyze a job description"""
    global demo_counter
    demo_counter += 1
    
    # Demo analysis
    analysis = {
        "id": demo_counter,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs"],
        "technologies": ["Python 3.9+", "FastAPI", "PostgreSQL", "Redis"],
        "soft_skills": ["Communication", "Problem-solving", "Teamwork"],
        "experience_required": "5+ years backend development",
        "readiness_score": 65.0  # Demo score
    }
    
    demo_analyses[demo_counter] = analysis
    logger.info(f"Job analyzed: {demo_counter}")
    return analysis

@app.get("/api/v1/jobs/{analysis_id}", response_model=JobAnalysisResponse)
async def get_job_analysis(analysis_id: int):
    """Get a specific job analysis"""
    if analysis_id not in demo_analyses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    return demo_analyses[analysis_id]

@app.get("/api/v1/jobs/{analysis_id}/readiness-score")
async def get_readiness_score(analysis_id: int):
    """Get readiness score"""
    if analysis_id not in demo_analyses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    return {"readiness_score": demo_analyses[analysis_id]["readiness_score"]}

@app.get("/api/v1/jobs/{analysis_id}/skill-gaps")
async def get_skill_gaps(analysis_id: int):
    """Get skill gaps"""
    if analysis_id not in demo_analyses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    return {
        "skill_gaps": [
            {"skill": "Docker", "current_level": "none", "required_level": "intermediate", "importance": "high"},
            {"skill": "Kubernetes", "current_level": "none", "required_level": "intermediate", "importance": "medium"},
        ]
    }

# ==================== Learning Paths Endpoints ====================

@app.post("/api/v1/learning-paths", status_code=status.HTTP_201_CREATED)
async def create_learning_path(data: dict):
    """Create a learning path"""
    return {
        "id": 1,
        "title": "Backend Development Path",
        "skill_gaps": ["Docker", "Kubernetes", "System Design"],
        "estimated_hours": 50,
        "progress_percentage": 0,
        "is_completed": False,
        "learning_modules": [
            {
                "id": 1,
                "title": "Docker Basics",
                "resource_type": "video",
                "estimated_hours": 2,
                "is_completed": False
            }
        ]
    }

# ==================== Assessment Endpoints ====================

@app.post("/api/v1/assessments", status_code=status.HTTP_201_CREATED)
async def create_assessment(data: dict):
    """Create an assessment"""
    return {
        "id": 1,
        "title": "Backend MCQ Assessment",
        "assessment_type": data.get("assessment_type", "mcq"),
        "questions": [
            {
                "id": 1,
                "question": "What is a REST API?",
                "options": ["a) Remote servers", "b) Architecture style", "c) Database", "d) Web server"],
                "correct_answer": 1
            }
        ],
        "score": None,
        "feedback": None
    }

@app.post("/api/v1/assessments/{assessment_id}/submit")
async def submit_assessment(assessment_id: int, submission: dict):
    """Submit assessment answers"""
    return {
        "id": assessment_id,
        "score": 85.0,
        "feedback": "Great job! You got 85% correct.",
        "time_taken_seconds": 300
    }

@app.get("/api/v1/assessments/{assessment_id}/score")
async def get_assessment_score(assessment_id: int):
    """Get assessment score"""
    return {
        "assessment_id": assessment_id,
        "score": 85.0,
        "feedback": "Great job!"
    }

# ==================== Interview Endpoints ====================

@app.post("/api/v1/interviews", status_code=status.HTTP_201_CREATED)
async def start_interview(data: dict):
    """Start an interview"""
    return {
        "id": 1,
        "title": data.get("title", "Mock Interview"),
        "status": "in_progress",
        "conversation_history": [
            {
                "role": "assistant",
                "content": "Hi! Tell me about your background and experience."
            }
        ],
        "started_at": "2024-01-01T12:00:00",
        "completed_at": None
    }

@app.post("/api/v1/interviews/{interview_id}/respond")
async def respond_interview(interview_id: int, data: dict):
    """Respond to interview question"""
    return {
        "interview_id": interview_id,
        "user_message": data.get("message", ""),
        "ai_response": "That's great! Tell me more about working with databases."
    }

@app.post("/api/v1/interviews/{interview_id}/end")
async def end_interview(interview_id: int):
    """End interview and get feedback"""
    return {
        "id": interview_id,
        "overall_score": 78.0,
        "strengths": ["Good communication", "Technical knowledge"],
        "improvement_areas": ["System design", "Problem-solving approach"],
        "detailed_feedback": "Good performance overall!",
        "duration_seconds": 1200,
        "completed_at": "2024-01-01T12:20:00"
    }

@app.get("/api/v1/interviews/{interview_id}/feedback")
async def get_interview_feedback(interview_id: int):
    """Get interview feedback"""
    return {
        "interview_id": interview_id,
        "overall_score": 78.0,
        "strengths": ["Communication", "Technical Skills"],
        "improvement_areas": ["System Design"],
        "detailed_feedback": "Good performance!"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("CareerLaunch AI Backend - Starting...")
    print("="*60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"\n📚 API Documentation: http://localhost:8000/docs")
    print(f"🏥 Health Check: http://localhost:8000/api/v1/health")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
