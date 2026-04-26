"""
Analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.user_service import UserService
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("")
async def get_analytics(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive user analytics
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        analytics = AnalyticsService.get_user_analytics(db, user.id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics fetch failed: {str(e)}"
        )

@router.get("/skills")
async def get_skill_analytics(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get skill-level analytics
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        analytics = AnalyticsService.get_skill_analytics(db, user.id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skill analytics fetch failed: {str(e)}"
        )

@router.get("/progress")
async def get_progress_analytics(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress analytics over time
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        analytics = AnalyticsService.get_progress_analytics(db, user.id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Progress analytics fetch failed: {str(e)}"
        )
