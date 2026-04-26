"""
Analytics service - business logic for user analytics and reports
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta

from app.models import User, Assessment, Interview, JobAnalysis

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for analytics and reporting"""
    
    @staticmethod
    def get_user_analytics(db: Session, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get assessments
            assessments = db.query(Assessment).filter(Assessment.user_id == user_id).all()
            
            # Get interviews
            interviews = db.query(Interview).filter(Interview.user_id == user_id).all()
            
            # Get job analyses
            job_analyses = db.query(JobAnalysis).filter(JobAnalysis.user_id == user_id).all()
            
            # Calculate stats
            total_assessments = len(assessments)
            completed_assessments = len([a for a in assessments if a.score is not None])
            avg_assessment_score = sum([a.score for a in assessments if a.score]) / completed_assessments if completed_assessments else 0
            
            total_interviews = len(interviews)
            completed_interviews = len([i for i in interviews if i.overall_score is not None])
            avg_interview_score = sum([i.overall_score for i in interviews if i.overall_score]) / completed_interviews if completed_interviews else 0
            
            # Calculate readiness
            readiness_scores = [j.readiness_score for j in job_analyses if j.readiness_score]
            avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
            
            return {
                "total_assessments": total_assessments,
                "completed_assessments": completed_assessments,
                "avg_assessment_score": avg_assessment_score,
                "total_interviews": total_interviews,
                "completed_interviews": completed_interviews,
                "avg_interview_score": avg_interview_score,
                "avg_readiness": avg_readiness,
                "total_jobs_analyzed": len(job_analyses),
            }
        except Exception as e:
            logger.error(f"Analytics calculation error: {str(e)}")
            raise
    
    @staticmethod
    def get_skill_analytics(db: Session, user_id: int) -> Dict[str, Any]:
        """Get skill-specific analytics"""
        try:
            from app.models import UserSkill
            
            skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
            
            skill_analytics = []
            for skill in skills:
                skill_analytics.append({
                    "skill": skill.skill_name,
                    "proficiency": skill.proficiency_level,
                    "experience_years": skill.years_of_experience,
                })
            
            return {
                "skills": skill_analytics,
                "total_skills": len(skills),
            }
        except Exception as e:
            logger.error(f"Skill analytics error: {str(e)}")
            raise
    
    @staticmethod
    def get_progress_analytics(db: Session, user_id: int) -> Dict[str, Any]:
        """Get progress analytics over time"""
        try:
            assessments = db.query(Assessment).filter(
                Assessment.user_id == user_id
            ).all()
            
            interviews = db.query(Interview).filter(
                Interview.user_id == user_id
            ).all()
            
            # Group by week
            weekly_progress = []
            for i in range(4):
                week_ago = datetime.utcnow() - timedelta(weeks=i+1)
                week_start = week_ago - timedelta(days=week_ago.weekday())
                week_end = week_start + timedelta(days=7)
                
                week_assessments = [
                    a for a in assessments 
                    if a.created_at and week_start <= a.created_at <= week_end
                ]
                
                avg_score = (
                    sum([a.score for a in week_assessments if a.score]) / len(week_assessments)
                    if week_assessments else 0
                )
                
                weekly_progress.append({
                    "week": f"Week {i+1}",
                    "assessment_count": len(week_assessments),
                    "avg_score": avg_score,
                })
            
            return {
                "weekly_progress": weekly_progress,
                "total_assessments": len(assessments),
                "total_interviews": len(interviews),
            }
        except Exception as e:
            logger.error(f"Progress analytics error: {str(e)}")
            raise
