"""
Interview simulator service - business logic for mock interviews
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import json
from datetime import datetime

from app.models import Interview, InterviewStatus
from app.utils.external_apis import openai_client

logger = logging.getLogger(__name__)

class InterviewService:
    """Service for interview operations"""
    
    # System prompts for different roles
    INTERVIEW_SYSTEM_PROMPTS = {
        'software_engineer': """You are an experienced technical interviewer conducting a mock interview for a Software Engineer position.
        Your role is to:
        1. Ask challenging but fair questions based on the candidate's responses
        2. Probe deeper with follow-up questions to understand their thinking
        3. Maintain a professional yet friendly tone
        4. Take notes on their responses for final feedback
        5. Ask about 5-7 questions total
        
        Topics to cover: coding, system design, problem-solving, communication, teamwork.""",
        
        'product_manager': """You are an experienced PM interviewer. Ask about:
        1. Product thinking and strategy
        2. Case studies and real examples
        3. Data-driven decision making
        4. Cross-functional collaboration
        5. Communication skills""",
        
        'data_scientist': """You are an experienced Data Science interviewer. Focus on:
        1. Machine learning concepts
        2. Statistical knowledge
        3. Data analysis projects
        4. Programming skills (Python/R)
        5. Business impact of analyses"""
    }
    
    @staticmethod
    async def start_interview(
        db: Session,
        user_id: int,
        title: str,
        job_analysis_id: Optional[int] = None,
        duration_minutes: int = 30
    ) -> Interview:
        """Start a new mock interview"""
        try:
            interview = Interview(
                user_id=user_id,
                job_analysis_id=job_analysis_id,
                title=title,
                status=InterviewStatus.IN_PROGRESS,
                conversation_history=[],
                started_at=datetime.utcnow()
            )
            
            db.add(interview)
            db.commit()
            db.refresh(interview)
            
            # Send initial question
            initial_question = await InterviewService._get_initial_question(job_analysis_id)
            
            # Store in conversation history
            interview.conversation_history = [
                {
                    "role": "assistant",
                    "content": initial_question
                }
            ]
            db.commit()
            db.refresh(interview)
            
            logger.info(f"Interview started for user {user_id}: {interview.id}")
            return interview
            
        except Exception as e:
            db.rollback()
            logger.error(f"Interview start error: {str(e)}")
            raise
    
    @staticmethod
    async def _get_initial_question(job_analysis_id: Optional[int]) -> str:
        """Generate initial interview question"""
        try:
            prompt = """Generate an opening question for a tech interview.
            Make it friendly and open-ended to break the ice.
            Ask about their background or experience."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a friendly tech interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Initial question generation error: {str(e)}")
            return "Hi! Tell me about your background and experience with the technologies listed in the job description."
    
    @staticmethod
    async def process_interview_response(
        db: Session,
        interview_id: int,
        user_message: str
    ) -> str:
        """Process user response and generate next question"""
        try:
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            
            if not interview:
                raise ValueError("Interview not found")
            
            # Add user message to history
            if interview.conversation_history is None:
                interview.conversation_history = []
            
            interview.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate next question using LLM
            system_prompt = InterviewService.INTERVIEW_SYSTEM_PROMPTS['software_engineer']
            
            messages = [
                {"role": "system", "content": system_prompt}
            ] + interview.conversation_history
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            interview.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            db.commit()
            db.refresh(interview)
            
            logger.info(f"Interview {interview_id} processed")
            return ai_response
            
        except Exception as e:
            db.rollback()
            logger.error(f"Interview response processing error: {str(e)}")
            raise
    
    @staticmethod
    async def end_interview(
        db: Session,
        interview_id: int
    ) -> Interview:
        """End interview and generate feedback"""
        try:
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            
            if not interview:
                raise ValueError("Interview not found")
            
            # Generate feedback report
            feedback = await InterviewService._generate_feedback(interview.conversation_history)
            
            interview.status = InterviewStatus.COMPLETED
            interview.completed_at = datetime.utcnow()
            interview.feedback_report = feedback
            interview.overall_score = feedback.get('overall_score', 0)
            interview.strengths = feedback.get('strengths', [])
            interview.improvement_areas = feedback.get('improvement_areas', [])
            
            # Calculate duration
            if interview.started_at and interview.completed_at:
                duration = (interview.completed_at - interview.started_at).total_seconds()
                interview.duration_seconds = int(duration)
            
            db.commit()
            db.refresh(interview)
            
            logger.info(f"Interview {interview_id} ended with score {interview.overall_score}")
            return interview
            
        except Exception as e:
            db.rollback()
            logger.error(f"Interview end error: {str(e)}")
            raise
    
    @staticmethod
    async def _generate_feedback(conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate comprehensive feedback on interview"""
        try:
            prompt = f"""Analyze this interview conversation and provide detailed feedback:

            Conversation:
            {json.dumps(conversation_history, indent=2)}

            Provide JSON response with:
            {{
                "overall_score": overall score (0-100),
                "strengths": list of strengths demonstrated,
                "improvement_areas": list of areas for improvement,
                "technical_skills": score for technical skills (0-100),
                "communication": score for communication (0-100),
                "problem_solving": score for problem-solving (0-100),
                "detailed_feedback": paragraph of detailed feedback
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert tech interview evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            feedback = json.loads(content)
            return feedback
            
        except Exception as e:
            logger.error(f"Feedback generation error: {str(e)}")
            return {
                'overall_score': 0,
                'strengths': [],
                'improvement_areas': [],
                'technical_skills': 0,
                'communication': 0,
                'problem_solving': 0,
                'detailed_feedback': 'Unable to generate feedback'
            }
    
    @staticmethod
    def get_interview(db: Session, interview_id: int) -> Optional[Interview]:
        """Get interview by ID"""
        return db.query(Interview).filter(Interview.id == interview_id).first()
    
    @staticmethod
    def get_user_interviews(db: Session, user_id: int) -> List[Interview]:
        """Get all interviews for a user"""
        return db.query(Interview).filter(Interview.user_id == user_id).all()
    
    @staticmethod
    def get_user_completed_interviews(db: Session, user_id: int) -> List[Interview]:
        """Get completed interviews for a user"""
        return db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == InterviewStatus.COMPLETED
        ).all()
