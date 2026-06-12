#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Helper
Deploy your Enterprise AI System to the cloud in 5 minutes
"""

import os
import subprocess
import sys

print("""
╔════════════════════════════════════════════════════════════════╗
║   🚀 ENTERPRISE AI - CLOUD DEPLOYMENT HELPER                  ║
╚════════════════════════════════════════════════════════════════╝
""")

def check_git():
    """Check if git is installed"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git is installed")
        return True
    except:
        print("❌ Git not found. Please install from https://git-scm.com")
        return False

def check_github_account():
    """Prompt for GitHub account info"""
    print("\n📋 GITHUB SETUP REQUIRED")
    print("=" * 60)
    username = input("Enter your GitHub username: ").strip()
    repo_name = input("Enter repository name (e.g., enterprise-ai-agent): ").strip()
    return username, repo_name

def setup_git_repo(username, repo_name):
    """Initialize and setup git repository"""
    print(f"\n🔧 Setting up Git repository...")
    
    # Initialize repo if needed
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], check=True)
        print("✅ Git repository initialized")
    
    # Add remote
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    try:
        subprocess.run(["git", "remote", "add", "origin", remote_url], 
                      capture_output=True, check=False)
    except:
        pass
    
    # Stage and commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Deploy to Streamlit Cloud"], 
                  capture_output=True, check=False)
    
    print(f"✅ Staged for commit to: {remote_url}")
    return remote_url

def show_deployment_steps():
    """Show step-by-step deployment instructions"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║           🎯 DEPLOYMENT STEPS (5 MINUTES)                      ║
╚════════════════════════════════════════════════════════════════╝

📍 STEP 1: PUSH TO GITHUB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Create a NEW repository on GitHub (don't initialize with README)
2. Run these commands:
   
   git branch -M main
   git push -u origin main

Then wait for it to complete.

📍 STEP 2: DEPLOY FASTAPI BACKEND (Render.com)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to https://render.com
2. Sign up with GitHub (or create account)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Fill in:
   - Name: enterprise-ai-api
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   - Plan: Free
6. Click "Advanced" → Add Environment Variables:
   - GEMINI_API_KEY = your_key_here
   - TAVILY_API_KEY = your_key_here
7. Click "Create Web Service"
8. Copy the URL (e.g., https://enterprise-ai-api.onrender.com)

📍 STEP 3: UPDATE STREAMLIT CONFIG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Edit ui/dashboard.py line 15 and update:
   API_URL = "https://enterprise-ai-api.onrender.com/api/tasks"

Then commit and push to GitHub.

📍 STEP 4: DEPLOY STREAMLIT UI (Streamlit Cloud)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Set Main file path: ui/dashboard.py
5. Click "Deploy"
6. Go to Settings → Secrets
7. Add secrets:
   GEMINI_API_KEY = "your_key"
   TAVILY_API_KEY = "your_key"
8. Save

📍 STEP 5: SHARE WITH THE WORLD! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your app URL: https://[username]-enterprise-ai-agent.streamlit.app

Share this link with anyone to use your AI system!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS:
✓ Free tier on Render spins down after 15 min of inactivity
✓ Free tier on Streamlit is fully always running
✓ Upgrade to paid for better performance
✓ Both services offer generous free tiers

🔗 USEFUL LINKS:
- Streamlit Cloud: https://share.streamlit.io
- Render.com: https://render.com
- GitHub: https://github.com
""")

def main():
    if not check_git():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("This helper will guide you through cloud deployment")
    print("=" * 60)
    
    username, repo_name = check_github_account()
    
    print(f"\n📦 Repository: {username}/{repo_name}")
    
    # Git setup
    setup_git_repo(username, repo_name)
    
    # Show deployment steps
    show_deployment_steps()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete! Follow the steps above to deploy.")
    print("=" * 60)

if __name__ == "__main__":
    main()
