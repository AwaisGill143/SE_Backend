# CareerLaunch AI Backend - Local Development Setup

## 🚀 Quickest Way to Start

### **Option 1: Double-Click (Windows)**
Simply double-click `run.bat` - that's it!

**What it does:**
- Creates virtual environment
- Installs required packages
- Starts the API server
- Opens documentation automatically

### **Option 2: PowerShell Command**
```powershell
cd "f:\SE BACKEND"
python app/main_simple.py
```

### **Option 3: Manual Setup**
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn

# Run server
python app/main_simple.py
```

---

## 📖 Access the API

Once the server starts, open your browser:

- **Interactive Documentation** (Swagger UI): http://localhost:8000/docs
- **Alternative Documentation** (ReDoc): http://localhost:8000/redoc
- **API Root**: http://localhost:8000

---

## 🧪 Test the API

### Method 1: Use Browser (Swagger UI)
1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in the parameters
4. Click "Execute"

### Method 2: PowerShell Commands

```powershell
# Health check
curl http://localhost:8000/api/v1/health

# Register a user
$body = @{
    email = "test@example.com"
    username = "testuser"
    full_name = "Test User"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Method 3: Python Script

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Analyze a job
response = requests.post(
    f"{BASE_URL}/jobs/analyze",
    json={"job_description": "Senior Python Developer with 5+ years experience..."}
)
print(response.json())
```

---

## 📁 Project Structure

```
f:\SE BACKEND\
├── run.bat                          ← Double-click to start! 
├── QUICK_RUN.md                     ← Quick start guide
├── app/
│   ├── main_simple.py              ← Simplified API (no database needed)
│   ├── main.py                      ← Full API (requires PostgreSQL)
│   ├── config_simple.py             ← Simplified config
│   ├── config.py                    ← Full config
│   ├── models.py                    ← Database models
│   ├── schemas.py                   ← Request/response schemas
│   ├── routers/                     ← API endpoints
│   ├── services/                    ← Business logic
│   └── utils/                       ← Utilities
├── requirements-dev.txt             ← Dev dependencies
├── requirements.txt                 ← Full dependencies
├── docker-compose.yml               ← Docker setup
└── README.md                        ← Full documentation
```

---

## 🔧 Two Versions Available

### **1. Simplified Version (main_simple.py)**
- ✅ No database setup needed
- ✅ Works immediately
- ✅ Perfect for testing and development
- ✅ Demo data in memory
- ❌ Data not persistent

**Start with:**
```powershell
python app/main_simple.py
```

### **2. Full Version (main.py)**
- ✅ Full features with database
- ✅ Persistent data storage
- ✅ Production-ready
- ❌ Requires PostgreSQL setup
- ❌ More complex setup

**Start with:**
```powershell
# After installing all dependencies and setting up PostgreSQL
python app/main.py
```

---

## 📚 Using the API

### Create User & Get Token
```bash
# Register
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"user@example.com\",
    \"username\": \"testuser\",
    \"full_name\": \"Test User\",
    \"password\": \"password123\"
  }"

# Login
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"user@example.com\",
    \"password\": \"password123\"
  }"
```

### Analyze a Job
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/analyze" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_description\": \"Senior Backend Engineer...\"
  }"
```

### Create Assessment
```bash
curl -X POST "http://localhost:8000/api/v1/assessments" \
  -H "Content-Type: application/json" \
  -d "{
    \"assessment_type\": \"mcq\",
    \"difficulty\": \"medium\"
  }"
```

### Start Interview
```bash
curl -X POST "http://localhost:8000/api/v1/interviews" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Mock Interview\",
    \"duration_minutes\": 30
  }"
```

---

## 🔌 API Endpoints Summary

### Jobs
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/jobs/analyze` | Analyze job description |
| GET | `/api/v1/jobs/{id}` | Get analysis details |
| GET | `/api/v1/jobs/{id}/readiness-score` | Get readiness score |
| GET | `/api/v1/jobs/{id}/skill-gaps` | Get skill gaps |

### Users
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/users/register` | Register user |
| POST | `/api/v1/users/login` | Login user |
| GET | `/api/v1/users/me` | Get profile |

### Assessments
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/assessments` | Create assessment |
| POST | `/api/v1/assessments/{id}/submit` | Submit answers |
| GET | `/api/v1/assessments/{id}/score` | Get score |

### Interviews
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/interviews` | Start interview |
| POST | `/api/v1/interviews/{id}/respond` | Respond to question |
| POST | `/api/v1/interviews/{id}/end` | End interview |
| GET | `/api/v1/interviews/{id}/feedback` | Get feedback |

---

## ❓ Troubleshooting

### "Python not found"
- Install Python 3.9+ from https://python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal

### Port 8000 already in use
```powershell
# Find and kill the process
Get-NetTCPConnection -LocalPort 8000
taskkill /PID <PID> /F
```

### Module errors
```powershell
# Make sure venv is activated
.\venv\Scripts\activate

# Reinstall packages
pip install --upgrade fastapi uvicorn
```

### API returns 404
- Make sure server is running: `python app/main_simple.py`
- Check the URL is correct (case-sensitive after `/api`)
- Try http://localhost:8000/docs first

---

## 📊 What to Try First

1. **✅ Start the server**
   ```powershell
   python app/main_simple.py
   ```

2. **📚 Open Swagger UI**
   - Visit: http://localhost:8000/docs
   - Click on any endpoint
   - Click "Try it out"
   - Click "Execute"

3. **👤 Register a User**
   - Email: `test@example.com`
   - Username: `testuser`
   - Full Name: `Test User`
   - Password: `password123`

4. **🔐 Login**
   - Use the credentials from step 3

5. **💼 Analyze a Job**
   - Submit a job description
   - See the analysis results

6. **📝 Create Assessment**
   - Create an MCQ assessment
   - See demo questions

7. **🎤 Start Interview**
   - Start a mock interview
   - See AI responses

---

## 🚀 Next Steps

1. **Explore the API** - Use Swagger UI to test all endpoints
2. **Read the code** - Check `app/main_simple.py` to understand structure
3. **Modify responses** - Edit `main_simple.py` to change demo data
4. **Setup full version** - Follow README.md for production setup
5. **Add your API keys** - Update `.env` for real AI features

---

## 📞 Need Help?

- **API Documentation**: http://localhost:8000/docs
- **Full Guide**: See `README.md`
- **Deployment**: See `DEPLOYMENT.md`
- **Examples**: See `TESTING_USECASES.md`

---

**🎉 Ready to go! Start with: `python app/main_simple.py` or double-click `run.bat`**
