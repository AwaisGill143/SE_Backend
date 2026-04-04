# Quick Start Guide

## 5-Minute Setup

### Option 1: Local Development (Recommended for Development)

1. **Install Dependencies**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup Environment**
```bash
cp .env.example .env
# Edit .env with your API keys and database URL
```

3. **Setup Database**
```bash
# Make sure PostgreSQL is running locally
createdb careerlaunch_db
```

4. **Run Server**
```bash
python app/main.py
# or
uvicorn app.main:app --reload --port 8000
```

5. **Access API**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

### Option 2: Docker (Recommended for Production)

1. **Clone and Setup**
```bash
cd f:\SE BACKEND
```

2. **Create .env file**
```bash
cp .env.example .env
# Set your API keys in .env
```

3. **Run with Docker**
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

4. **Access Application**
- **API**: http://localhost/api/v1
- **Docs**: http://localhost/docs
- **Database**: localhost:5432
- **Redis**: localhost:6379

---

## Common Tasks

### Register as a User
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Analyze a Job Description
```bash
curl -X POST http://localhost:8000/api/v1/jobs/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "job_description": "We are looking for a Senior Python Developer..."
  }'
```

### Create an Assessment
```bash
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "assessment_type": "mcq",
    "difficulty": "medium"
  }'
```

### Start an Interview
```bash
curl -X POST http://localhost:8000/api/v1/interviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Mock Interview",
    "duration_minutes": 30
  }'
```

---

## Database Management

### Create Database Backup
```bash
# PostgreSQL backup
pg_dump careerlaunch_db > backup.sql

# Docker backup
docker-compose exec db pg_dump -U careerlaunch careerlaunch_db > backup.sql
```

### Restore Database
```bash
# Restore from backup
psql careerlaunch_db < backup.sql

# Docker restore
docker-compose exec -T db psql -U careerlaunch careerlaunch_db < backup.sql
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U careerlaunch -d careerlaunch_db -c "SELECT 1"

# In Docker:
docker-compose ps
docker-compose logs db
```

### API Key Issues
- Verify all API keys in `.env` are correct
- Check keys are active/valid
- Review API usage limits

### Redis Connection Issues
```bash
# Test Redis locally
redis-cli ping

# In Docker:
docker-compose exec redis redis-cli ping
```

---

## Testing API Endpoints

### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
response = requests.post(f"{BASE_URL}/users/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "password123"
})

# Login
response = requests.post(f"{BASE_URL}/users/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Analyze Job
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/jobs/analyze", json={
    "job_description": "Senior Backend Engineer..."
}, headers=headers)
```

---

## Performance Tips

1. **Database Optimization**
   - Create indexes for frequently queried columns
   - Use connection pooling
   - Monitor slow queries

2. **Caching**
   - Use Redis for caching frequently accessed data
   - Cache API responses
   - Cache AI model outputs

3. **Async Operations**
   - Use async/await for I/O operations
   - Offload long-running tasks to background jobs

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong passwords for database
- [ ] Enable HTTPS in production
- [ ] Rotate API keys regularly
- [ ] Use environment variables for sensitive data
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Use CORS properly
- [ ] Implement logging and monitoring
- [ ] Regular security audits

---

## Getting Help

- Check the full README.md for detailed documentation
- Review API docs at /docs endpoint
- Check application logs for errors
- Create an issue on GitHub for bugs

---

**Need help? Start with the /docs endpoint for interactive API documentation!**
