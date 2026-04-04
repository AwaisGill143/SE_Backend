"""
User service - business logic for user management
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.models import User, UserSkill
from app.schemas import UserCreate, UserUpdate, UserSkillCreate
from app.utils.auth import hash_password, verify_password

logger = logging.getLogger(__name__)

class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data.email) | (User.username == user_data.username)
            ).first()
            
            if existing_user:
                raise ValueError("User with this email or username already exists")
            
            # Create new user
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hash_password(user_data.password)
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created: {user.email}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"User creation error: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        try:
            user = UserService.get_user_by_id(db, user_id)
            
            if not user:
                raise ValueError("User not found")
            
            # Update fields
            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User updated: {user.email}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"User update error: {str(e)}")
            raise
    
    @staticmethod
    def get_user_skills(db: Session, user_id: int) -> List[UserSkill]:
        """Get all skills for a user"""
        return db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    
    @staticmethod
    def add_user_skill(db: Session, user_id: int, skill_data: UserSkillCreate) -> UserSkill:
        """Add a skill to user's profile"""
        try:
            skill = UserSkill(
                user_id=user_id,
                skill_name=skill_data.skill_name,
                proficiency_level=skill_data.proficiency_level,
                years_of_experience=skill_data.years_of_experience
            )
            
            db.add(skill)
            db.commit()
            db.refresh(skill)
            
            logger.info(f"Skill added for user {user_id}: {skill_data.skill_name}")
            return skill
            
        except Exception as e:
            db.rollback()
            logger.error(f"Skill addition error: {str(e)}")
            raise
    
    @staticmethod
    def delete_user_skill(db: Session, skill_id: int) -> bool:
        """Delete a user skill"""
        try:
            skill = db.query(UserSkill).filter(UserSkill.id == skill_id).first()
            
            if not skill:
                raise ValueError("Skill not found")
            
            db.delete(skill)
            db.commit()
            
            logger.info(f"Skill deleted: {skill_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Skill deletion error: {str(e)}")
            raise
