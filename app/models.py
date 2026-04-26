"""
Database models for CareerLaunch AI
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"

class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class AssessmentType(str, enum.Enum):
    MCQ = "mcq"
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"

class InterviewStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Models
class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    profile_picture_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CANDIDATE)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_analyses = relationship("JobAnalysis", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")
    assessments = relationship("Assessment", back_populates="user")
    interviews = relationship("Interview", back_populates="user")
    user_skills = relationship("UserSkill", back_populates="user")

class UserSkill(Base):
    """User skills model"""
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_name = Column(String, index=True)
    proficiency_level = Column(String)  # novice, intermediate, advanced, expert
    years_of_experience = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="user_skills")

class JobPosting(Base):
    """Job posting model"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    company = Column(String)
    location = Column(String)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    experience_level = Column(Enum(ExperienceLevel))
    job_url = Column(String, nullable=True)
    posted_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = relationship("JobAnalysis", back_populates="job_posting")

class JobAnalysis(Base):
    """Job analysis model"""
    __tablename__ = "job_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)
    job_description = Column(Text)  # Original job description
    required_skills = Column(JSON)  # List of required skills
    technologies = Column(JSON)  # Technology stack
    soft_skills = Column(JSON)  # Soft skills required
    experience_required = Column(String)
    readiness_score = Column(Float, nullable=True)
    skill_gaps = Column(JSON)  # Skills the user is missing
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="job_analyses")
    job_posting = relationship("JobPosting", back_populates="analyses")
    learning_path = relationship("LearningPath", uselist=False, back_populates="job_analysis")

class LearningPath(Base):
    """Learning path model"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_analysis_id = Column(Integer, ForeignKey("job_analyses.id"))
    title = Column(String)
    description = Column(Text)
    skill_gaps = Column(JSON)  # Skills to focus on
    recommended_resources = Column(JSON)  # Videos, courses, docs
    video_playlists = Column(JSON)  # YouTube playlists
    estimated_hours = Column(Float)
    progress_percentage = Column(Float, default=0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")
    job_analysis = relationship("JobAnalysis", back_populates="learning_path")
    learning_modules = relationship("LearningModule", back_populates="learning_path")

class LearningModule(Base):
    """Learning module within a path"""
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    title = Column(String)
    description = Column(Text)
    resource_type = Column(String)  # video, article, course, project
    resource_url = Column(String)
    estimated_hours = Column(Float)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    learning_path = relationship("LearningPath", back_populates="learning_modules")

class Assessment(Base):
    """Assessment model"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_analysis_id = Column(Integer, ForeignKey("job_analyses.id"), nullable=True)
    title = Column(String)
    assessment_type = Column(Enum(AssessmentType))
    questions = Column(JSON)  # Assessment questions
    user_answers = Column(JSON, nullable=True)  # User's answers
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="assessments")

class Interview(Base):
    """Mock interview model"""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_analysis_id = Column(Integer, ForeignKey("job_analyses.id"), nullable=True)
    title = Column(String)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED)
    conversation_history = Column(JSON)  # Chat history
    feedback_report = Column(JSON, nullable=True)  # Detailed feedback
    overall_score = Column(Float, nullable=True)
    strengths = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    video_recording_url = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="interviews")

class CompanyIntelligence(Base):
    """Company interview patterns"""
    __tablename__ = "company_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    common_question_patterns = Column(JSON)
    frequently_asked_topics = Column(JSON)
    average_interview_duration = Column(Float)
    candidates_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Resume(Base):
    """User resume model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_url = Column(String)  # S3 or storage URL
    file_name = Column(String)
    extracted_skills = Column(JSON)  # Skills extracted from resume
    extracted_experience = Column(JSON)  # Experience details
    extracted_education = Column(JSON)  # Education details
    summary = Column(Text, nullable=True)  # Resume summary
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="resumes")

class Performance(Base):
    """User performance tracking model"""
    __tablename__ = "performances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True)
    learning_module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=True)
    activity_type = Column(String)  # assessment, interview, learning, practice
    score = Column(Float, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    skill_tags = Column(JSON)  # Skills practiced in this session
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="performances")

class SkillGapAnalysis(Base):
    """Skill gap analysis model comparing resume vs job requirements"""
    __tablename__ = "skill_gap_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_analysis_id = Column(Integer, ForeignKey("job_analyses.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    resume_skills = Column(JSON)  # Skills from resume
    required_skills = Column(JSON)  # Skills required by job
    matching_skills = Column(JSON)  # Skills user has
    gap_skills = Column(JSON)  # Skills user needs to learn
    gap_percentage = Column(Float)  # % of skills missing
    priority_skills = Column(JSON)  # Top skills to focus on
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="skill_gap_analyses")
    job_analysis = relationship("JobAnalysis")
    resume = relationship("Resume")
