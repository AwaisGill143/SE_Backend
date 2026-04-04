"""
Assessment endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AssessmentRequest, AssessmentResponse, AssessmentAnswerSubmit
)
from app.services.assessment_service import AssessmentService
from app.services.user_service import UserService
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentRequest,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new assessment
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        assessment = await AssessmentService.create_assessment(
            db,
            user.id,
            assessment_data.assessment_type,
            assessment_data.job_analysis_id,
            assessment_data.difficulty or 'medium'
        )
        return assessment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment creation failed: {str(e)}"
        )

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific assessment
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    assessment = AssessmentService.get_assessment(db, assessment_id)
    
    if not assessment or assessment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return assessment

@router.get("")
async def get_my_assessments(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all assessments for current user
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    assessments = AssessmentService.get_user_assessments(db, user.id)
    return assessments

@router.post("/{assessment_id}/submit", response_model=AssessmentResponse)
async def submit_assessment(
    assessment_id: int,
    submission: AssessmentAnswerSubmit,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit assessment answers
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    assessment = AssessmentService.get_assessment(db, assessment_id)
    if not assessment or assessment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    try:
        updated_assessment = await AssessmentService.submit_assessment(
            db,
            assessment_id,
            submission.user_answers,
            submission.code
        )
        return updated_assessment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assessment submission failed: {str(e)}"
        )

@router.get("/{assessment_id}/score")
async def get_assessment_score(
    assessment_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get assessment score
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    assessment = AssessmentService.get_assessment(db, assessment_id)
    
    if not assessment or assessment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if not assessment.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment not yet submitted"
        )
    
    return {
        "assessment_id": assessment.id,
        "score": assessment.score,
        "feedback": assessment.feedback,
        "time_taken_seconds": assessment.time_taken_seconds
    }

@router.get("/{assessment_id}/details")
async def get_assessment_details(
    assessment_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed assessment information including questions and answers
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    assessment = AssessmentService.get_assessment(db, assessment_id)
    
    if not assessment or assessment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return {
        "id": assessment.id,
        "title": assessment.title,
        "type": assessment.assessment_type,
        "questions": assessment.questions,
        "user_answers": assessment.user_answers,
        "score": assessment.score,
        "feedback": assessment.feedback,
        "completed_at": assessment.completed_at
    }
