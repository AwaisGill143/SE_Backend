"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    bio: Optional[str]
    profile_picture_url: Optional[str]

# Authentication Schemas
class TokenRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

# Job Parser Schemas
class JobPostingBase(BaseModel):
    title: str
    description: str
    company: str
    location: str
    experience_level: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_url: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: int
    posted_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobAnalysisRequest(BaseModel):
    job_description: str
    job_url: Optional[str] = None

class SkillGap(BaseModel):
    skill: str
    current_level: str
    required_level: str
    importance: str  # high, medium, low

class JobAnalysisResponse(BaseModel):
    id: int
    required_skills: List[str]
    technologies: List[str]
    soft_skills: List[str]
    experience_required: str
    readiness_score: Optional[float]
    skill_gaps: List[SkillGap]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Learning Path Schemas
class LearningResourceBase(BaseModel):
    title: str
    description: str
    resource_type: str  # video, article, course, project
    resource_url: str
    estimated_hours: float

class LearningModuleResponse(LearningResourceBase):
    id: int
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LearningPathResponse(BaseModel):
    id: int
    title: str
    description: str
    skill_gaps: List[str]
    estimated_hours: float
    progress_percentage: float
    is_completed: bool
    learning_modules: List[LearningModuleResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LearningPathCreateRequest(BaseModel):
    job_analysis_id: int

# Assessment Schemas
class MCQQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class CodingChallenge(BaseModel):
    title: str
    problem_statement: str
    difficulty: str  # easy, medium, hard
    test_cases: List[Dict[str, Any]]
    boilerplate_code: Optional[str]
    time_limit_seconds: int

class AssessmentRequest(BaseModel):
    job_analysis_id: Optional[int] = None
    assessment_type: str  # mcq, coding, system_design, behavioral
    difficulty: Optional[str] = None

class AssessmentAnswerSubmit(BaseModel):
    assessment_id: int
    user_answers: List[Any]
    code: Optional[str] = None  # For coding challenges

class AssessmentResponse(BaseModel):
    id: int
    title: str
    assessment_type: str
    score: Optional[float]
    feedback: Optional[str]
    time_taken_seconds: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Interview Schemas
class InterviewStartRequest(BaseModel):
    job_analysis_id: Optional[int] = None
    title: str
    duration_minutes: int = 30

class InterviewMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class InterviewResponse(BaseModel):
    response_text: str
    follow_up_question: Optional[str]

class InterviewSubmitResponse(BaseModel):
    interview_id: int
    user_message: str
    ai_response: str

class InterviewFeedback(BaseModel):
    id: int
    overall_score: float
    strengths: List[str]
    improvement_areas: List[str]
    detailed_feedback: str
    duration_seconds: int
    completed_at: datetime
    
    class Config:
        from_attributes = True

class InterviewDetailResponse(BaseModel):
    id: int
    title: str
    status: str
    conversation_history: List[InterviewMessage]
    feedback_report: Optional[Dict[str, Any]]
    overall_score: Optional[float]
    strengths: Optional[List[str]]
    improvement_areas: Optional[List[str]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Skill Schemas
class UserSkillCreate(BaseModel):
    skill_name: str
    proficiency_level: str  # novice, intermediate, advanced, expert
    years_of_experience: float

class UserSkillResponse(UserSkillCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Company Intelligence
class CompanyIntelligenceResponse(BaseModel):
    company_name: str
    common_question_patterns: List[str]
    frequently_asked_topics: List[str]
    average_interview_duration: float
    candidates_count: int
    
    class Config:
        from_attributes = True

# Resume Schemas
class ResumeUploadRequest(BaseModel):
    """Request for resume upload"""
    file_name: str
    is_primary: bool = True

class ResumeResponse(BaseModel):
    """Resume response"""
    id: int
    file_name: str
    extracted_skills: Optional[List[str]] = []
    extracted_experience: Optional[Any] = None
    extracted_education: Optional[Any] = None
    summary: Optional[str] = None
    is_primary: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SkillGapAnalysisResponse(BaseModel):
    """Skill gap analysis response"""
    id: int
    resume_skills: List[str]
    required_skills: List[str]
    matching_skills: List[str]
    gap_skills: List[str]
    gap_percentage: float
    priority_skills: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Performance Schemas
class PerformanceResponse(BaseModel):
    """Performance tracking response"""
    id: int
    activity_type: str
    score: Optional[float]
    time_taken_seconds: Optional[int]
    feedback: Optional[str]
    skill_tags: List[str]
    completed_at: datetime
    
    class Config:
        from_attributes = True

# Learning Recommendations
class LearningRecommendationResponse(BaseModel):
    """Learning recommendations response"""
    skill_gaps: List[str]
    current_skills: List[str]
    recommendations: str
    generated_at: str

class ConceptExplanationResponse(BaseModel):
    """Concept explanation response"""
    skill: str
    level: str
    explanation: str
    generated_at: str

# Error Response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()