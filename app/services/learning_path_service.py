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
        Create a personalized learning path based on job analysis
        """
        try:
            from app.services.job_service import JobService
            
            # Get job analysis
            job_analysis = JobService.get_job_analysis(db, job_analysis_id)
            if not job_analysis:
                raise ValueError("Job analysis not found")
            
            # Get skill gaps
            skill_gaps = await LearningPathService._get_prioritized_skill_gaps(
                job_analysis.skill_gaps
            )
            
            # Get learning resources
            resources = await LearningPathService._get_learning_resources(skill_gaps)
            
            # Create learning path
            learning_path = LearningPath(
                user_id=user_id,
                job_analysis_id=job_analysis_id,
                title=f"Learning Path for {job_analysis.job_description[:50]}",
                description="Personalized learning path based on job requirements",
                skill_gaps=[gap['skill'] for gap in skill_gaps],
                recommended_resources=resources.get('resources', []),
                video_playlists=resources.get('videos', []),
                estimated_hours=resources.get('estimated_hours', 0)
            )
            
            db.add(learning_path)
            db.commit()
            db.refresh(learning_path)
            
            # Create learning modules
            await LearningPathService._create_learning_modules(
                db, learning_path.id, resources
            )
            
            logger.info(f"Learning path created for user {user_id}")
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
    async def _get_learning_resources(skill_gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gather learning resources for skill gaps"""
        try:
            resources = []
            videos = []
            total_hours = 0
            
            # Extract skill names
            skills = [gap['skill'] for gap in skill_gaps[:5]]  # Top 5 skills
            
            # Get YouTube videos
            video_results = await YouTubeAPI.search_learning_videos(skills)
            videos.extend(video_results)
            
            # Add other resources
            resources.append({
                'type': 'documentation',
                'title': 'Official Documentation',
                'url': 'https://docs.example.com'
            })
            
            resources.append({
                'type': 'course',
                'title': 'Online Courses',
                'url': 'https://udemy.com'
            })
            
            resources.append({
                'type': 'project',
                'title': 'Build Projects to Practice',
                'url': 'https://github.com'
            })
            
            # Estimate hours (10 hours per gap)
            total_hours = len(skill_gaps) * 10
            
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
        resources: Dict[str, Any]
    ) -> None:
        """Create learning modules for a learning path"""
        try:
            # Create module for each video
            for idx, video in enumerate(resources.get('videos', [])[:10]):
                module = LearningModule(
                    learning_path_id=learning_path_id,
                    title=video.get('title', f'Video {idx+1}'),
                    description=f"Watch this tutorial to learn {video.get('channel', 'the topic')}",
                    resource_type='video',
                    resource_url=video.get('url', ''),
                    estimated_hours=1.5
                )
                db.add(module)
            
            # Create modules for other resources
            for resource in resources.get('resources', []):
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
