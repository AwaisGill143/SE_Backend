"""
Interview simulator endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    InterviewStartRequest, InterviewDetailResponse, InterviewSubmitResponse,
    InterviewFeedback
)
from app.services.interview_service import InterviewService
from app.services.user_service import UserService
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("", response_model=InterviewDetailResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    interview_data: InterviewStartRequest,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new mock interview
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        interview = await InterviewService.start_interview(
            db,
            user.id,
            interview_data.title,
            interview_data.job_analysis_id,
            interview_data.duration_minutes
        )
        return interview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview creation failed: {str(e)}"
        )

@router.get("/{interview_id}", response_model=InterviewDetailResponse)
async def get_interview(
    interview_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific interview
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interview = InterviewService.get_interview(db, interview_id)
    
    if not interview or interview.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    return interview

@router.get("")
async def get_my_interviews(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all interviews for current user
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interviews = InterviewService.get_user_interviews(db, user.id)
    return interviews

@router.post("/{interview_id}/respond")
async def respond_to_interview_question(
    interview_id: int,
    response_data: dict,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a response to an interview question
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interview = InterviewService.get_interview(db, interview_id)
    
    if not interview or interview.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    user_message = response_data.get("message", "")
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    try:
        ai_response = await InterviewService.process_interview_response(
            db,
            interview_id,
            user_message
        )
        
        return {
            "interview_id": interview_id,
            "user_message": user_message,
            "ai_response": ai_response
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Response processing failed: {str(e)}"
        )

@router.post("/{interview_id}/end", response_model=InterviewFeedback)
async def end_interview(
    interview_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End the interview and get feedback
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interview = InterviewService.get_interview(db, interview_id)
    
    if not interview or interview.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    try:
        completed_interview = await InterviewService.end_interview(db, interview_id)
        
        return {
            "id": completed_interview.id,
            "overall_score": completed_interview.overall_score,
            "strengths": completed_interview.strengths,
            "improvement_areas": completed_interview.improvement_areas,
            "detailed_feedback": completed_interview.feedback_report.get('detailed_feedback', '') if completed_interview.feedback_report else "",
            "duration_seconds": completed_interview.duration_seconds,
            "completed_at": completed_interview.completed_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interview end failed: {str(e)}"
        )

@router.get("/{interview_id}/feedback")
async def get_interview_feedback(
    interview_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback for a completed interview
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interview = InterviewService.get_interview(db, interview_id)
    
    if not interview or interview.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if not interview.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview not yet completed"
        )
    
    return {
        "interview_id": interview_id,
        "overall_score": interview.overall_score,
        "strengths": interview.strengths,
        "improvement_areas": interview.improvement_areas,
        "detailed_feedback": interview.feedback_report,
        "duration_seconds": interview.duration_seconds,
        "completed_at": interview.completed_at
    }

@router.get("/{interview_id}/conversation")
async def get_interview_conversation(
    interview_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the conversation history of an interview
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interview = InterviewService.get_interview(db, interview_id)
    
    if not interview or interview.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    return {
        "interview_id": interview_id,
        "conversation": interview.conversation_history or []
    }

@router.get("/user/completed")
async def get_completed_interviews(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all completed interviews for current user
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interviews = InterviewService.get_user_completed_interviews(db, user.id)
    return interviews
