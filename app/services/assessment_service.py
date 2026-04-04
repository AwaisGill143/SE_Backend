"""
Assessment service - business logic for assessments
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import json

from app.models import Assessment, AssessmentType
from app.utils.external_apis import Judge0API, openai_client

logger = logging.getLogger(__name__)

class AssessmentService:
    """Service for assessment operations"""
    
    # Language IDs for Judge0
    LANGUAGE_IDS = {
        'python': 71,
        'javascript': 63,
        'java': 62,
        'cpp': 54,
        'csharp': 51,
        'go': 60
    }
    
    @staticmethod
    async def create_assessment(
        db: Session,
        user_id: int,
        assessment_type: str,
        job_analysis_id: Optional[int] = None,
        difficulty: str = 'medium'
    ) -> Assessment:
        """Create a new assessment based on type"""
        try:
            if assessment_type == 'mcq':
                questions = await AssessmentService._generate_mcq(job_analysis_id, difficulty)
            elif assessment_type == 'coding':
                questions = await AssessmentService._generate_coding_challenge(difficulty)
            elif assessment_type == 'system_design':
                questions = await AssessmentService._generate_system_design(difficulty)
            elif assessment_type == 'behavioral':
                questions = await AssessmentService._generate_behavioral(difficulty)
            else:
                raise ValueError(f"Unknown assessment type: {assessment_type}")
            
            # Create assessment record
            assessment = Assessment(
                user_id=user_id,
                job_analysis_id=job_analysis_id,
                title=f"{assessment_type.upper()} Assessment",
                assessment_type=assessment_type,
                questions=questions
            )
            
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            
            logger.info(f"Assessment created for user {user_id}: {assessment_type}")
            return assessment
            
        except Exception as e:
            db.rollback()
            logger.error(f"Assessment creation error: {str(e)}")
            raise
    
    @staticmethod
    async def _generate_mcq(job_analysis_id: Optional[int], difficulty: str) -> List[Dict[str, Any]]:
        """Generate MCQ questions"""
        try:
            prompt = f"""Generate 5 multiple choice questions with difficulty level: {difficulty}.
            Each question should have:
            - question: The MCQ question
            - options: List of 4 options
            - correct_answer: Index of correct answer (0-3)
            - explanation: Explanation of correct answer
            
            Return as JSON list."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            return questions
            
        except Exception as e:
            logger.error(f"MCQ generation error: {str(e)}")
            return []
    
    @staticmethod
    async def _generate_coding_challenge(difficulty: str) -> List[Dict[str, Any]]:
        """Generate coding challenges"""
        try:
            challenges = [
                {
                    'title': 'Two Sum Problem',
                    'problem_statement': 'Given an array of integers, find two numbers that add up to a target.',
                    'difficulty': difficulty,
                    'test_cases': [
                        {'input': '[2, 7, 11, 15] 9', 'expected_output': '[0, 1]'},
                        {'input': '[3, 2, 4] 6', 'expected_output': '[1, 2]'}
                    ],
                    'boilerplate_code': 'def twoSum(nums, target):\n    pass',
                    'time_limit_seconds': 60
                },
                {
                    'title': 'Reverse String',
                    'problem_statement': 'Reverse a string without using built-in reverse functions.',
                    'difficulty': difficulty,
                    'test_cases': [
                        {'input': 'hello', 'expected_output': 'olleh'},
                        {'input': 'world', 'expected_output': 'dlrow'}
                    ],
                    'boilerplate_code': 'def reverseString(s):\n    pass',
                    'time_limit_seconds': 30
                }
            ]
            
            return challenges
            
        except Exception as e:
            logger.error(f"Coding challenge generation error: {str(e)}")
            return []
    
    @staticmethod
    async def _generate_system_design(difficulty: str) -> List[Dict[str, Any]]:
        """Generate system design questions"""
        try:
            questions = [
                {
                    'question': 'Design a URL shortening service like Bitly',
                    'requirements': [
                        'Handle millions of URL requests',
                        'Store mapping between short and long URLs',
                        'Provide analytics on URL clicks',
                        'Support custom short names'
                    ],
                    'difficulty': difficulty,
                    'estimated_time_minutes': 45
                },
                {
                    'question': 'Design a distributed cache system',
                    'requirements': [
                        'Store key-value pairs',
                        'Support expiration',
                        'Distributed across multiple nodes',
                        'Handle cache eviction'
                    ],
                    'difficulty': difficulty,
                    'estimated_time_minutes': 45
                }
            ]
            
            return questions
            
        except Exception as e:
            logger.error(f"System design generation error: {str(e)}")
            return []
    
    @staticmethod
    async def _generate_behavioral(difficulty: str) -> List[Dict[str, Any]]:
        """Generate behavioral questions"""
        try:
            questions = [
                {
                    'question': 'Tell me about a time you overcame a technical challenge.',
                    'tags': ['problem-solving', 'resilience'],
                    'difficulty': difficulty
                },
                {
                    'question': 'Describe your experience working with a difficult team member.',
                    'tags': ['teamwork', 'communication'],
                    'difficulty': difficulty
                },
                {
                    'question': 'How do you handle tight deadlines?',
                    'tags': ['time-management', 'pressure'],
                    'difficulty': difficulty
                },
                {
                    'question': 'Tell me about your approach to learning new technologies.',
                    'tags': ['learning', 'growth-mindset'],
                    'difficulty': difficulty
                }
            ]
            
            return questions
            
        except Exception as e:
            logger.error(f"Behavioral question generation error: {str(e)}")
            return []
    
    @staticmethod
    async def submit_assessment(
        db: Session,
        assessment_id: int,
        user_answers: List[Any],
        code: Optional[str] = None
    ) -> Assessment:
        """Submit assessment answers and evaluate"""
        try:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            
            if not assessment:
                raise ValueError("Assessment not found")
            
            # Evaluate based on type
            if assessment.assessment_type == 'coding':
                score = await AssessmentService._evaluate_coding(code, assessment.questions)
            elif assessment.assessment_type == 'mcq':
                score = AssessmentService._evaluate_mcq(user_answers, assessment.questions)
            elif assessment.assessment_type == 'behavioral':
                score = await AssessmentService._evaluate_behavioral(user_answers, assessment.questions)
            else:
                score = 0
            
            # Update assessment
            assessment.user_answers = user_answers
            assessment.score = score
            assessment.completed_at = __import__('datetime').datetime.utcnow()
            
            db.commit()
            db.refresh(assessment)
            
            logger.info(f"Assessment {assessment_id} submitted with score {score}")
            return assessment
            
        except Exception as e:
            db.rollback()
            logger.error(f"Assessment submission error: {str(e)}")
            raise
    
    @staticmethod
    def _evaluate_mcq(user_answers: List[int], questions: List[Dict[str, Any]]) -> float:
        """Evaluate MCQ answers"""
        correct = 0
        for user_answer, question in zip(user_answers, questions):
            if user_answer == question.get('correct_answer'):
                correct += 1
        
        return (correct / len(questions) * 100) if questions else 0
    
    @staticmethod
    async def _evaluate_coding(code: str, questions: List[Dict[str, Any]]) -> float:
        """Evaluate coding solution"""
        try:
            # Use Judge0 to evaluate
            test_cases = questions[0].get('test_cases', [])
            language_id = AssessmentService.LANGUAGE_IDS.get('python', 71)
            
            result = await Judge0API.evaluate_code_solution(code, test_cases, language_id)
            
            success_rate = result.get('success_rate', 0)
            return success_rate * 100
            
        except Exception as e:
            logger.error(f"Coding evaluation error: {str(e)}")
            return 0
    
    @staticmethod
    async def _evaluate_behavioral(user_answers: List[str], questions: List[Dict[str, Any]]) -> float:
        """Evaluate behavioral answers using AI"""
        try:
            prompt = f"""Evaluate these behavioral interview answers (scale 0-100):
            
            Questions: {json.dumps(questions)}
            Answers: {user_answers}
            
            Consider: clarity, confidence, relevance, examples, leadership qualities.
            Return only a number between 0-100."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            score = float(response.choices[0].message.content.strip())
            return min(max(score, 0), 100)
            
        except Exception as e:
            logger.error(f"Behavioral evaluation error: {str(e)}")
            return 0
    
    @staticmethod
    def get_assessment(db: Session, assessment_id: int) -> Optional[Assessment]:
        """Get assessment by ID"""
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    @staticmethod
    def get_user_assessments(db: Session, user_id: int) -> List[Assessment]:
        """Get all assessments for a user"""
        return db.query(Assessment).filter(Assessment.user_id == user_id).all()
