"""
Job parser service - business logic for job analysis
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

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
        """Analyze a job description and extract required skills"""
        try:
            analysis_result = await JobParserAPI.analyze_job_description(
                job_data.job_description
            )

            job_analysis = JobAnalysis(
                user_id=user_id,
                job_description=job_data.job_description,
                required_skills=analysis_result.get('required_skills', []),
                technologies=analysis_result.get('technologies', []),
                soft_skills=analysis_result.get('soft_skills', []),
                experience_required=analysis_result.get('experience_required', ''),
                skill_gaps=[]
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

    # ------------------------------------------------------------------ #
    #  Shared helper — single DB hit, reused by both methods below         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_user_skill_set(db: Session, user_id: int) -> set:
        """
        Return a lowercase set of the user's skill names.
        O(n) to build, O(1) per lookup — shared so callers avoid
        duplicate DB queries.
        """
        from app.services.user_service import UserService
        return {
            skill.skill_name.lower()
            for skill in UserService.get_user_skills(db, user_id)
        }

    # ------------------------------------------------------------------ #
    #  Readiness score                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def calculate_readiness_score(
        db: Session,
        user_id: int,
        job_analysis_id: int,
        user_skill_set: set = None   # optional — pass in to avoid extra DB hit
    ) -> float:
        """
        Calculate readiness score by comparing user skills with job requirements.
        Time complexity: O(n + m) where n = user skills, m = required skills.
        """
        try:
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")

            required_skills = job_analysis.required_skills
            if not required_skills:
                return 0.0

            # Build set once if not passed in
            if user_skill_set is None:
                user_skill_set = JobService._get_user_skill_set(db, user_id)

            # O(m) — each `in` check is O(1) against a set
            matched = sum(
                1 for skill in required_skills
                if skill.lower() in user_skill_set
            )

            readiness_score = round((matched / len(required_skills)) * 100, 2)

            job_analysis.readiness_score = readiness_score
            db.commit()

            logger.info(f"Readiness score calculated: {readiness_score}")
            return readiness_score

        except Exception as e:
            logger.error(f"Readiness score calculation error: {str(e)}")
            raise

    # ------------------------------------------------------------------ #
    #  Skill gap identification                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def identify_skill_gaps(
        db: Session,
        user_id: int,
        job_analysis_id: int,
        user_skill_set: set = None   # optional — pass in to avoid extra DB hit
    ) -> List[Dict[str, Any]]:
        """
        Identify skill gaps between user and job requirements.
        Time complexity: O(n + m) where n = user skills, m = required skills.
        """
        try:
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")

            # Build set once if not passed in
            if user_skill_set is None:
                user_skill_set = JobService._get_user_skill_set(db, user_id)

            # O(m) list comprehension — set lookup is O(1) per skill
            skill_gaps = [
                {
                    'skill': skill,
                    'current_level': 'none',
                    'required_level': 'intermediate',
                    'importance': 'high'
                }
                for skill in job_analysis.required_skills
                if skill.lower() not in user_skill_set
            ]

            job_analysis.skill_gaps = skill_gaps
            db.commit()

            logger.info(f"Identified {len(skill_gaps)} skill gaps")
            return skill_gaps

        except Exception as e:
            logger.error(f"Skill gap identification error: {str(e)}")
            raise

    # ------------------------------------------------------------------ #
    #  Combined helper — score + gaps in one DB round-trip                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def calculate_readiness_and_gaps(
        db: Session,
        user_id: int,
        job_analysis_id: int
    ) -> Dict[str, Any]:
        """
        Run both score and gap calculations with a single DB hit for user skills.
        Use this instead of calling the two methods separately.
        """
        user_skill_set = JobService._get_user_skill_set(db, user_id)

        score = JobService.calculate_readiness_score(
            db, user_id, job_analysis_id, user_skill_set=user_skill_set
        )
        gaps = JobService.identify_skill_gaps(
            db, user_id, job_analysis_id, user_skill_set=user_skill_set
        )

        return {'readiness_score': score, 'skill_gaps': gaps}

    # ------------------------------------------------------------------ #
    #  Job postings                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_job_analysis(db: Session, analysis_id: int) -> Optional[JobAnalysis]:
        return db.query(JobAnalysis).filter(JobAnalysis.id == analysis_id).first()

    @staticmethod
    def get_user_job_analyses(db: Session, user_id: int) -> List[JobAnalysis]:
        return db.query(JobAnalysis).filter(JobAnalysis.user_id == user_id).all()

    @staticmethod
    def create_job_posting(db: Session, job_data: Dict[str, Any]) -> JobPosting:
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
        return db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()