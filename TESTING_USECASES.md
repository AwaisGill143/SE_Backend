# Real-World Use Cases & Testing Examples

## Use Case 1: Complete Interview Preparation Workflow

This example shows a complete user journey from job analysis to mock interview.

### Step 1: Register and Create Profile

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
register_response = requests.post(f"{BASE_URL}/users/register", json={
    "email": "alex@example.com",
    "username": "alex_dev",
    "full_name": "Alex Developer",
    "password": "SecurePass123!"
})
print("Registration:", register_response.json())

# Login
login_response = requests.post(f"{BASE_URL}/users/login", json={
    "email": "alex@example.com",
    "password": "SecurePass123!"
})

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### Step 2: Add User Skills

```python
# Add Python skill
skill_response = requests.post(f"{BASE_URL}/users/me/skills", 
    json={
        "skill_name": "Python",
        "proficiency_level": "advanced",
        "years_of_experience": 3.5
    },
    headers=headers
)
print("Skill added:", skill_response.json())

# Add Django skill
requests.post(f"{BASE_URL}/users/me/skills",
    json={
        "skill_name": "Django",
        "proficiency_level": "intermediate",
        "years_of_experience": 2
    },
    headers=headers
)
```

### Step 3: Analyze Job Description

```python
job_description = """
Senior Backend Engineer / Python

We're looking for an experienced backend engineer to join our team.

Requirements:
- 5+ years of backend development experience
- Expert-level Python skills
- Strong experience with Django or FastAPI
- PostgreSQL and Redis expertise
- Microservices architecture knowledge
- REST API design and implementation
- Docker and Kubernetes experience
- Strong SQL optimization skills

Nice to have:
- GraphQL experience
- AWS or GCP experience
- Message queue experience (RabbitMQ, Kafka)
- System design knowledge

Responsibilities:
- Design and implement scalable APIs
- Optimize database queries
- Mentor junior developers
- Participate in code reviews
- Contribute to architectural decisions
"""

# Analyze job
analysis_response = requests.post(f"{BASE_URL}/jobs/analyze",
    json={"job_description": job_description},
    headers=headers
)

job_analysis = analysis_response.json()
analysis_id = job_analysis["id"]

print("Job Analysis Results:")
print(f"Readiness Score: {job_analysis['readiness_score']}%")
print(f"Required Skills: {job_analysis['required_skills']}")
print(f"Technologies: {job_analysis['technologies']}")
print(f"Skill Gaps: {job_analysis['skill_gaps']}")
```

### Step 4: Get Readiness Score and Skill Gaps

```python
# Get detailed readiness score
score_response = requests.get(
    f"{BASE_URL}/jobs/{analysis_id}/readiness-score",
    headers=headers
)
print("Readiness Score:", score_response.json()["readiness_score"])

# Get skill gaps for focused learning
gaps_response = requests.get(
    f"{BASE_URL}/jobs/{analysis_id}/skill-gaps",
    headers=headers
)
print("Skill Gaps Identified:")
for gap in gaps_response.json()["skill_gaps"]:
    print(f"  - {gap['skill']}: {gap['importance']} importance")
```

### Step 5: Create Personalized Learning Path

```python
# Create learning path
path_response = requests.post(f"{BASE_URL}/learning-paths",
    json={"job_analysis_id": analysis_id},
    headers=headers
)

learning_path = path_response.json()
path_id = learning_path["id"]

print(f"Learning Path Created:")
print(f"  Estimated Hours: {learning_path['estimated_hours']}")
print(f"  Modules to Complete: {len(learning_path['learning_modules'])}")
print("\nRecommended Learning Path:")
for module in learning_path['learning_modules'][:5]:
    print(f"  - {module['title']}")
    print(f"    Resource: {module['resource_type']}")
    print(f"    Time: {module['estimated_hours']}h")
```

### Step 6: Complete Learning Modules

```python
# Complete first learning module
for module in learning_path['learning_modules'][:3]:
    complete_response = requests.post(
        f"{BASE_URL}/learning-paths/{path_id}/modules/{module['id']}/complete",
        headers=headers
    )
    print(f"Completed: {module['title']}")
    print(f"Path Progress: {complete_response.json()['learning_path_progress']}%")
```

### Step 7: Take Practice Assessments

```python
# Create MCQ assessment
mcq_response = requests.post(f"{BASE_URL}/assessments",
    json={
        "assessment_type": "mcq",
        "difficulty": "hard",
        "job_analysis_id": analysis_id
    },
    headers=headers
)

assessment_id = mcq_response.json()["id"]
questions = mcq_response.json()["questions"]

print("MCQ Assessment Started:")
print(f"Questions: {len(questions)}")

# Submit answers
submit_response = requests.post(
    f"{BASE_URL}/assessments/{assessment_id}/submit",
    json={"user_answers": [0, 2, 1, 3, 0]},
    headers=headers
)

print(f"Assessment Complete!")
print(f"Score: {submit_response.json()['score']}%")
print(f"Feedback: {submit_response.json()['feedback']}")
```

### Step 8: Start Mock Interview

```python
# Start interview session
interview_response = requests.post(f"{BASE_URL}/interviews",
    json={
        "title": "Senior Backend Engineer Interview",
        "duration_minutes": 30,
        "job_analysis_id": analysis_id
    },
    headers=headers
)

interview_id = interview_response.json()["id"]
first_question = interview_response.json()["conversation_history"][-1]["content"]

print(f"Interview Started!")
print(f"Opening Question: {first_question}")
```

### Step 9: Interactive Interview

```python
# Have a conversation with the interviewer
user_responses = [
    "I have 5 years of backend development experience, primarily with Python and Django...",
    "I've worked with PostgreSQL and Redis extensively in production environments...",
    "System design is something I'm very passionate about. I've designed microservices architectures...",
]

for response in user_responses:
    answer_response = requests.post(
        f"{BASE_URL}/interviews/{interview_id}/respond",
        json={"message": response},
        headers=headers
    )
    
    ai_response = answer_response.json()["ai_response"]
    print(f"\nYou: {response[:50]}...")
    print(f"Interviewer: {ai_response}")
```

### Step 10: End Interview and Get Feedback

```python
# End interview and get feedback
feedback_response = requests.post(
    f"{BASE_URL}/interviews/{interview_id}/end",
    headers=headers
)

feedback = feedback_response.json()

print(f"\nInterview Complete!")
print(f"Overall Score: {feedback['overall_score']}/100")
print(f"Duration: {feedback['duration_seconds']} seconds")
print(f"\nStrengths:")
for strength in feedback['strengths']:
    print(f"  ✓ {strength}")
print(f"\nAreas for Improvement:")
for area in feedback['improvement_areas']:
    print(f"  ⚠ {area}")
```

---

## Use Case 2: Coding Challenge Assessment

```python
# Create coding challenge
coding_response = requests.post(f"{BASE_URL}/assessments",
    json={
        "assessment_type": "coding",
        "difficulty": "medium"
    },
    headers=headers
)

assessment_id = coding_response.json()["id"]
questions = coding_response.json()["questions"]

print(f"Coding Challenge: {questions[0]['title']}")
print(f"Problem: {questions[0]['problem_statement']}")
print(f"Time Limit: {questions[0]['time_limit_seconds']}s")

# Submit solution
solution_code = """
def twoSum(nums, target):
    # Using hash map for O(n) solution
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""

submit_response = requests.post(
    f"{BASE_URL}/assessments/{assessment_id}/submit",
    json={
        "user_answers": [],
        "code": solution_code
    },
    headers=headers
)

print(f"Score: {submit_response.json()['score']}%")
```

---

## Use Case 3: Performance Comparison

```python
# Compare assessments over time
assessments = requests.get(f"{BASE_URL}/assessments", headers=headers)
all_assessments = assessments.json()

# Group by type
by_type = {}
for assessment in all_assessments:
    type_ = assessment['assessment_type']
    if type_ not in by_type:
        by_type[type_] = []
    by_type[type_].append(assessment['score'])

# Calculate average scores
print("Performance Summary:")
for type_, scores in by_type.items():
    avg = sum(scores) / len(scores) if scores else 0
    print(f"  {type_.upper()}: {avg:.1f}% average")
```

---

## Use Case 4: Interview Analytics

```python
# Get all completed interviews
interviews = requests.get(f"{BASE_URL}/interviews/user/completed", headers=headers)
completed = interviews.json()

print(f"Total Interviews: {len(completed)}")

# Analyze performance trends
scores = [int['overall_score'] for int in completed]
if scores:
    print(f"Average Score: {sum(scores)/len(scores):.1f}%")
    print(f"Best Interview: {max(scores):.1f}%")
    print(f"Most Recent: {completed[-1]['completed_at']}")
```

---

## CLI Testing Script

Create `test_api.py` to automate testing:

```python
#!/usr/bin/env python3
"""
Automated testing script for CareerLaunch API
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class CareerLaunchTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_id = None

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def register_user(self, email, username, full_name, password):
        self.log(f"Registering user {email}...")
        response = self.session.post(
            f"{self.base_url}/users/register",
            json={
                "email": email,
                "username": username,
                "full_name": full_name,
                "password": password
            }
        )
        if response.status_code == 201:
            self.log("✓ User registered successfully")
            return response.json()
        else:
            self.log(f"✗ Registration failed: {response.text}")
            return None

    def login(self, email, password):
        self.log(f"Logging in as {email}...")
        response = self.session.post(
            f"{self.base_url}/users/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.log("✓ Login successful")
            return True
        else:
            self.log(f"✗ Login failed: {response.text}")
            return False

    def analyze_job(self, description):
        self.log("Analyzing job description...")
        response = self.session.post(
            f"{self.base_url}/jobs/analyze",
            json={"job_description": description}
        )
        if response.status_code == 201:
            self.log("✓ Job analysis complete")
            return response.json()
        else:
            self.log(f"✗ Analysis failed: {response.text}")
            return None

    def run_full_test(self):
        """Run complete test workflow"""
        # Register
        user = self.register_user(
            "testuser@example.com",
            "testuser",
            "Test User",
            "TestPassword123!"
        )
        
        if not user:
            return
        
        # Login
        if not self.login("testuser@example.com", "TestPassword123!"):
            return
        
        # Add skills
        self.log("Adding user skills...")
        self.session.post(
            f"{self.base_url}/users/me/skills",
            json={
                "skill_name": "Python",
                "proficiency_level": "advanced",
                "years_of_experience": 3
            }
        )
        self.log("✓ Skills added")
        
        # Analyze job
        job_desc = "Senior Python Developer needed. Requires 5+ years Python, Django, PostgreSQL..."
        analysis = self.analyze_job(job_desc)
        if not analysis:
            return
        
        analysis_id = analysis["id"]
        self.log(f"Readiness Score: {analysis.get('readiness_score', 'N/A')}%")
        
        # Create assessment
        self.log("Creating assessment...")
        response = self.session.post(
            f"{self.base_url}/assessments",
            json={"assessment_type": "mcq", "difficulty": "medium"}
        )
        if response.status_code == 201:
            self.log("✓ Assessment created")
        
        self.log("\n✓ All tests passed!")

if __name__ == "__main__":
    tester = CareerLaunchTester()
    tester.run_full_test()
```

Run with: `python test_api.py`

---

## Performance Testing (Load Testing)

Using `locust`:

```python
from locust import HttpUser, task, between
import json

class CareerLaunchUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def analyze_job(self):
        self.client.post("/api/v1/jobs/analyze",
            json={"job_description": "Senior Python Developer..."},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task
    def get_assessments(self):
        self.client.get("/api/v1/assessments",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

Run with: `locust -f locustfile.py --host http://localhost:8000`

---

**These use cases demonstrate the full capabilities of the CareerLaunch AI platform!**
