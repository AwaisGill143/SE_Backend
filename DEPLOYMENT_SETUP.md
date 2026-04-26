# CareerLaunch AI - Complete Setup & Deployment Guide

## ✅ Current System Status

### Running Services
- **Backend**: http://localhost:8000 (Enhanced version with OpenAI support)
- **Frontend**: http://localhost:8080 or http://localhost:8081
- **API Docs**: http://localhost:8000/docs (Swagger UI)

### Test Credentials
```
Email: ayesha@example.com
Password: password123
```

---

## 🚀 Features Overview

### 1. **Job Parser / Job Analysis** ✅
- **Status**: Fully functional
- **How it works**: Paste a job description, click "Analyze with AI"
- **Current**: Uses mock data (returns demo skills/requirements)
- **With OpenAI**: Returns AI-analyzed skills, technologies, and readiness score

### 2. **Assessments** ✅
- **Status**: Fully functional
- **How it works**: Create assessment → System generates questions → Answer questions → Get score
- **Current**: Uses mock questions
- **With OpenAI**: Generates real questions based on skill focus

### 3. **Interview Simulator** ✅
- **Status**: Fully functional
- **How it works**: Start interview → AI asks questions → Respond → Get feedback
- **Current**: Uses mock interview responses
- **With OpenAI**: Real AI-powered mock interviews with actual feedback

### 4. **Learning Paths** ✅
- **Status**: Fully functional
- **How it works**: System recommends learning resources based on skill gaps

### 5. **Analytics Dashboard** ✅
- **Status**: Fully functional
- **How it works**: View performance metrics, assessment scores, interview stats

---

## 🔑 Enable Real OpenAI Features (5 minutes)

### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up or login to OpenAI
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Step 2: Set Environment Variable

**Option A: Windows PowerShell (One Session)**
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
cd "F:\Career LAunch\SE BACKEND"
python -m uvicorn app.main_enhanced:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Create .env File (Permanent)**
```bash
# Create file: F:\Career LAunch\SE BACKEND\.env
OPENAI_API_KEY=sk-your-key-here
```

Then restart the backend:
```powershell
cd "F:\Career LAunch\SE BACKEND"
python -m uvicorn app.main_enhanced:app --reload
```

### Step 3: Verify it Works
1. Open http://localhost:8080
2. Login with: ayesha@example.com / password123
3. Go to Job Parser
4. Paste a job description
5. Click "Analyze with AI"
6. Should see real AI analysis (not mock data)

---

## 🏗️ Project Architecture

### Frontend Stack
- **Framework**: React 18.3.1 with TypeScript
- **Build Tool**: Vite
- **HTTP Client**: Axios with JWT interceptors
- **UI Components**: shadcn/ui
- **Styling**: Tailwind CSS

### Backend Stack
- **Framework**: FastAPI
- **AI Integration**: OpenAI API (GPT-3.5-turbo)
- **Database**: SQLite (local dev), PostgreSQL (production)
- **Authentication**: JWT tokens
- **Server**: Uvicorn

### Key Files

**Backend** (F:\Career LAunch\SE BACKEND\):
- `app/main_enhanced.py` - Enhanced backend with OA enAI support
- `app/main.py` - Production version with database
- `app/main_simple.py` - Simplified demo version

**Frontend** (F:\Career LAunch\dream-site-realized\):
- `src/lib/api.ts` - API client with token management
- `src/lib/auth.ts` - Authentication service
- `src/components/ProtectedRoute.tsx` - Route protection
- `src/pages/` - Application pages:
  - `Login.tsx` - Login/Register
  - `Dashboard.tsx` - Homepage with stats
  - `JobParser.tsx` - Job analysis
  - `Assessments.tsx` - Practice assessments
  - `InterviewSim.tsx` - Mock interviews
  - `LearningPath.tsx` - Learning resources
  - `Analytics.tsx` - Performance dashboard

---

## 📡 API Endpoints

### Authentication
```
POST   /api/v1/users/register       - Create new account
POST   /api/v1/users/login          - Get access token
POST   /api/v1/users/refresh        - Refresh token
GET    /api/v1/users/me             - Get current user
```

### Job Analysis
```
POST   /api/v1/jobs/analyze         - Analyze job description
GET    /api/v1/jobs/my-analyses     - Get user's analyses
```

### Assessments
```
POST   /api/v1/assessments          - Create assessment
GET    /api/v1/assessments          - Get user's assessments
POST   /api/v1/assessments/{id}/answers/{q_id}  - Submit answer
POST   /api/v1/assessments/{id}/submit          - Submit & grade
```

### Interviews
```
POST   /api/v1/interviews           - Start interview
POST   /api/v1/interviews/{id}/respond          - Send response
POST   /api/v1/interviews/{id}/end              - End & get feedback
GET    /api/v1/interviews           - Get user's interviews
```

### Learning Paths
```
POST   /api/v1/learning-paths       - Create path
GET    /api/v1/learning-paths       - Get user's paths
```

### Analytics
```
GET    /api/v1/analytics            - Get user analytics
```

---

## 🧪 Testing the APIs

### Using Swagger UI (Easiest)
1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. For protected endpoints:
   - First login at `/api/v1/users/login`
   - Copy the `access_token`
   - Click "Authorize" button (top right)
   - Paste token as: `Bearer sk-your-token`
   - Now test other endpoints

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "username":"testuser",
    "full_name":"Test User",
    "password":"password123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Analyze Job (with token)
curl -X POST http://localhost:8000/api/v1/jobs/analyze \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"job_description":"5+ years Python development, FastAPI, PostgreSQL..."}'
```

---

## 🚢 Deployment Guide

### Docker Deployment

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./SE\ BACKEND
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/careerlaunch
    depends_on:
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./dream-site-realized
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=careerlaunch
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

### Production Checklist
- [ ] Change SECRET_KEY to random value
- [ ] Set OPENAI_API_KEY
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Set CORS_ORIGINS to your domain
- [ ] Use environment-specific configuration
- [ ] Set DEBUG=false
- [ ] Enable database backups
- [ ] Configure logging
- [ ] Set up monitoring

---

## 🔧 Troubleshooting

### "Authorization header missing" Error
**Solution**: 
1. Make sure you're logged in
2. Check that Authorization: Bearer token is being sent
3. Look at browser DevTools Network tab to verify headers

### "OpenAI API key not configured" Warning
**Solution**: 
1. This is normal if you haven't set OPENAI_API_KEY
2. Features will use mock responses
3. To enable real AI: Follow Section 3 above

### Port Already in Use
```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Or use specific port
python -m uvicorn app.main_enhanced:app --port 9000
```

### Frontend Can't Connect to Backend
**Check**:
1. Backend running on http://localhost:8000?
2. VITE_API_URL correct in .env.local?
3. CORS configured in backend?
4. Check browser console for Network errors

---

## 📚 Next Steps

1. **Set OpenAI API Key** (5 minutes)
   - Get from https://platform.openai.com/api-keys
   - Set OPENAI_API_KEY env variable
   - Restart backend
   - Test in app

2. **Test All Features** (10 minutes)
   - Create account
   - Try Job Parser
   - Create assessment
   - Start interview
   - Check analytics

3. **Customize** (optional)
   - Update branding/colors
   - Add more assessment types
   - Configure interview difficulty
   - Add learning resources

4. **Deploy** (production)
   - Switch to PostgreSQL
   - Use Docker
   - Configure domain/HTTPS
   - Set up monitoring

---

## 📖 API Response Examples

### Job Analysis Response
```json
{
  "id": 1,
  "job_title": "Senior Backend Engineer",
  "company": "Tech Corp",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "System Design"],
  "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
  "soft_skills": ["Communication", "Leadership", "Problem-solving"],
  "experience_required": "5+ years backend development",
  "readiness_score": 75.5
}
```

### Assessment Response
```json
{
  "id": 1,
  "title": "Backend Assessment",
  "assessment_type": "mcq",
  "skill_focus": "Python",
  "questions": [
    {
      "id": 1,
      "question": "What is async/await?",
      "options": ["..."],
      "correct_answer": 0
    }
  ],
  "score": null,
  "feedback": null
}
```

### Interview Response
```json
{
  "interview_id": 1,
  "user_message": "I have 5 years of Python experience",
  "ai_response": "Great! Tell me about your experience with..."
}
```

### Authentication Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **React**: https://react.dev/
- **Vite**: https://vitejs.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

---

## 📞 Support

If you encounter issues:

1. Check the logs:
   - Frontend: Browser DevTools Console (F12)
   - Backend: Terminal output

2. Verify endpoints work:
   - Visit http://localhost:8000/docs
   - Test endpoints directly

3. Common fixes:
   - Restart both servers
   - Clear browser cache
   - Check CORS configuration
   - Verify API key is set

---

## 📝 Deployment Summary

**Current Setup (Development)**:
- ✅ Backend running (SQLite, mock AI)
- ✅ Frontend running
- ✅ Authentication working
- ⚠️ AI features (mock only)

**To Go Live**:
1. Add OPENAI_API_KEY
2. Switch to PostgreSQL
3. Add HTTPS
4. Deploy to cloud (AWS, GCP, Heroku, etc.)

---

**Last Updated**: April 5, 2026  
**Version**: 2.0.0 (Enhanced)
