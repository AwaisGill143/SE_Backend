# ⚡ CareerLaunch AI - Quick Start (5 Minutes)

## ✅ What's Already Running

Right now, both your servers are running:
- **Backend API**: http://localhost:8000 ✅
- **Frontend App**: http://localhost:8080 ✅
- **API Docs**: http://localhost:8000/docs ✅

---

## 🔑 Step 1: Get Your OpenAI API Key (2 minutes)

1. **Go to**: https://platform.openai.com/api-keys
2. **Create Account** or **Login** with Google/GitHub
3. **Click**: "Create new secret key"
4. **Copy** the key (looks like: `sk-proj-xxx...`)
5. **Save** it somewhere safe (you won't see it again!)

### 💡 Pricing
- First time: $5 free credits
- After: Pay per API call (very cheap for testing)
- MCQ Assessment (10 questions) = ~$0.01
- Interview conversation = ~$0.05 per response

---

## 🔧 Step 2: Set OpenAI Key (1 minute)

### Option A: Quick Test (Current Session Only)

In PowerShell, run this BEFORE starting the backend:
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

Then start backend:
```powershell
cd "F:\Career LAunch\SE BACKEND"
python -m uvicorn app.main_enhanced:app --reload --host 0.0.0.0 --port 8000
```

### Option B: Permanent (Using .env File)

Create a file `F:\Career LAunch\SE BACKEND\.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

---

## ✨ Step 3: Test Everything (2 minutes)

### Open Browser
Go to → **http://localhost:8080**

### Login
```
Email: ayesha@example.com
Password: password123
```

### Test Each Feature

**1. Job Parser** 
- Click "Job Parser"
- Paste a job description
- Click "Analyze with AI"
- ✅ Should see AI-analyzed skills

**2. Assessments**
- Click "Assessments"
- Click "Create Assessment"
- Fill in > Click Create
- ✅ Should see AI-generated questions
- Answer & Submit

**3. Interview**
- Click "Interview Simulator"
- Click "Start Interview"
- Type your response
- ✅ Should get AI feedback

**4. Analytics**
- Click "Analytics"
- ✅ Should see your stats

---

## 🎯 Current Feature Status

| Feature | Status | With OpenAI |
|---------|--------|------------|
| Login/Register | ✅ Real | ✅ Real |
| Job Parser | ✅ Works | ✅ Smart analysis |
| Assessments | ✅ Works | ✅ Real questions |
| Interviews | ✅ Works | ✅ Real conversations |
| Learning Paths | ✅ Works | ✅ Smart paths |
| Analytics | ✅ Works | ✅ Full stats |

---

## 📡 API Testing (Advanced)

### Quick Test with Browser
1. Go to http://localhost:8000/docs
2. All endpoints listed with "Try it out" button
3. For protected endpoints:
   - Click "Authorize"
   - Login first to get token
   - Paste in as: `Bearer token-here`

### cURL Test
```bash
# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ayesha@example.com","password":"password123"}'

# Copy the access_token from response

# Analyze Job
curl -X POST http://localhost:8000/api/v1/jobs/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_description":"5+ years Python, FastAPI, PostgreSQL..."}'
```

---

## 🚨 Troubleshooting

### "Authorization error" or "API key error"
**Fix**: Make sure you set OPENAI_API_KEY before starting backend

### "System cannot find the path"
**Fix**: Make sure you're in the right directory:
```powershell
cd "F:\Career LAunch\SE BACKEND"
```

### Backend won't start
**Fix**: Kill existing Python processes:
```powershell
Get-Process python | Stop-Process -Force
```

### Frontend shows blank
**Fix**: Clear cache & reload:
- Press `Ctrl+Shift+Delete`
- Clear all cache
- Refresh page

### Still not working?
Check the tutorial: [DEPLOYMENT_SETUP.md](./DEPLOYMENT_SETUP.md)

---

## 🎓 What This App Does

### For Job Seekers
- 📄 **Analyze Job Descriptions**: AI tells you what skills you need
- 🧪 **Practice Assessments**: AI creates questions from any topic
- 🗣️ **Mock Interviews**: Practice with AI interviewer
- 📚 **Learning Paths**: Get personalized learning recommendations
- 📊 **Track Progress**: See your improvement over time

### For Companies (Future)
- Hire better candidates
- Real skill assessment
- Reduce interview time

---

## 📞 Need Help?

1. ✅ **Backend running?** → Check http://localhost:8000
2. ✅ **Frontend running?** → Check http://localhost:8080
3. ✅ **OpenAI key set?** → Check env variable
4. ❓ **Still stuck?** → See DEPLOYMENT_SETUP.md

---

## 🚀 Next: Deploy to Production

Once everything works locally:

1. **Get a domain** (e.g., careerlaunch.com)
2. **Use Docker** to containerize
3. **Deploy to** AWS/GCP/Heroku/DigitalOcean
4. **Configure HTTPS** (Let's Encrypt free)
5. **Set up database** (PostgreSQL)

See [DEPLOYMENT_SETUP.md](./DEPLOYMENT_SETUP.md) for detailed instructions.

---

**Ready?** → Go to http://localhost:8080 and login! 🚀

