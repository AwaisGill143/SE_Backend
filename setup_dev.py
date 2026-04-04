#!/usr/bin/env python3
"""
CareerLaunch AI Backend - Setup and Run Script
Simple local development without database requirements
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"[*] {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            return True
        else:
            print(f"✗ {description} - FAILED")
            return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False

def main():
    """Main setup process"""
    print("\n" + "="*60)
    print("CareerLaunch AI Backend - Local Development Setup")
    print("="*60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Step 1: Create virtual environment
    if not os.path.exists('venv'):
        run_command(
            f"{sys.executable} -m venv venv",
            "Creating Python virtual environment"
        )
    
    # Step 2: Install minimal dependencies
    venv_python = os.path.join('venv', 'Scripts', 'python')
    venv_pip = os.path.join('venv', 'Scripts', 'pip')
    
    run_command(
        f'"{venv_pip}" install -q fastapi uvicorn pydantic python-dotenv',
        "Installing core dependencies"
    )
    
    # Step 3: Create .env file
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# CareerLaunch AI Backend Configuration
# Development mode - no database required for API testing

ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# JWT Configuration
SECRET_KEY=dev-secret-key-change-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (optional, not needed for basic testing)
OPENAI_API_KEY=sk-test-key
ANTHROPIC_API_KEY=sk-ant-test-key
YOUTUBE_API_KEY=test-key

# Database (optional for basic testing)
DATABASE_URL=sqlite:///./careerlaunch.db

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
""")
        print("✓ Created .env configuration file")
    
    # Step 4: Display next steps
    print("\n" + "="*60)
    print("✓ Setup Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Activate virtual environment:")
    print("   Windows: .\\venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print("\n2. Run the API server:")
    print(f"   .\\venv\\Scripts\\python app/main.py")
    print("\n3. Access the API:")
    print("   Browser: http://localhost:8000/docs")
    print("   API: http://localhost:8000/api/v1")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
