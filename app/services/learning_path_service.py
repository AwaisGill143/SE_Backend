"""
Learning paths service - business logic for personalized learning paths
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

from app.models import LearningPath, LearningModule
from app.utils.external_apis import YouTubeAPI, PineconeAPI

logger = logging.getLogger(__name__)

class LearningPathService:
    """Service for learning path operations"""
    
    @staticmethod
    async def create_learning_path(
        db: Session,
        user_id: int,
        job_analysis_id: int
    ) -> LearningPath:
        """
        Create a personalized learning path based on job analysis and resume
        """
        try:
            from app.services.job_service import JobService
            from app.services.resume_service import ResumeService
            
            # Get job analysis
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")
            
            # Get skill gap analysis with resume comparison
            skill_gap_analysis = ResumeService.get_skill_gap_analysis(db, user_id, job_analysis_id)
            
            if not skill_gap_analysis:
                # Create skill gap analysis if doesn't exist
                skill_gap_analysis = await ResumeService.analyze_skill_gaps(db, user_id, job_analysis_id)
            
            # Use gap skills from analysis
            priority_skills = skill_gap_analysis.priority_skills or skill_gap_analysis.gap_skills[:5]
            
            # Get learning resources focused on gap skills
            resources = await LearningPathService._get_learning_resources(priority_skills)
            
            # Create learning path
            learning_path = LearningPath(
                user_id=user_id,
                job_analysis_id=job_analysis_id,
                title=f"Learning Path - {job_analysis.job_description[:30]}...",
                description=f"Personalized path to close {len(skill_gap_analysis.gap_skills)} skill gaps",
                skill_gaps=skill_gap_analysis.gap_skills,
                recommended_resources=resources.get('resources', []),
                video_playlists=resources.get('videos', []),
                estimated_hours=resources.get('estimated_hours', 0)
            )
            
            db.add(learning_path)
            db.commit()
            db.refresh(learning_path)
            
            # Create learning modules with concept teaching from Groq
            await LearningPathService._create_learning_modules(
                db, learning_path.id, priority_skills, resources
            )
            
            logger.info(f"Learning path created for user {user_id} with {len(priority_skills)} focus skills")
            return learning_path
            
        except Exception as e:
            db.rollback()
            logger.error(f"Learning path creation error: {str(e)}")
            raise
    
    @staticmethod
    async def _get_prioritized_skill_gaps(skill_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort skill gaps by importance"""
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        return sorted(
            skill_gaps,
            key=lambda x: priority_order.get(x.get('importance', 'medium'), 1)
        )
    
    @staticmethod
    async def _get_learning_resources(skills: List[str]) -> Dict[str, Any]:
        """Gather learning resources for skills"""
        try:
            resources = []
            videos = []
            total_hours = 0
            
            # Get YouTube videos for each skill
            video_results = await YouTubeAPI.search_learning_videos(skills, max_results=3)
            videos.extend(video_results)
            
            # Add curated resources based on skills
            resource_map = {
                "React.js": "https://react.dev",
                "TypeScript": "https://www.typescriptlang.org/docs",
                "System Design": "https://www.youtube.com/results?search_query=system+design+interview",
                "Python": "https://docs.python.org/3",
                "Docker": "https://docs.docker.com",
                "AWS": "https://aws.amazon.com/training",
                "GraphQL": "https://graphql.org/learn",
                "Machine Learning": "https://www.coursera.org/specializations/machine-learning",
            }
            
            for skill in skills[:5]:
                url = resource_map.get(skill, f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}")
                resources.append({
                    'type': 'course',
                    'title': f'{skill} - Complete Course',
                    'url': url
                })
            
            # Add generic resources
            if not resources:
                resources.append({
                    'type': 'documentation',
                    'title': 'Official Documentation',
                    'url': 'https://docs.example.com'
                })
            
            # Estimate hours (8 hours per skill)
            total_hours = len(skills) * 8
            
            return {
                'resources': resources,
                'videos': videos,
                'estimated_hours': total_hours
            }
            
        except Exception as e:
            logger.error(f"Resource gathering error: {str(e)}")
            return {'resources': [], 'videos': [], 'estimated_hours': 0}
    
    @staticmethod
    async def _create_learning_modules(
        db: Session,
        learning_path_id: int,
        skills: List[str],
        resources: Dict[str, Any]
    ) -> None:
        """Create learning modules with concept teaching for a learning path"""
        try:
            from app.utils.external_apis import GroqAPI
            
            # Create concept teaching modules using Groq
            for idx, skill in enumerate(skills[:5]):  # Top 5 skills
                # Get Groq explanation for the concept
                try:
                    explanation = await GroqAPI.teach_concept(skill, "beginner")
                    
                    module = LearningModule(
                        learning_path_id=learning_path_id,
                        title=f"Learn {skill} - Concept Explanation",
                        description=f"AI-powered explanation of {skill} fundamentals",
                        resource_type='concept',
                        resource_url='',  # Internal content
                        estimated_hours=2.0
                    )
                except:
                    # Fallback if Groq fails
                    module = LearningModule(
                        learning_path_id=learning_path_id,
                        title=f"Master {skill}",
                        description=f"Complete guide to understanding {skill}",
                        resource_type='course',
                        resource_url='https://www.udemy.com',
                        estimated_hours=2.0
                    )
                
                db.add(module)
            
            # Create modules for YouTube videos
            for idx, video in enumerate(resources.get('videos', [])[:5]):
                module = LearningModule(
                    learning_path_id=learning_path_id,
                    title=video.get('title', f'Video {idx+1}'),
                    description=f"Video tutorial by {video.get('channel', 'Expert')}: {video.get('title', 'Learning material')}",
                    resource_type='video',
                    resource_url=video.get('url', ''),
                    estimated_hours=1.5
                )
                db.add(module)
            
            # Create modules for other resources
            for resource in resources.get('resources', [])[:5]:
                module = LearningModule(
                    learning_path_id=learning_path_id,
                    title=resource.get('title', 'Resource'),
                    description=f"Explore {resource.get('type', 'learning resource')}",
                    resource_type=resource.get('type', 'article'),
                    resource_url=resource.get('url', ''),
                    estimated_hours=2.0
                )
                db.add(module)
            
            db.commit()
            logger.info(f"Learning modules created for path {learning_path_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Module creation error: {str(e)}")
    
    @staticmethod
    def get_learning_path(db: Session, path_id: int) -> Optional[LearningPath]:
        """Get learning path by ID"""
        return db.query(LearningPath).filter(LearningPath.id == path_id).first()
    
    @staticmethod
    def get_user_learning_paths(db: Session, user_id: int) -> List[LearningPath]:
        """Get all learning paths for a user"""
        return db.query(LearningPath).filter(LearningPath.user_id == user_id).all()
    
    @staticmethod
    def update_module_completion(db: Session, module_id: int, is_completed: bool) -> LearningModule:
        """Mark a learning module as completed"""
        try:
            module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
            
            if not module:
                raise ValueError("Module not found")
            
            module.is_completed = is_completed
            db.commit()
            db.refresh(module)
            
            logger.info(f"Module {module_id} completion updated")
            return module
            
        except Exception as e:
            db.rollback()
            logger.error(f"Module update error: {str(e)}")
            raise
    
    @staticmethod
    def update_learning_path_progress(db: Session, path_id: int) -> LearningPath:
        """Update learning path progress percentage"""
        try:
            learning_path = LearningPathService.get_learning_path(db, path_id)
            
            if not learning_path:
                raise ValueError("Learning path not found")
            
            # Calculate progress
            modules = db.query(LearningModule).filter(
                LearningModule.learning_path_id == path_id
            ).all()
            
            if modules:
                completed = len([m for m in modules if m.is_completed])
                progress = (completed / len(modules)) * 100
                learning_path.progress_percentage = progress
                
                if completed == len(modules):
                    learning_path.is_completed = True
            
            db.commit()
            db.refresh(learning_path)
            
            logger.info(f"Learning path {path_id} progress updated")
            return learning_path
            
        except Exception as e:
            db.rollback()
            logger.error(f"Progress update error: {str(e)}")
            raise
