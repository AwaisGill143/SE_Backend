"""
Job parser endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    JobAnalysisRequest, JobAnalysisResponse, JobPostingCreate, JobPostingResponse
)
from app.services.job_service import JobService
from app.services.user_service import UserService
from app.utils.auth import get_current_user

router = APIRouter()

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
