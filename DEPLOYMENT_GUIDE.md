# Streamlit Cloud Deployment Guide

## 🚀 HOW TO DEPLOY

### **Option 1: Deploy on Streamlit Cloud (FREE & EASIEST)**

#### Prerequisites:
1. GitHub account (https://github.com)
2. Streamlit Cloud account (https://share.streamlit.io)

#### Steps:

**Step 1: Push to GitHub**
```bash
# Initialize git repo (if not already)
cd c:\Users\YASH BINEKAR\OneDrive\Desktop\Pictures\Saved Pictures\EnterPrise_agent
git init
git add .
git commit -m "Initial commit - Enterprise AI Automation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/enterprise-ai-agent.git
git push -u origin main
```

**Step 2: Create `.streamlit/secrets.toml`**
Create this file in your project:
```
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_api_key_here"
TAVILY_API_KEY = "your_tavily_key_here"
```

**Step 3: Deploy on Streamlit Cloud**
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Set main file path to: `ui/dashboard.py`
5. Click Deploy
6. Add secrets in Settings → Secrets

#### Important Notes:
- Streamlit Cloud will run `ui/dashboard.py` as the main app
- The FastAPI backend MUST be accessible via HTTPS URL (currently running locally)
- You need to deploy the FastAPI backend to a cloud service too

---

### **Option 2: Deploy Both Frontend & Backend (RECOMMENDED)**

For full functionality, you need:
1. **Streamlit UI** → Streamlit Cloud (FREE)
2. **FastAPI Backend** → Render.com, Heroku, Railway, etc.

#### **Step 2a: Deploy FastAPI to Render (FREE)**

**Create `render.yaml` in project root:**
```yaml
services:
  - type: web
    name: enterprise-ai-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        scope: build
        sync: false
      - key: TAVILY_API_KEY
        scope: build
        sync: false
      - key: REDIS_URL
        value: "redis://localhost:6379"
      - key: PORT
        value: "8000"
```

1. Create Render account: https://render.com
2. Connect GitHub repo
3. Deploy as Web Service
4. Copy the deployment URL (e.g., `https://enterprise-ai-api.onrender.com`)
5. Update `ui/dashboard.py` line 15 to use this URL

---

### **Option 3: Docker + Any Cloud Provider (PRODUCTION)**

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD streamlit run ui/dashboard.py --server.port=8501 &\
    uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Deploy to: AWS, Azure, GCP, Railway, etc.

---

## 📝 CONFIGURATION CHANGES NEEDED

### **Update UI to use Cloud API URL**

Edit `ui/dashboard.py` line 15:
```python
# LOCAL (current)
API_URL = "http://localhost:8000/api/tasks"

# CLOUD (change to your deployed backend URL)
API_URL = "https://enterprise-ai-api.onrender.com/api/tasks"
```

---

## ✅ QUICKEST DEPLOYMENT (5 minutes)

1. Push code to GitHub
2. Deploy Streamlit UI on Streamlit Cloud
3. Deploy FastAPI on Render.com
4. Update API URL in dashboard.py
5. Done! Anyone can access your app

---

## 🔐 SECRETS MANAGEMENT

**On Streamlit Cloud:**
1. Deploy app
2. Go to Settings → Secrets
3. Paste secrets in TOML format:
```toml
GEMINI_API_KEY = "your_key"
TAVILY_API_KEY = "your_key"
REDIS_URL = "redis://localhost:6379"
```

---

## 📊 ESTIMATED COSTS

| Service | Cost | Notes |
|---------|------|-------|
| Streamlit Cloud | FREE | Up to 1GB RAM |
| Render.com | FREE | Spins down after 15 min inactivity |
| Heroku | $7/month | Always running |
| Railway | $5/month | Pay-as-you-go |

---

## 🎯 DEPLOYMENT CHECKLIST

- [ ] Code pushed to GitHub
- [ ] `.streamlit/secrets.toml` created
- [ ] Streamlit Cloud app deployed
- [ ] FastAPI backend deployed (Render/Heroku/etc)
- [ ] API URL updated in `ui/dashboard.py`
- [ ] Secrets configured on Streamlit Cloud
- [ ] Test with public URL
- [ ] Share link with team!

---

## 🚀 YOUR PUBLIC URL WILL BE

```
https://your-username-enterprise-ai-agent.streamlit.app
```

Anyone can visit this URL to use your AI automation system!
