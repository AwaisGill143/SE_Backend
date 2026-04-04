"""
Learning paths endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    LearningPathResponse, LearningPathCreateRequest, LearningModuleResponse
)
from app.services.learning_path_service import LearningPathService
from app.services.user_service import UserService
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    path_data: LearningPathCreateRequest,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a personalized learning path based on job analysis
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        learning_path = await LearningPathService.create_learning_path(
            db, user.id, path_data.job_analysis_id
        )
        return learning_path
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Learning path creation failed: {str(e)}"
        )

@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific learning path
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    learning_path = LearningPathService.get_learning_path(db, path_id)
    
    if not learning_path or learning_path.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    return learning_path

@router.get("")
async def get_my_learning_paths(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all learning paths for current user
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    learning_paths = LearningPathService.get_user_learning_paths(db, user.id)
    return learning_paths

@router.post("/{path_id}/modules/{module_id}/complete", status_code=status.HTTP_200_OK)
async def complete_module(
    path_id: int,
    module_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a learning module as completed
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify ownership
    learning_path = LearningPathService.get_learning_path(db, path_id)
    if not learning_path or learning_path.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    try:
        updated_module = LearningPathService.update_module_completion(db, module_id, True)
        
        # Update learning path progress
        updated_path = LearningPathService.update_learning_path_progress(db, path_id)
        
        return {
            "message": "Module marked as completed",
            "module": updated_module,
            "learning_path_progress": updated_path.progress_percentage
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module completion failed: {str(e)}"
        )

@router.post("/{path_id}/modules/{module_id}/incomplete", status_code=status.HTTP_200_OK)
async def incomplete_module(
    path_id: int,
    module_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a learning module as incomplete
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify ownership
    learning_path = LearningPathService.get_learning_path(db, path_id)
    if not learning_path or learning_path.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    try:
        updated_module = LearningPathService.update_module_completion(db, module_id, False)
        
        # Update learning path progress
        updated_path = LearningPathService.update_learning_path_progress(db, path_id)
        
        return {
            "message": "Module marked as incomplete",
            "module": updated_module,
            "learning_path_progress": updated_path.progress_percentage
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module update failed: {str(e)}"
        )

@router.get("/{path_id}/progress")
async def get_learning_path_progress(
    path_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress of a learning path
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    learning_path = LearningPathService.get_learning_path(db, path_id)
    
    if not learning_path or learning_path.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    return {
        "path_id": learning_path.id,
        "progress_percentage": learning_path.progress_percentage,
        "is_completed": learning_path.is_completed,
        "estimated_hours": learning_path.estimated_hours
    }
