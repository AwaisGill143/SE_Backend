"""
CareerLaunch AI Backend - Enhanced Version with OpenAI Integration
Fully functional with real AI features
"""
from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import logging
import json
from typing import Optional, List
import os
from datetime import datetime
import hashlib
import secrets

# Groq integration
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Configuration ====================
class Settings:
    ENVIRONMENT = "development"
    DEBUG = True
    LOG_LEVEL = "INFO"
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "https://dream-site-realized.vercel.app"
    ]
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# ==================== Schemas ====================
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class JobAnalysisRequest(BaseModel):
    job_description: str
    job_url: Optional[str] = None

class JobAnalysisResponse(BaseModel):
    id: int
    job_title: Optional[str]
    company: Optional[str]
    required_skills: List[str]
    technologies: List[str]
    soft_skills: List[str]
    experience_required: str
    readiness_score: float
    seniority_level: Optional[str] = "Mid-Level"
    role_type: Optional[str] = "Full-Stack"
    skill_gaps: Optional[List[dict]] = []

class AssessmentCreateRequest(BaseModel):
    title: str
    assessment_type: str = "mcq"
    skill_focus: Optional[str] = None
    skills: Optional[List[str]] = None
    num_questions: Optional[int] = 10

class AssessmentSubmitRequest(BaseModel):
    answers: Optional[dict] = {}

class InterviewStartRequest(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None

class InterviewResponseRequest(BaseModel):
    message: str

class AssessmentAnswerRequest(BaseModel):
    question_id: int
    answer: str

# ==================== Initialize FastAPI ====================
app = FastAPI(
    title="CareerLaunch AI Backend",
    description="AI-powered platform for job interview preparation",
    version="2.0.0 (Enhanced)",
)

settings = Settings()

# Initialize Groq client
groq_client = None
if HAS_GROQ and settings.GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        logger.info("✅ Groq client initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize Groq client: {str(e)}")
        logger.info("Using mock AI responses as fallback")
else:
    if not HAS_GROQ:
        logger.warning("⚠️ Groq library not installed. Using mock responses.")
    else:
        logger.warning("⚠️ GROQ_API_KEY environment variable not set. Using mock responses.")
        logger.info("To enable real AI features:")
        logger.info("  1. Get API key from https://console.groq.com/keys")
        logger.info("  2. Set: $env:GROQ_API_KEY='gsk-...'")
        logger.info("  3. Restart backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== In-Memory Storage ====================
demo_users = {
    "ayesha@example.com": {
        "id": 1,
        "email": "ayesha@example.com",
        "username": "ayesha",
        "full_name": "Ayesha Khan",
        "password": "password123",  # In production, use bcrypt
        "access_token": "demo-token-ayesha@example.com",
        "refresh_token": "demo-refresh-ayesha@example.com",
        "skills": ["React.js", "TypeScript", "Node.js", "REST APIs", "HTML/CSS", "JavaScript", "Git"],
    }
}

demo_analyses = {}
demo_assessments = {}
demo_interviews = {}
demo_counter = {"analyses": 0, "assessments": 0, "interviews": 0}
user_sessions = {}

# ==================== Helper Functions ====================
def get_user_from_token(authorization: Optional[str] = Header(None)):
    """Extract user from Bearer token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = parts[1]
    for email, user in demo_users.items():
        if user["access_token"] == token:
            return email
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token"
    )

def call_openai(messages: list, model: str = "llama-3.1-8b-instant") -> str:
    """Call Groq API with fallback to mock responses"""
    if not groq_client or not settings.GROQ_API_KEY:
        # No API key configured - return mock response
        logger.info("Using mock AI response (Groq API key not configured)")
        
        # Provide context-aware mock responses
        messages_text = str(messages).lower()
        if "analyze" in messages_text or "job" in messages_text:
            return json.dumps({
                "job_title": "Senior Backend Engineer",
                "company": "Tech Company",
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "System Design", "Docker"],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "Redis"],
                "soft_skills": ["Communication", "Problem-solving", "Leadership", "Teamwork"],
                "experience_required": "5+ years of backend development"
            })
        elif "question" in messages_text or "assessment" in messages_text:
            return json.dumps({
                "questions": [
                    {
                        "id": 1,
                        "question": "What is the purpose of a REST API?",
                        "options": ["Database management", "Architectural style for web services", "Programming language", "Cloud storage"],
                        "correct_answer": 1
                    },
                    {
                        "id": 2,
                        "question": "Which HTTP method is used to retrieve data?",
                        "options": ["POST", "GET", "DELETE", "PUT"],
                        "correct_answer": 1
                    }
                ]
            })
        
        return "Mock AI response - Configure OPENAI_API_KEY for real responses"
    
    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        # Fallback to mock response on error
        logger.info("Falling back to mock response due to API error")
        if "job" in str(messages).lower():
            return json.dumps({
                "job_title": "Backend Engineer",
                "company": "Tech Company",
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs"],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "soft_skills": ["Communication", "Problem-solving"],
                "experience_required": "5+ years development"
            })
        return f"AI processing error (fallback response). Error: {str(e)}"

# ==================== Root Endpoints ====================
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CareerLaunch AI Backend",
        "version": "2.0.0 (Enhanced)",
        "environment": settings.ENVIRONMENT,
        "groq_configured": groq_client is not None,
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CareerLaunch AI Backend",
        "groq_available": groq_client is not None
    }

# ==================== User Endpoints ====================
@app.post("/api/v1/users/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    if user_data.email in demo_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    access_token = f"token-{secrets.token_hex(16)}"
    refresh_token = f"refresh-{secrets.token_hex(16)}"
    
    demo_users[user_data.email] = {
        "id": len(demo_users) + 1,
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "password": user_data.password,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    
    logger.info(f"User registered: {user_data.email}")
    return {
        "id": demo_users[user_data.email]["id"],
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "message": "User registered successfully"
    }

@app.post("/api/v1/users/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    print(credentials)
    """Login and get JWT token"""
    if credentials.email not in demo_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = demo_users[credentials.email]
    if user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    logger.info(f"User logged in: {credentials.email}")
    return {
        "access_token": user["access_token"],
        "refresh_token": user["refresh_token"],
        "token_type": "bearer"
    }

@app.post("/api/v1/users/refresh")
async def refresh_token(authorization: Optional[str] = Header(None)):
    """Refresh access token"""
    email = get_user_from_token(authorization)
    user = demo_users[email]
    
    # Generate new token
    new_access_token = f"token-{secrets.token_hex(16)}"
    user["access_token"] = new_access_token
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me", response_model=dict)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user profile"""
    email = get_user_from_token(authorization)
    user = demo_users[email]
    
    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user["full_name"],
        "is_active": True,
    }

# ==================== Job Parser Endpoints ====================
@app.post("/api/v1/jobs/analyze", response_model=JobAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_job(job_data: JobAnalysisRequest, authorization: Optional[str] = Header(None)):
    """Analyze a job description with AI"""
    email = get_user_from_token(authorization)
    demo_counter["analyses"] += 1
    
    # Call OpenAI to analyze job
    analysis_prompt = f"""
    Analyze this job description and provide a structured response in JSON format:
    
    Job Description:
    {job_data.job_description}
    
    Return a JSON response with these fields:
    - job_title: The job title (string)
    - company: The company name if mentioned (string)
    - required_skills: Array of 5-8 required technical skills
    - technologies: Array of 5-10 technologies/frameworks needed
    - soft_skills: Array of 3-5 soft skills needed
    - experience_required: Brief string about experience requirements
    - seniority_level: Detect seniority level from JD (Junior, Mid-Level, Senior, or Lead)
    - role_type: Detect role type (Frontend, Backend, Full-Stack, DevOps, QA, Data Engineer, etc.)
    
    Return ONLY valid JSON, no markdown or extra text.
    """
    logger.info(f"Analyzing job for {email}: {job_data.job_description[:20]}...")
    
    try:
        ai_response = call_openai([{"role": "user", "content": analysis_prompt}])
        logger.info(f"AI response for job analysis: {ai_response[:200]}...")
        
        # Strip markdown code fences if present
        cleaned_response = ai_response.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.split("\n", 1)[-1]
            cleaned_response = cleaned_response.rsplit("```", 1)[0].strip()

        # Try to parse JSON response
        try:
            analysis_data = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # If response isn't pure JSON, use defaults
            logger.warning("Could not parse AI response as JSON, using defaults")
            analysis_data = {
                "job_title": "Backend Engineer",
                "company": "Unknown",
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "System Design"],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "soft_skills": ["Communication", "Problem-solving", "Leadership"],
                "experience_required": "5+ years of backend development",
                "seniority_level": "Mid-Level",
                "role_type": "Full-Stack"
            }
    except Exception as e:
        logger.error(f"Error calling AI: {str(e)}")
        # Use safe defaults
        analysis_data = {
            "job_title": "Backend Engineer",
            "company": "Unknown",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "System Design"],
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "soft_skills": ["Communication", "Problem-solving", "Leadership"],
            "experience_required": "5+ years of backend development",
            "seniority_level": "Senior",
            "role_type": "Backend"
        }
    
    # Calculate readiness score (mock - in production, compare with user skills)
    readiness_score = 65.0
    
    # Get user's current skills
    user = demo_users.get(email, {})
    user_skills = set(user.get("skills", []))
    required_skills_set = set(analysis_data.get("required_skills", []))
    
    # Calculate skill gaps
    skill_gaps = []
    all_skills = required_skills_set.union(user_skills)
    for skill in sorted(all_skills):
        if skill in user_skills:
            level = "Strong"
            pct = 88
            color = "bg-green-500"
            text_color = "text-green-600"
        elif skill in required_skills_set:
            level = "Gap"
            pct = 10
            color = "bg-red-500"
            text_color = "text-red-600"
        else:
            level = "Good"
            pct = 72
            color = "bg-blue-500"
            text_color = "text-blue-600"
        
        skill_gaps.append({
            "name": skill,
            "level": level,
            "pct": pct,
            "color": color,
            "textColor": text_color
        })
    
    analysis = {
        "id": demo_counter["analyses"],
        "job_title": analysis_data.get("job_title", ""),
        "company": analysis_data.get("company", ""),
        "required_skills": analysis_data.get("required_skills", []),
        "technologies": analysis_data.get("technologies", []),
        "soft_skills": analysis_data.get("soft_skills", []),
        "experience_required": analysis_data.get("experience_required", ""),
        "readiness_score": readiness_score,
        "seniority_level": analysis_data.get("seniority_level", "Mid-Level"),
        "role_type": analysis_data.get("role_type", "Full-Stack"),
        "skill_gaps": skill_gaps
    }
    
    demo_analyses[demo_counter["analyses"]] = analysis
    logger.info(f"Job analyzed by {email}: {demo_counter['analyses']}")
    print(analysis)
    return analysis

@app.get("/api/v1/jobs/my-analyses")
async def get_my_analyses(authorization: Optional[str] = Header(None)):
    """Get user's job analyses"""
    email = get_user_from_token(authorization)
    return {
        "data": list(demo_analyses.values())
    }

# ==================== Assessment Endpoints ====================
@app.post("/api/v1/assessments", status_code=status.HTTP_201_CREATED)
async def create_assessment(data: AssessmentCreateRequest, authorization: Optional[str] = Header(None)):
    """Create an assessment with AI-generated questions"""
    email = get_user_from_token(authorization)
    demo_counter["assessments"] += 1
    
    # Generate assessment questions with AI
    skills_text = ", ".join(data.skills) if data.skills else (data.skill_focus or "general backend development")
    num_q = data.num_questions or 10
    prompt = f"""Generate exactly {num_q} multiple-choice questions to test knowledge of: {skills_text}.

Return ONLY a valid JSON object with this exact structure:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Clear question text?",
            "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
            "correct_answer": 0
        }}
    ]
}}

Rules:
- correct_answer is a 0-based index (0=first option, 1=second, 2=third, 3=fourth)
- Generate exactly {num_q} questions
- Mix easy, medium, and hard difficulty
- Cover different aspects of {skills_text}
- Return ONLY valid JSON, no markdown fences"""
    
    try:
        ai_response = call_openai([{"role": "user", "content": prompt}])
        cleaned = ai_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0].strip()
        questions_data = json.loads(cleaned)
        questions = questions_data.get("questions", [])
    except Exception as e:
        logger.warning(f"Failed to generate assessment: {str(e)}")
        questions = [
            {
                "id": 1,
                "question": "What is the purpose of a REST API?",
                "options": ["Database management", "Architectural style for web services", "Programming language", "Cloud storage"],
                "correct_answer": 1
            },
            {
                "id": 2,
                "question": "Which of the following is NOT a common HTTP method?",
                "options": ["GET", "POST", "DELETE", "RECEIVE"],
                "correct_answer": 3
            }
        ]
    
    assessment = {
        "id": demo_counter["assessments"],
        "title": data.title,
        "assessment_type": data.assessment_type,
        "skill_focus": data.skill_focus,
        "questions": questions,
        "score": None,
        "feedback": None,
        "user_answers": {}
    }
    
    demo_assessments[demo_counter["assessments"]] = assessment
    logger.info(f"Assessment created by {email}: {demo_counter['assessments']}")
    
    return assessment

@app.get("/api/v1/assessments")
async def get_my_assessments(authorization: Optional[str] = Header(None)):
    """Get user's assessments"""
    email = get_user_from_token(authorization)
    return {
        "data": list(demo_assessments.values())
    }

@app.post("/api/v1/assessments/{assessment_id}/answers/{question_id}")
async def submit_assessment_answer(
    assessment_id: int,
    question_id: int,
    data: AssessmentAnswerRequest,
    authorization: Optional[str] = Header(None)
):
    """Submit answer to assessment question"""
    email = get_user_from_token(authorization)
    
    if assessment_id not in demo_assessments:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = demo_assessments[assessment_id]
    assessment["user_answers"][str(question_id)] = data.answer
    
    return {
        "assessment_id": assessment_id,
        "question_id": question_id,
        "answer": data.answer,
        "status": "recorded"
    }

@app.post("/api/v1/assessments/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: int,
    data: Optional[AssessmentSubmitRequest] = None,
    authorization: Optional[str] = Header(None)
):
    """Submit assessment and get score"""
    email = get_user_from_token(authorization)
    
    if assessment_id not in demo_assessments:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = demo_assessments[assessment_id]
    
    # Merge bulk answers from body into stored answers
    if data and data.answers:
        for qid, answer in data.answers.items():
            assessment["user_answers"][str(qid)] = answer
    
    # Calculate score and build per-question results
    correct = 0
    question_results = []
    for q in assessment["questions"]:
        raw = assessment["user_answers"].get(str(q["id"]))
        user_answer = int(raw) if raw is not None else None
        is_correct = user_answer is not None and user_answer == q["correct_answer"]
        if is_correct:
            correct += 1
        question_results.append({
            **q,
            "user_answer": user_answer,
            "is_correct": is_correct,
        })
    
    score = (correct / len(assessment["questions"])) * 100 if assessment["questions"] else 0
    
    # Get AI feedback
    feedback_prompt = f"Give brief 2-sentence feedback for someone who scored {score:.0f}% on an assessment about {assessment.get('skill_focus', 'general topics')}. Be encouraging and mention what to focus on."
    
    try:
        feedback = call_openai([{"role": "user", "content": feedback_prompt}])
    except:
        feedback = f"Great effort! You scored {score:.0f}%. Keep practicing to improve your weak areas."
    
    assessment["score"] = score
    assessment["feedback"] = feedback
    
    return {
        "id": assessment_id,
        "score": score,
        "feedback": feedback,
        "correct_count": correct,
        "total": len(assessment["questions"]),
        "questions": question_results,
    }

# ==================== Interview Endpoints ====================
@app.post("/api/v1/interviews", status_code=status.HTTP_201_CREATED)
async def start_interview(data: InterviewStartRequest, authorization: Optional[str] = Header(None)):
    """Start an AI interview"""
    email = get_user_from_token(authorization)
    demo_counter["interviews"] += 1
    
    topic = data.topic or "general software engineering"
    
    # Get initial AI prompt
    initial_prompt = f"You are an experienced technical interviewer. Start a mock interview about {topic}. Ask a thoughtful opening question to assess the candidate's background and experience. Keep response brief (2-3 sentences)."
    
    try:
        initial_response = call_openai([{"role": "user", "content": initial_prompt}])
    except:
        initial_response = f"Hi! I'm your interviewer today. Let's discuss {topic}. Could you please tell me about your background and experience in this area?"
    
    interview = {
        "id": demo_counter["interviews"],
        "title": data.title or f"Interview - {topic}",
        "topic": topic,
        "status": "in_progress",
        "conversation_history": [
            {"role": "assistant", "content": initial_response}
        ],
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "duration_seconds": 0
    }
    
    demo_interviews[demo_counter["interviews"]] = interview
    logger.info(f"Interview started by {email}: {demo_counter['interviews']}")
    
    return interview

@app.post("/api/v1/interviews/{interview_id}/response")
async def respond_interview(
    interview_id: int,
    data: InterviewResponseRequest,
    authorization: Optional[str] = Header(None)
):
    print("="*70)
    """Respond to interview question"""
    email = get_user_from_token(authorization)
    
    if interview_id not in demo_interviews:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = demo_interviews[interview_id]
    
    # Add user message to history
    interview["conversation_history"].append({
        "role": "user",
        "content": data.message
    })
    
    # Get AI response
    system_prompt = f"You are an experienced technical interviewer. Previous conversation:\n"
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(interview["conversation_history"])
    messages.append({"role": "user", "content": "Provide a follow-up question or feedback based on the candidate's response. Keep it brief (2-3 sentences)."})
    
    try:
        ai_response = call_openai(messages)
    except:
        ai_response = "That's interesting! Can you tell me more about your experience and how it relates to this role?"
    
    # Add AI response to history
    interview["conversation_history"].append({
        "role": "assistant",
        "content": ai_response
    })
    
    return {
        "interview_id": interview_id,
        "user_message": data.message,
        "ai_response": ai_response
    }

@app.post("/api/v1/interviews/{interview_id}/end")
async def end_interview(interview_id: int, authorization: Optional[str] = Header(None)):
    """End interview and get feedback"""
    email = get_user_from_token(authorization)
    
    if interview_id not in demo_interviews:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = demo_interviews[interview_id]
    interview["status"] = "completed"
    interview["completed_at"] = datetime.now().isoformat()
    
    # Get AI feedback
    feedback_prompt = f"Based on this interview about {interview['topic']}, provide feedback. Return JSON with: overall_score (0-100), strengths (array), improvement_areas (array), detailed_feedback (string)."
    messages = [{"role": "user", "content": feedback_prompt}]
    messages.extend(interview["conversation_history"])
    
    try:
        feedback_response = call_openai(messages)
        cleaned = feedback_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0].strip()
        feedback_data = json.loads(cleaned)
    except:
        feedback_data = {
            "overall_score": 75,
            "strengths": ["Clear communication", "Technical knowledge"],
            "improvement_areas": ["System design depth", "Following up on requirements"],
            "detailed_feedback": "Good performance overall. Work on questioning and design thinking."
        }
    
    return {
        "id": interview_id,
        "overall_score": feedback_data.get("overall_score", 75),
        "strengths": feedback_data.get("strengths", []),
        "improvement_areas": feedback_data.get("improvement_areas", []),
        "detailed_feedback": feedback_data.get("detailed_feedback", ""),
        "duration_seconds": 0,
        "completed_at": interview["completed_at"]
    }

@app.get("/api/v1/interviews")
async def get_my_interviews(authorization: Optional[str] = Header(None)):
    """Get user's interviews"""
    email = get_user_from_token(authorization)
    return {
        "data": list(demo_interviews.values())
    }

# ==================== Learning Paths Endpoints ====================
@app.post("/api/v1/learning-paths", status_code=status.HTTP_201_CREATED)
async def create_learning_path(data: dict, authorization: Optional[str] = Header(None)):
    """Create a learning path based on job analysis and skill gaps"""
    email = get_user_from_token(authorization)

    # Extract job details and skill gaps
    job_title = data.get("job_title", "Target Role")
    skill_gaps = data.get("skill_gaps", [])
    required_skills = data.get("required_skills", [])

    # Priority: gap skills first (up to 3), then fill from required skills
    gap_skills = [gap["name"] for gap in skill_gaps if gap.get("level") == "Gap"][:3]
    extra_skills = [s for s in required_skills if s not in gap_skills][:2]
    all_target_skills = gap_skills + extra_skills

    # Ask AI to generate real resources with YouTube search URLs
    skills_list = ", ".join(all_target_skills) if all_target_skills else job_title
    ai_prompt = f"""
You are a learning path curator. For a candidate preparing for a "{job_title}" role, generate curated learning resources for these skills: {skills_list}.

For EACH skill return 2 resources:
1. A YouTube tutorial (use a real YouTube search URL: https://www.youtube.com/results?search_query=SKILL+tutorial)
2. An official documentation or a well-known free resource URL (e.g. docs.python.org, react.dev, typescriptlang.org, etc.)

Return ONLY a valid JSON array with this exact structure (no markdown, no extra text):
[
  {{
    "skill": "Skill Name",
    "title": "Descriptive resource title",
    "url": "https://...",
    "type": "video",
    "hours": 3,
    "priority": "high"
  }},
  {{
    "skill": "Skill Name",
    "title": "Official documentation title",
    "url": "https://...",
    "type": "documentation",
    "hours": 5,
    "priority": "medium"
  }}
]

Rules:
- For YouTube resources use https://www.youtube.com/results?search_query=SKILL+TOPIC (replace spaces with +)
- For documentation use the real official docs URL
- type must be one of: video, documentation, course, book
- hours should be realistic (video: 2-5h, docs: 4-10h, course: 8-20h)
- priority: "high" for gap skills, "medium" for recommended skills
Return ONLY the JSON array.
"""

    learning_modules = []
    estimated_total_hours = 0
    module_id = 1

    try:
        ai_response = call_openai([{"role": "user", "content": ai_prompt}])

        # Strip markdown fences
        cleaned = ai_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        resources = json.loads(cleaned)
        if not isinstance(resources, list):
            raise ValueError("Expected a JSON array")

        for resource in resources:
            skill = resource.get("skill", "General")
            hours = int(resource.get("hours", 5))
            estimated_total_hours += hours
            learning_modules.append({
                "id": module_id,
                "title": resource.get("title", f"{skill} Resource"),
                "skill": skill,
                "resource_type": resource.get("type", "video"),
                "url": resource.get("url", f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial"),
                "estimated_hours": hours,
                "progress": 0,
                "is_completed": False,
                "priority": resource.get("priority", "medium"),
            })
            module_id += 1

    except Exception as e:
        logger.warning(f"AI resource generation failed: {e}. Using YouTube search fallback.")
        # Fallback: generate YouTube search URLs programmatically
        for i, skill in enumerate(all_target_skills):
            query = skill.replace(" ", "+")
            priority = "high" if skill in gap_skills else "medium"
            estimated_total_hours += 3
            learning_modules.append({
                "id": module_id,
                "title": f"{skill} Full Tutorial for Beginners",
                "skill": skill,
                "resource_type": "video",
                "url": f"https://www.youtube.com/results?search_query={query}+tutorial+full+course",
                "estimated_hours": 3,
                "progress": 0,
                "is_completed": False,
                "priority": priority,
            })
            module_id += 1
            estimated_total_hours += 5
            learning_modules.append({
                "id": module_id,
                "title": f"{skill} — Interview Prep & Best Practices",
                "skill": skill,
                "resource_type": "video",
                "url": f"https://www.youtube.com/results?search_query={query}+interview+preparation",
                "estimated_hours": 5,
                "progress": 0,
                "is_completed": False,
                "priority": priority,
            })
            module_id += 1

    if "learning_paths" not in demo_counter:
        demo_counter["learning_paths"] = 0
    demo_counter["learning_paths"] += 1

    return {
        "id": demo_counter["learning_paths"],
        "title": f"{job_title} Preparation Path",
        "description": f"Personalized learning path to master skills for {job_title} role",
        "job_title": job_title,
        "skill_gaps": gap_skills,
        "total_skills_gap": len(gap_skills),
        "estimated_hours": estimated_total_hours,
        "progress_percentage": 0,
        "is_completed": False,
        "learning_modules": learning_modules,
        "created_at": datetime.now().isoformat(),
    }

@app.get("/api/v1/learning-paths")
async def get_my_learning_paths(authorization: Optional[str] = Header(None)):
    """Get user's learning paths"""
    email = get_user_from_token(authorization)
    return {
        "data": [
            {
                "id": 1,
                "title": "Backend Development Path",
                "description": "Personalized learning path to master backend skills",
                "skill_gaps": ["Docker", "Kubernetes", "System Design"],
                "total_skills_gap": 3,
                "estimated_hours": 50,
                "progress_percentage": 30,
                "is_completed": False,
                "learning_modules": [
                    {
                        "id": 1,
                        "title": "Docker Official Documentation",
                        "skill": "Docker",
                        "resource_type": "documentation",
                        "url": "https://docker.com/docs",
                        "estimated_hours": 5,
                        "progress": 100,
                        "is_completed": True,
                        "priority": "high"
                    },
                    {
                        "id": 2,
                        "title": "Docker & Kubernetes Crash Course",
                        "skill": "Docker",
                        "resource_type": "video",
                        "url": "https://youtube.com",
                        "estimated_hours": 3,
                        "progress": 0,
                        "is_completed": False,
                        "priority": "high"
                    }
                ]
            }
        ]
    }

# ==================== Analytics Endpoints ====================
@app.get("/api/v1/analytics")
async def get_analytics(authorization: Optional[str] = Header(None)):
    """Get user analytics"""
    email = get_user_from_token(authorization)
    
    return {
        "total_assessments": len(demo_assessments),
        "completed_assessments": sum(1 for a in demo_assessments.values() if a.get("score") is not None),
        "avg_assessment_score": sum(a.get("score", 0) for a in demo_assessments.values()) / max(1, len(demo_assessments)),
        "total_interviews": len(demo_interviews),
        "completed_interviews": sum(1 for i in demo_interviews.values() if i["status"] == "completed"),
        "avg_interview_score": 75.0,
        "avg_readiness": 65.0,
        "total_jobs_analyzed": len(demo_analyses)
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 CareerLaunch AI Backend - Starting...")
    print("="*70)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Groq Configured: {groq_client is not None}")
    print(f"\n📚 API Documentation: http://localhost:8000/docs")
    print(f"🏥 Health Check: http://localhost:8000/api/v1/health")
    print(f"\n✅ Test Credentials:")
    print(f"   Email: ayesha@example.com")
    print(f"   Password: password123")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
