"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, UserDetailResponse,
    TokenRequest, TokenResponse, TokenRefresh, UserSkillCreate, UserSkillResponse,
    ResumeResponse, SkillGapAnalysisResponse
)
from app.services.user_service import UserService
from app.services.resume_service import ResumeService
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

# Resume endpoints

@router.post("/me/resume/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    is_primary: bool = Form(default=True),
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse resume
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate file type
    allowed_types = [".pdf", ".docx", ".txt"]
    file_ext = "." + file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    try:
        file_content = await file.read()
        resume = await ResumeService.upload_resume(
            db, user.id, file_content, file.filename, is_primary
        )
        return resume
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume upload failed: {str(e)}"
        )

@router.get("/me/resume/primary", response_model=ResumeResponse)
async def get_primary_resume(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get primary resume
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    resume = ResumeService.get_primary_resume(db, user.id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No primary resume found"
        )
    
    return resume

@router.get("/me/resume", response_model=list[ResumeResponse])
async def get_my_resumes(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resumes for current user
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    resumes = ResumeService.get_user_resumes(db, user.id)
    return resumes

@router.get("/me/resume/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific resume
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    resume = ResumeService.get_user_resume(db, user.id, resume_id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume