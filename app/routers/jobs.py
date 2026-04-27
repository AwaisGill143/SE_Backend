"""
Job parser endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    JobAnalysisRequest, JobAnalysisResponse, JobPostingCreate, JobPostingResponse,
    SkillGapAnalysisResponse, LearningRecommendationResponse, ConceptExplanationResponse
)
from app.services.job_service import JobService
from app.services.user_service import UserService
from app.services.resume_service import ResumeService
from app.utils.auth import get_current_user
from app.utils.external_apis import GroqAPI

router = APIRouter()

# NOTE: Order matters! More specific routes must come before generic ones with path parameters

@router.post("/analyze", response_model=JobAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_job_description(
    job_data: JobAnalysisRequest,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a job description and extract requirements
    """
    # Get current user
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        job_analysis = await JobService.analyze_job_description(db, user.id, job_data)
        return job_analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job analysis failed: {str(e)}"
        )

@router.get("/user/my-analyses")
async def get_my_analyses(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all job analyses for current user
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    analyses = JobService.get_user_job_analyses(db, user.id)
    return analyses

@router.get("/{analysis_id}/readiness-score")
async def get_readiness_score(
    analysis_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get readiness score for a job analysis
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    job_analysis = JobService.get_job_analysis(db, analysis_id)
    if not job_analysis or job_analysis.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    try:
        score = JobService.calculate_readiness_score(db, user.id, analysis_id)
        return {"readiness_score": score}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Score calculation failed: {str(e)}"
        )

@router.get("/{analysis_id}/skill-gaps")
async def get_skill_gaps(
    analysis_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get skill gaps for a job analysis
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    job_analysis = JobService.get_job_analysis(db, analysis_id)
    if not job_analysis or job_analysis.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    try:
        skill_gaps = JobService.identify_skill_gaps(db, user.id, analysis_id)
        return {"skill_gaps": skill_gaps}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill gap identification failed: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=JobAnalysisResponse)
async def get_job_analysis(
    analysis_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific job analysis
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    job_analysis = JobService.get_job_analysis(db, analysis_id)
    
    if not job_analysis or job_analysis.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    return job_analysis

@router.get("/{analysis_id}/skill-gap-analysis", response_model=SkillGapAnalysisResponse)
async def analyze_skill_gaps(
    analysis_id: int,
    resume_id: int = None,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze skill gaps comparing resume with job requirements
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    job_analysis = JobService.get_job_analysis(db, analysis_id)
    if not job_analysis or job_analysis.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    try:
        skill_gap_analysis = await ResumeService.analyze_skill_gaps(
            db, user.id, analysis_id, resume_id
        )
        return skill_gap_analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill gap analysis failed: {str(e)}"
        )

@router.get("/{analysis_id}/learning-recommendations", response_model=LearningRecommendationResponse)
async def get_learning_recommendations(
    analysis_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Groq-powered learning recommendations based on skill gaps
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    job_analysis = JobService.get_job_analysis(db, analysis_id)
    if not job_analysis or job_analysis.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    try:
        # Get skill gap analysis
        skill_gap_analysis = ResumeService.get_skill_gap_analysis(db, user.id, analysis_id)
        
        if not skill_gap_analysis:
            # Create one first
            skill_gap_analysis = await ResumeService.analyze_skill_gaps(db, user.id, analysis_id)
        
        gap_skills = skill_gap_analysis.gap_skills or []
        resume_skills = skill_gap_analysis.resume_skills or []
        
        # Get Groq recommendations
        recommendations = await GroqAPI.generate_learning_recommendations(gap_skills, resume_skills)
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.post("/concepts/{skill_name}/explain", response_model=ConceptExplanationResponse)
async def explain_concept(
    skill_name: str,
    level: str = "beginner",
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Groq-powered explanation of a skill/concept
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        explanation = await GroqAPI.teach_concept(skill_name, level)
        return explanation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate explanation: {str(e)}"
        )
