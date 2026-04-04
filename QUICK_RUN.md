# CareerLaunch AI Backend - Quick Start (5 Minutes)

## For Immediate Testing (No Database Required)

### Option 1: Run Simplified Version (Fastest)

```powershell
# Navigate to backend directory
cd "f:\SE BACKEND"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install minimal dependencies
pip install fastapi uvicorn

# Run the simplified API server
python app/main_simple.py
```

**Access the API:**
- **Swagger UI Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### API Testing Examples

```powershell
# In another terminal, test the API:

# Register user
curl -X POST http://localhost:8000/api/v1/users/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login `
  -H "Content-Type: application/json" `
  -d '{"email": "test@example.com", "password": "password123"}'

# Analyze a job
curl -X POST http://localhost:8000/api/v1/jobs/analyze `
  -H "Content-Type: application/json" `
  -d '{"job_description": "Senior Python Developer with FastAPI experience..."}'

# Get readiness score
curl http://localhost:8000/api/v1/jobs/1/readiness-score

# Start a mock interview
curl -X POST http://localhost:8000/api/v1/interviews `
  -H "Content-Type: application/json" `
  -d '{"title": "Mock Interview", "duration_minutes": 30}'
```

---

## For Full Development Setup (With Database)

### Prerequisites
- PostgreSQL running locally
- Redis (optional, for caching)

### Setup Steps

```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Configure environment
copy .env.example .env
# Edit .env with your DATABASE_URL and API keys

# 4. Create database
psql -U postgres -c "CREATE DATABASE careerlaunch_db;"

# 5. Run migrations (when Alembic is set up)
# alembic upgrade head

# 6. Start server
python app/main.py
```

---

## Available Endpoints (Simplified Version)

### Health & Status
- `GET /` - Root info
- `GET /api/v1/health` - Health check

### Users (Demo)
- `POST /api/v1/users/register` - Register
- `POST /api/v1/users/login` - Login
- `GET /api/v1/users/me` - Get profile

### Job Parser
- `POST /api/v1/jobs/analyze` - Analyze job
- `GET /api/v1/jobs/{id}` - Get analysis
- `GET /api/v1/jobs/{id}/readiness-score` - Get score
- `GET /api/v1/jobs/{id}/skill-gaps` - Get gaps

### Learning Paths
- `POST /api/v1/learning-paths` - Create path

### Assessments
- `POST /api/v1/assessments` - Create assessment
- `POST /api/v1/assessments/{id}/submit` - Submit answers
- `GET /api/v1/assessments/{id}/score` - Get score

### Interviews
- `POST /api/v1/interviews` - Start interview
- `POST /api/v1/interviews/{id}/respond` - Respond
- `POST /api/v1/interviews/{id}/end` - End interview
- `GET /api/v1/interviews/{id}/feedback` - Get feedback

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
r = requests.post(f"{BASE_URL}/users/register", json={
    "email": "user@example.com",
    "username": "user",
    "full_name": "Test User",
    "password": "pass123"
})
print(r.json())

# Login
r = requests.post(f"{BASE_URL}/users/login", json={
    "email": "user@example.com",
    "password": "pass123"
})
token = r.json()["access_token"]
print(f"Token: {token}")

# Analyze job
r = requests.post(f"{BASE_URL}/jobs/analyze", json={
    "job_description": "Senior Backend Engineer with Python..."
})
print(f"Analysis: {r.json()}")

# Get readiness
r = requests.get(f"{BASE_URL}/jobs/1/readiness-score")
print(f"Readiness: {r.json()}")
```

---

## Troubleshooting

### ModuleNotFoundError
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall packages
pip install fastapi uvicorn
```

### Port 8000 already in use
```powershell
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python app/main_simple.py --port 8001
```

### Can't connect to database
```powershell
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Use simplified version without DB:
python app/main_simple.py
```

---

## Next Steps

1. ✅ **Start the server** - `python app/main_simple.py`
2. 📚 **Read API docs** - Open http://localhost:8000/docs in browser
3. 🧪 **Test endpoints** - Use Swagger UI or curl
4. 📝 **Review code** - Check `app/main_simple.py`
5. 🚀 **Deploy** - Follow DEPLOYMENT.md when ready

---

**Ready to go! Start with:** `python app/main_simple.py`
