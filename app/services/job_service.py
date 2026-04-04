"""
Job parser service - business logic for job analysis
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import json

from app.models import JobAnalysis, JobPosting
from app.schemas import JobAnalysisRequest
from app.utils.external_apis import JobParserAPI

logger = logging.getLogger(__name__)

class JobService:
    """Service for job analysis operations"""
    
    @staticmethod
    async def analyze_job_description(
        db: Session,
        user_id: int,
        job_data: JobAnalysisRequest
    ) -> JobAnalysis:
        """
        Analyze a job description and extract required skills
        """
        try:
            # Use LLM to analyze the job description
            analysis_result = await JobParserAPI.analyze_job_description(job_data.job_description)
            
            # Create job analysis record
            job_analysis = JobAnalysis(
                user_id=user_id,
                job_description=job_data.job_description,
                required_skills=analysis_result.get('required_skills', []),
                technologies=analysis_result.get('technologies', []),
                soft_skills=analysis_result.get('soft_skills', []),
                experience_required=analysis_result.get('experience_required', ''),
                skill_gaps=[]  # Will be populated when compared with user skills
            )
            
            db.add(job_analysis)
            db.commit()
            db.refresh(job_analysis)
            
            logger.info(f"Job analysis created for user {user_id}")
            return job_analysis
            
        except Exception as e:
            db.rollback()
            logger.error(f"Job analysis error: {str(e)}")
            raise
    
    @staticmethod
    def get_job_analysis(db: Session, analysis_id: int) -> Optional[JobAnalysis]:
        """Get job analysis by ID"""
        return db.query(JobAnalysis).filter(JobAnalysis.id == analysis_id).first()
    
    @staticmethod
    def get_user_job_analyses(db: Session, user_id: int) -> List[JobAnalysis]:
        """Get all job analyses for a user"""
        return db.query(JobAnalysis).filter(JobAnalysis.user_id == user_id).all()
    
    @staticmethod
    def calculate_readiness_score(
        db: Session,
        user_id: int,
        job_analysis_id: int
    ) -> float:
        """
        Calculate readiness score by comparing user skills with job requirements
        """
        try:
            from app.services.user_service import UserService
            
            # Get job analysis
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")
            
            # Get user skills
            user_skills = UserService.get_user_skills(db, user_id)
            user_skill_names = [skill.skill_name.lower() for skill in user_skills]
            
            # Calculate matching skills
            required_skills = [s.lower() for s in job_analysis.required_skills]
            matched_skills = len([s for s in required_skills if s in user_skill_names])
            
            # Calculate score (0-100)
            readiness_score = (matched_skills / len(required_skills) * 100) if required_skills else 0
            
            # Update job analysis with score
            job_analysis.readiness_score = readiness_score
            db.commit()
            
            logger.info(f"Readiness score calculated: {readiness_score}")
            return readiness_score
            
        except Exception as e:
            logger.error(f"Readiness score calculation error: {str(e)}")
            raise
    
    @staticmethod
    def identify_skill_gaps(
        db: Session,
        user_id: int,
        job_analysis_id: int
    ) -> List[Dict[str, Any]]:
        """
        Identify skill gaps between user and job requirements
        """
        try:
            from app.services.user_service import UserService
            
            # Get job analysis
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")
            
            # Get user skills
            user_skills = UserService.get_user_skills(db, user_id)
            user_skill_dict = {
                skill.skill_name.lower(): {
                    'proficiency': skill.proficiency_level,
                    'experience': skill.years_of_experience
                }
                for skill in user_skills
            }
            
            # Identify gaps
            skill_gaps = []
            for required_skill in job_analysis.required_skills:
                if required_skill.lower() not in user_skill_dict:
                    skill_gaps.append({
                        'skill': required_skill,
                        'current_level': 'none',
                        'required_level': 'intermediate',  # assumption
                        'importance': 'high'
                    })
            
            # Update job analysis
            job_analysis.skill_gaps = skill_gaps
            db.commit()
            
            logger.info(f"Identified {len(skill_gaps)} skill gaps")
            return skill_gaps
            
        except Exception as e:
            logger.error(f"Skill gap identification error: {str(e)}")
            raise
    
    @staticmethod
    def create_job_posting(db: Session, job_data: Dict[str, Any]) -> JobPosting:
        """Create a new job posting"""
        try:
            job_posting = JobPosting(**job_data)
            db.add(job_posting)
            db.commit()
            db.refresh(job_posting)
            
            logger.info(f"Job posting created: {job_posting.title}")
            return job_posting
            
        except Exception as e:
            db.rollback()
            logger.error(f"Job posting creation error: {str(e)}")
            raise
    
    @staticmethod
    def get_job_posting(db: Session, job_posting_id: int) -> Optional[JobPosting]:
        """Get job posting by ID"""
        return db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
