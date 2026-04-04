# CareerLaunch AI Backend

AI-powered platform for job interview preparation with personalized learning paths, multi-format assessments, and adaptive mock interviews.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Development](#development)

## Project Overview

CareerLaunch AI is a comprehensive platform designed to revolutionize job interview preparation by:

- **Smart Job Parser**: AI-powered extraction of required skills, technologies, and qualifications from job postings
- **Personalized Learning Paths**: Automated skill gap analysis with curated learning resources
- **Multi-Format Assessments**: MCQs, coding challenges, system design, and behavioral questions
- **AI Interview Simulator**: Real-time conversational AI with adaptive questioning and comprehensive feedback

## Features

### Module 1: Smart Job Parser
- Extract required skills, technologies, and qualifications from job postings
- Experience level classification and role requirement analysis
- Technology stack identification and categorization
- Readiness score calculation
- Skill gap identification

### Module 2: Personalized Learning Paths
- Automated skill gap analysis
- YouTube video playlist curation
- Recommended courses, documentation, and projects
- Progress tracking with milestone markers

### Module 3: Multi-Format Assessments
- Multiple choice questions (MCQs)
- Coding challenges with automated evaluation
- System design questions
- Behavioral questions with AI evaluation

### Module 4: AI Interview Simulator
- Real-time conversational AI
- Adaptive questions based on responses
- Video and audio recording support
- Comprehensive feedback reports
- Interview analytics

## System Architecture

```
CareerLaunch AI Backend
├── FastAPI Application
├── PostgreSQL Database
├── External AI APIs (OpenAI/Claude)
├── Judge0 (Code Execution)
├── YouTube API (Learning Resources)
├── Pinecone (Vector Search)
└── Redis (Caching & Queues)
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Git

### Setup Steps

1. **Clone the repository**
```bash
cd "f:\SE BACKEND"
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Setup the database**
```bash
# Create PostgreSQL database
createdb careerlaunch_db

# Run migrations (if using Alembic)
alembic upgrade head
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example` with the following key variables:

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/careerlaunch_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=AIza...
JUDGE0_API_KEY=...

# Pinecone
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=careerlaunch-embeddings

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Running the Application

### Development Server

```bash
# Using Uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python app/main.py
```

### Access the API

- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

### Production Deploy

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication

All endpoints (except register and login) require authentication using JWT tokens.

**Headers**: `Authorization: Bearer <access_token>`

### Endpoints

#### 1. Authentication Endpoints

**Register User**
```
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "password": "password123"
}
```

**Login**
```
POST /users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### 2. Job Parser Endpoints

**Analyze Job Description**
```
POST /jobs/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_description": "..."
}
```

**Get Job Analysis**
```
GET /jobs/{analysis_id}
Authorization: Bearer <token>
```

**Get Readiness Score**
```
GET /jobs/{analysis_id}/readiness-score
Authorization: Bearer <token>
```

**Get Skill Gaps**
```
GET /jobs/{analysis_id}/skill-gaps
Authorization: Bearer <token>
```

#### 3. Learning Paths Endpoints

**Create Learning Path**
```
POST /learning-paths
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_analysis_id": 1
}
```

**Get Learning Path**
```
GET /learning-paths/{path_id}
Authorization: Bearer <token>
```

**Complete Module**
```
POST /learning-paths/{path_id}/modules/{module_id}/complete
Authorization: Bearer <token>
```

#### 4. Assessments Endpoints

**Create Assessment**
```
POST /assessments
Authorization: Bearer <token>
Content-Type: application/json

{
  "assessment_type": "mcq",
  "difficulty": "medium",
  "job_analysis_id": 1
}
```

**Submit Assessment**
```
POST /assessments/{assessment_id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_answers": [0, 1, 2],
  "code": null
}
```

**Get Assessment Score**
```
GET /assessments/{assessment_id}/score
Authorization: Bearer <token>
```

#### 5. Interview Endpoints

**Start Interview**
```
POST /interviews
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Software Engineer Interview",
  "duration_minutes": 30,
  "job_analysis_id": 1
}
```

**Respond to Interview Question**
```
POST /interviews/{interview_id}/respond
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Your response here..."
}
```

**End Interview**
```
POST /interviews/{interview_id}/end
Authorization: Bearer <token>
```

**Get Interview Feedback**
```
GET /interviews/{interview_id}/feedback
Authorization: Bearer <token>
```

## Project Structure

```
f:\SE BACKEND\
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database setup
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py          # Health check endpoints
│   │   ├── users.py           # User management endpoints
│   │   ├── jobs.py            # Job parser endpoints
│   │   ├── learning_paths.py  # Learning path endpoints
│   │   ├── assessments.py     # Assessment endpoints
│   │   └── interviews.py      # Interview endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py            # User business logic
│   │   ├── job_service.py             # Job analysis logic
│   │   ├── learning_path_service.py   # Learning path logic
│   │   ├── assessment_service.py      # Assessment logic
│   │   └── interview_service.py       # Interview logic
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication utilities
│   │   └── external_apis.py    # External API integrations
│   └── middleware/
│       ├── __init__.py
│       └── error_handler.py    # Error handling middleware
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## Technologies

### Backend Framework
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI application server

### Database
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations

### AI/ML
- **OpenAI GPT-4**: Natural language processing
- **Anthropic Claude**: Alternative LLM
- **LangChain**: AI workflow management
- **Pinecone**: Vector database for semantic search

### External Services
- **Judge0 API**: Code execution and evaluation
- **YouTube API**: Learning resource discovery
- **Redis**: Caching and task queues

### Security
- **JWT**: Authentication tokens
- **Bcrypt**: Password hashing
- **python-jose**: JWT implementation

### Testing & Development
- **pytest**: Testing framework
- **httpx**: HTTP client for testing

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_users.py
```

### Code Style

```bash
# Format code with black
black app/

# Lint with pylint
pylint app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## API Response Format

### Success Response
```json
{
  "data": {...},
  "message": "Success",
  "status_code": 200
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Performance Optimization

### Caching Strategy
- Redis caching for frequent queries
- Database connection pooling
- Response compression

### Database Optimization
- Indexed fields for fast queries
- Connection pooling
- Query optimization

## Logging

Logs are configured in the application with:
- Application logs at INFO level
- Database queries logged when SQLALCHEMY_ECHO=True
- Error tracking and reporting

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Issue Tracking**: [GitHub Issues]
- **Contributing**: See CONTRIBUTING.md

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Email verification
- [ ] Two-factor authentication
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Real-time collaboration features
- [ ] Video recording and playback
- [ ] Advanced ML-based feedback
- [ ] Company-specific question patterns
- [ ] Salary negotiation guidance
- [ ] Career path recommendations

## Contact

For questions or inquiries, please contact the development team.

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0
