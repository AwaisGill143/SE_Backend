"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, UserDetailResponse,
    TokenRequest, TokenResponse, TokenRefresh, UserSkillCreate, UserSkillResponse
)
from app.services.user_service import UserService
from app.utils.auth import (
    create_access_token, create_refresh_token, verify_token, 
    get_current_user, hash_password
)
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: TokenRequest, db: Session = Depends(get_db)):
    """
    Login and get JWT tokens
    """
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    try:
        payload = verify_token(token_data.refresh_token)
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = UserService.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        new_access_token = create_access_token(data={"sub": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID
    """
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/me", response_model=UserDetailResponse)
async def update_profile(
    user_data: UserUpdate,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        updated_user = UserService.update_user(db, user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Skills endpoints

@router.get("/me/skills", response_model=list[UserSkillResponse])
async def get_my_skills(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's skills
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    skills = UserService.get_user_skills(db, user.id)
    return skills

@router.post("/me/skills", response_model=UserSkillResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    skill_data: UserSkillCreate,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a skill to current user
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        skill = UserService.add_user_skill(db, user.id, skill_data)
        return skill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user skill
    """
    try:
        UserService.delete_user_skill(db, skill_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
