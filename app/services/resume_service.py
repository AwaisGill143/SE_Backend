"""
Resume service - business logic for resume upload and skill extraction
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import io
from datetime import datetime

from app.models import Resume, User, UserSkill, SkillGapAnalysis
from app.utils.external_apis import ResumeParserAPI
from app.config import settings

logger = logging.getLogger(__name__)

class ResumeService:
    """Service for resume operations"""
    
    @staticmethod
    async def upload_resume(
        db: Session,
        user_id: int,
        file_content: bytes,
        file_name: str,
        is_primary: bool = True
    ) -> Resume:
        """
        Upload resume and extract skills
        """
        try:
            # Extract text and skills from resume file
            import tempfile
            import os

            extracted_data: Dict[str, Any] = {"technical_skills": [], "work_experience": [], "education": []}

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name

            try:
                extracted_data = await ResumeParserAPI.extract_skills_from_file(tmp_path)
            except Exception as parse_err:
                # Fallback: extract text and use Groq if OpenAI is unavailable
                logger.warning(f"Primary parser failed ({parse_err}), using Groq fallback")
                try:
                    text = ResumeService._read_text(file_content, file_name)
                    extracted_data = await ResumeService._extract_skills_groq(text)
                except Exception as fallback_err:
                    logger.warning(f"Groq fallback also failed ({fallback_err}), storing with empty skills")
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

            # If is_primary, unset other primary resumes
            if is_primary:
                db.query(Resume).filter(
                    Resume.user_id == user_id,
                    Resume.is_primary == True
                ).update({"is_primary": False})
            
            # Create resume record
            resume = Resume(
                user_id=user_id,
                file_url=f"s3://careerlaunch-uploads/{user_id}/{file_name}",  # S3 URL format
                file_name=file_name,
                extracted_skills=extracted_data.get('technical_skills', []),
                extracted_experience=extracted_data.get('work_experience', []),
                extracted_education=extracted_data.get('education', []),
                summary=None,
                is_primary=is_primary
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            # Update user skills based on resume
            await ResumeService._update_user_skills(db, user_id, extracted_data)
            
            logger.info(f"Resume uploaded for user {user_id}: {file_name}")
            return resume
            
        except Exception as e:
            db.rollback()
            logger.error(f"Resume upload error: {str(e)}")
            raise
    
    @staticmethod
    def _read_text(file_content: bytes, file_name: str) -> str:
        """Extract plain text from resume bytes, with PDF/DOCX support."""
        fn = file_name.lower()
        if fn.endswith(".pdf"):
            try:
                import io
                from PyPDF2 import PdfReader
                reader = PdfReader(io.BytesIO(file_content))
                return " ".join(p.extract_text() or "" for p in reader.pages)
            except Exception:
                pass
        elif fn.endswith(".docx"):
            try:
                import io
                from docx import Document
                doc = Document(io.BytesIO(file_content))
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                pass
        return file_content.decode("utf-8", errors="ignore")

    @staticmethod
    async def _extract_skills_groq(text: str) -> Dict[str, Any]:
        """Extract skills via Groq as fallback."""
        import json as _json
        try:
            from groq import Groq
            from app.config import settings
            client = Groq(api_key=settings.GROQ_API_KEY)
            prompt = (
                "Extract a JSON object with keys 'technical_skills' (list of strings), "
                "'work_experience' (list), 'education' (list) from this resume. "
                "Return ONLY valid JSON, no markdown.\n\nResume:\n" + text[:3000]
            )
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            parsed = _json.loads(raw)
            return {
                "technical_skills": parsed.get("technical_skills", []),
                "work_experience": parsed.get("work_experience", []),
                "education": parsed.get("education", []),
            }
        except Exception as e:
            logger.warning(f"Groq skill extraction failed: {e}")
            return {"technical_skills": [], "work_experience": [], "education": []}

    @staticmethod
    async def _update_user_skills(
        db: Session,
        user_id: int,
        extracted_data: Dict[str, Any]
    ) -> None:
        """
        Update user skills based on resume extraction
        """
        try:
            technical_skills = extracted_data.get('technical_skills', [])
            years_of_experience = extracted_data.get('years_of_experience', 0)
            
            # Average experience level per skill
            avg_experience = years_of_experience / len(technical_skills) if technical_skills else 0
            
            # Map years to proficiency level
            def years_to_proficiency(years: float) -> str:
                if years < 1:
                    return "novice"
                elif years < 3:
                    return "intermediate"
                elif years < 5:
                    return "advanced"
                else:
                    return "expert"
            
            proficiency = years_to_proficiency(avg_experience)
            
            # Add/update user skills
            for skill in technical_skills:
                # Check if skill already exists
                existing_skill = db.query(UserSkill).filter(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_name.ilike(skill)
                ).first()
                
                if existing_skill:
                    # Update existing skill
                    existing_skill.proficiency_level = proficiency
                    existing_skill.years_of_experience = avg_experience
                else:
                    # Create new skill
                    user_skill = UserSkill(
                        user_id=user_id,
                        skill_name=skill,
                        proficiency_level=proficiency,
                        years_of_experience=avg_experience
                    )
                    db.add(user_skill)
            
            db.commit()
            logger.info(f"Updated {len(technical_skills)} skills for user {user_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Skills update error: {str(e)}")
            raise
    
    @staticmethod
    def get_user_resume(db: Session, user_id: int, resume_id: int) -> Optional[Resume]:
        """Get a specific resume by ID"""
        return db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_resumes(db: Session, user_id: int) -> List[Resume]:
        """Get all resumes for a user"""
        return db.query(Resume).filter(Resume.user_id == user_id).all()
    
    @staticmethod
    def get_primary_resume(db: Session, user_id: int) -> Optional[Resume]:
        """Get primary resume for a user"""
        return db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.is_primary == True
        ).first()
    
    @staticmethod
    async def analyze_skill_gaps(
        db: Session,
        user_id: int,
        job_analysis_id: int,
        resume_id: Optional[int] = None
    ) -> SkillGapAnalysis:
        """
        Analyze skill gaps by comparing resume skills with job requirements
        """
        try:
            from app.services.job_service import JobService
            
            # Get job analysis
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")
            
            # Get resume (primary if not specified)
            if resume_id:
                resume = ResumeService.get_user_resume(db, user_id, resume_id)
            else:
                resume = ResumeService.get_primary_resume(db, user_id)
            
            resume_skills = resume.extracted_skills if resume else []
            required_skills = job_analysis.required_skills or []
            
            # Find matching and gap skills
            resume_skills_lower = [s.lower() for s in resume_skills]
            required_skills_lower = [s.lower() for s in required_skills]
            
            matching_skills = [s for s in required_skills if s.lower() in resume_skills_lower]
            gap_skills = [s for s in required_skills if s.lower() not in resume_skills_lower]
            
            # Calculate gap percentage
            gap_percentage = (len(gap_skills) / len(required_skills) * 100) if required_skills else 0
            
            # Identify priority skills (gaps that are high importance)
            priority_skills = gap_skills[:5]  # Top 5 gap skills
            
            # Check if skill gap analysis already exists
            existing_analysis = db.query(SkillGapAnalysis).filter(
                SkillGapAnalysis.user_id == user_id,
                SkillGapAnalysis.job_analysis_id == job_analysis_id
            ).first()
            
            if existing_analysis:
                # Update existing analysis
                existing_analysis.resume_skills = resume_skills
                existing_analysis.required_skills = required_skills
                existing_analysis.matching_skills = matching_skills
                existing_analysis.gap_skills = gap_skills
                existing_analysis.gap_percentage = gap_percentage
                existing_analysis.priority_skills = priority_skills
                db.commit()
                db.refresh(existing_analysis)
                return existing_analysis
            
            # Create new skill gap analysis
            skill_gap_analysis = SkillGapAnalysis(
                user_id=user_id,
                job_analysis_id=job_analysis_id,
                resume_id=resume.id if resume else None,
                resume_skills=resume_skills,
                required_skills=required_skills,
                matching_skills=matching_skills,
                gap_skills=gap_skills,
                gap_percentage=gap_percentage,
                priority_skills=priority_skills
            )
            
            db.add(skill_gap_analysis)
            db.commit()
            db.refresh(skill_gap_analysis)
            
            logger.info(f"Skill gap analysis created: {len(gap_skills)} gaps identified")
            return skill_gap_analysis
            
        except Exception as e:
            db.rollback()
            logger.error(f"Skill gap analysis error: {str(e)}")
            raise
    
    @staticmethod
    def get_skill_gap_analysis(
        db: Session,
        user_id: int,
        job_analysis_id: int
    ) -> Optional[SkillGapAnalysis]:
        """Get skill gap analysis for a job"""
        return db.query(SkillGapAnalysis).filter(
            SkillGapAnalysis.user_id == user_id,
            SkillGapAnalysis.job_analysis_id == job_analysis_id
        ).first()