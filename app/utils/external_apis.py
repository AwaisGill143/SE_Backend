"""
External API integrations
"""
import httpx
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# OpenAI Client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

class JobParserAPI:
    """Job description parsing using OpenAI GPT-4"""
    
    @staticmethod
    async def analyze_job_description(job_description: str) -> Dict[str, Any]:
        """
        Analyze job description and extract skills, technologies, and requirements
        """
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert job analyst. Analyze job descriptions and extract:
                        1. Required skills (technical and non-technical)
                        2. Technology stack
                        3. Soft skills
                        4. Experience requirements
                        
                        Respond in JSON format with keys: required_skills, technologies, soft_skills, experience_required"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this job description:\n\n{job_description}"
                    }
                ],
                temperature=0.3,
            )
            
            # Parse response
            content = response.choices[0].message.content
            import json
            analysis = json.loads(content)
            return analysis
            
        except Exception as e:
            logger.error(f"Job parsing error: {str(e)}")
            raise

class YouTubeAPI:
    """YouTube API integration for learning resources"""
    
    @staticmethod
    async def search_learning_videos(skills: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search YouTube for learning videos based on skills
        """
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
            results = []
            
            for skill in skills:
                request = youtube.search().list(
                    q=f"{skill} tutorial",
                    part='snippet',
                    maxResults=max_results,
                    type='video',
                    order='relevance'
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    results.append({
                        'title': item['snippet']['title'],
                        'video_id': item['id']['videoId'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'thumbnail': item['snippet']['thumbnails']['default']['url'],
                        'channel': item['snippet']['channelTitle']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube API error: {str(e)}")
            return []

class Judge0API:
    """Judge0 API for code execution and evaluation"""
    
    @staticmethod
    async def execute_code(code: str, language_id: int, stdin: str = "") -> Dict[str, Any]:
        """
        Execute code using Judge0 API
        language_id: 62 = Python, 54 = C++, 63 = JavaScript, etc.
        """
        try:
            headers = {
                "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
            }
            
            payload = {
                "source_code": code,
                "language_id": language_id,
                "stdin": stdin
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.JUDGE0_API_URL}/submissions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    submission = response.json()
                    token = submission['token']
                    
                    # Poll for result
                    import time
                    for _ in range(10):
                        result_response = await client.get(
                            f"{settings.JUDGE0_API_URL}/submissions/{token}",
                            headers=headers
                        )
                        result = result_response.json()
                        
                        if result.get('status', {}).get('id') not in [1, 2]:  # 1=in queue, 2=processing
                            return result
                        
                        await asyncio.sleep(0.5)
                    
                    return result
                else:
                    logger.error(f"Judge0 API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return None

    @staticmethod
    async def evaluate_code_solution(code: str, test_cases: List[Dict[str, Any]], language_id: int) -> Dict[str, Any]:
        """
        Evaluate code against test cases
        """
        results = []
        passed = 0
        
        for test_case in test_cases:
            result = await Judge0API.execute_code(
                code,
                language_id,
                stdin=test_case.get('input', '')
            )
            
            expected_output = test_case.get('expected_output', '').strip()
            actual_output = result.get('stdout', '').strip() if result else ""
            
            passed_test = expected_output == actual_output
            if passed_test:
                passed += 1
            
            results.append({
                'test_case': test_case,
                'passed': passed_test,
                'expected': expected_output,
                'actual': actual_output,
                'error': result.get('stderr', '') if result else None
            })
        
        return {
            'total_tests': len(test_cases),
            'passed_tests': passed,
            'success_rate': passed / len(test_cases) if test_cases else 0,
            'results': results
        }

class PineconeAPI:
    """Pinecone vector database for semantic search"""
    
    @staticmethod
    async def store_embeddings(texts: List[str], ids: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Store text embeddings in Pinecone
        """
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index(settings.PINECONE_INDEX_NAME)
            
            # Generate embeddings using OpenAI
            embeddings_data = []
            for text, id_val, meta in zip(texts, ids, metadata or [{}] * len(texts)):
                response = openai_client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                embeddings_data.append((id_val, embedding, meta))
            
            # Upsert to Pinecone
            index.upsert(vectors=embeddings_data)
            logger.info(f"Stored {len(texts)} embeddings in Pinecone")
            
        except Exception as e:
            logger.error(f"Pinecone storage error: {str(e)}")

    @staticmethod
    async def search_similar(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar content in Pinecone
        """
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index(settings.PINECONE_INDEX_NAME)
            
            # Generate query embedding
            response = openai_client.embeddings.create(
                input=query_text,
                model="text-embedding-3-small"
            )
            query_embedding = response.data[0].embedding
            
            # Search
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results.get('matches', [])
            
        except Exception as e:
            logger.error(f"Pinecone search error: {str(e)}")
            return []

import asyncio

class ResumeParserAPI:
    """Resume parsing and skill extraction"""
    
    @staticmethod
    async def extract_resume_skills(resume_text: str) -> Dict[str, Any]:
        """
        Extract skills, experience, and education from resume text
        """
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert resume parser. Extract information from resumes and provide:
                        1. Technical skills (programming languages, frameworks, tools)
                        2. Soft skills (communication, leadership, etc.)
                        3. Years of experience (overall)
                        4. Work experience (companies, roles, key responsibilities)
                        5. Education (degrees, institutions)
                        6. Certifications
                        
                        Respond in JSON format with keys: technical_skills, soft_skills, years_of_experience, 
                        work_experience (list of {company, role, years, key_points}), 
                        education (list of {degree, institution, field}),
                        certifications (list of {name, issuer})"""
                    },
                    {
                        "role": "user",
                        "content": f"Extract skills and information from this resume:\n\n{resume_text}"
                    }
                ],
                temperature=0.3,
            )
            
            content = response.choices[0].message.content
            import json
            extraction = json.loads(content)
            return extraction
            
        except Exception as e:
            logger.error(f"Resume parsing error: {str(e)}")
            raise

    @staticmethod
    async def extract_skills_from_file(file_path: str) -> Dict[str, Any]:
        """
        Extract skills from resume file (PDF or DOCX)
        """
        try:
            from PyPDF2 import PdfReader
            from docx import Document
            
            resume_text = ""
            
            # Handle PDF files
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text()
            
            # Handle DOCX files
            elif file_path.endswith('.docx'):
                doc = Document(file_path)
                for paragraph in doc.paragraphs:
                    resume_text += paragraph.text + "\n"
            
            else:
                # Assume plain text
                with open(file_path, 'r') as file:
                    resume_text = file.read()
            
            # Extract skills from text
            return await ResumeParserAPI.extract_resume_skills(resume_text)
            
        except Exception as e:
            logger.error(f"File parsing error: {str(e)}")
            raise

class GroqAPI:
    """Groq API for concept teaching and explanations"""
    
    @staticmethod
    async def teach_concept(skill_name: str, level: str = "beginner") -> Dict[str, Any]:
        """
        Use Groq to teach a concept
        skill_name: The skill or concept to teach
        level: beginner, intermediate, advanced
        """
        try:
            from groq import Groq
            
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            prompt = f"""You are an expert technical educator. Explain the concept of '{skill_name}' 
            at a {level} level. Include:
            1. Definition and overview
            2. Why it's important
            3. Real-world applications
            4. Key concepts to understand
            5. Common mistakes to avoid
            6. Learning path recommendations
            7. Practice exercises
            
            Make it clear, concise, and engaging."""
            
            message = client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            explanation = message.content[0].text if message.content else ""
            
            return {
                "skill": skill_name,
                "level": level,
                "explanation": explanation,
                "generated_at": str(__import__('datetime').datetime.utcnow())
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise

    @staticmethod
    async def generate_learning_recommendations(skill_gaps: List[str], resume_skills: List[str]) -> Dict[str, Any]:
        """
        Generate personalized learning recommendations based on skill gaps
        """
        try:
            from groq import Groq
            
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            gaps_str = ", ".join(skill_gaps[:10])
            resume_str = ", ".join(resume_skills[:10])
            
            prompt = f"""Based on the following information, generate a personalized learning plan:

Current Skills from Resume: {resume_str}

Skill Gaps to Fill: {gaps_str}

Please provide:
1. Priority order of skills to learn
2. For each skill: learning approach, estimated time, and resources
3. Milestones and checkpoints
4. How to practice and apply these skills
5. Timeline recommendations

Be specific and practical."""
            
            message = client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            recommendations = message.content[0].text if message.content else ""
            
            return {
                "skill_gaps": skill_gaps,
                "current_skills": resume_skills,
                "recommendations": recommendations,
                "generated_at": str(__import__('datetime').datetime.utcnow())
            }
            
        except Exception as e:
            logger.error(f"Groq recommendations error: {str(e)}")
            raise
