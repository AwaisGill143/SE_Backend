"""
Analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import PerformanceResponse
from app.models import Performance
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

# Performance endpoints

@router.post("/performance", response_model=PerformanceResponse, status_code=status.HTTP_201_CREATED)
async def log_performance(
    activity_type: str,
    score: float = None,
    time_taken_seconds: int = None,
    feedback: str = None,
    skill_tags: List[str] = None,
    assessment_id: int = None,
    interview_id: int = None,
    learning_module_id: int = None,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log user performance for an activity
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        performance = Performance(
            user_id=user.id,
            activity_type=activity_type,
            score=score,
            time_taken_seconds=time_taken_seconds,
            feedback=feedback,
            skill_tags=skill_tags or [],
            assessment_id=assessment_id,
            interview_id=interview_id,
            learning_module_id=learning_module_id
        )
        
        db.add(performance)
        db.commit()
        db.refresh(performance)
        
        return performance
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to log performance: {str(e)}"
        )

@router.get("/performance", response_model=List[PerformanceResponse])
async def get_my_performance(
    activity_type: str = None,
    limit: int = 50,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's performance history
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = db.query(Performance).filter(Performance.user_id == user.id)
    
    if activity_type:
        query = query.filter(Performance.activity_type == activity_type)
    
    performances = query.order_by(Performance.completed_at.desc()).limit(limit).all()
    return performances

@router.get("/performance/stats")
async def get_performance_stats(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get performance statistics for user
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        from sqlalchemy import func
        
        # Get performance stats
        stats = db.query(
            Performance.activity_type,
            func.count(Performance.id).label("count"),
            func.avg(Performance.score).label("avg_score"),
            func.avg(Performance.time_taken_seconds).label("avg_time")
        ).filter(
            Performance.user_id == user.id
        ).group_by(
            Performance.activity_type
        ).all()
        
        stats_dict = {}
        for stat in stats:
            stats_dict[stat[0]] = {
                "count": stat[1],
                "avg_score": round(stat[2], 2) if stat[2] else None,
                "avg_time_seconds": round(stat[3], 2) if stat[3] else None
            }
        
        return stats_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get stats: {str(e)}"
        )
