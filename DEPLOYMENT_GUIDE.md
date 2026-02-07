# 📦 DealSense AI - Complete Render.com Deployment Guide

This guide provides everything you need to deploy DealSense AI to Render.com for public access.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Deploy (5 minutes)](#quick-deploy)
4. [Detailed Setup](#detailed-setup)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Scaling & Costs](#scaling--costs)

---

## Overview

### What Is Render.com?

Render.com is a cloud platform that hosts web applications. It:
- ✅ Deploys directly from GitHub (auto-redeploy on push)
- ✅ Manages servers (no DevOps needed)
- ✅ Provides free tier for development
- ✅ Scales automatically
- ✅ Gives you public URLs to share

### DealSense AI on Render.com

```
Your GitHub Repo
        ↓
   Render.com
        ↓
   ┌─────────┐
   │ Backend │ ← API at https://api.onrender.com
   │ (Python)│
   └─────────┘
        ↑
   ┌─────────┐
   │Frontend │ ← UI at https://ui.onrender.com
   │ (React) │
   └─────────┘
```

---

## Prerequisites

✅ **GitHub Account** - Repository with your code  
✅ **Render.com Account** - Free signup  
✅ **Azure Credentials** - From Azure Portal  
✅ **5 minutes** - Total setup time

---

## Quick Deploy

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click **"Get Started Free"**
3. Sign up with GitHub (select "Authorize")
4. You'll see the Render Dashboard

### Step 3: Create Backend Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Select your `dealsense-ai` GitHub repository
4. Fill in these fields:

| Field | Value |
|-------|-------|
| Name | `dealsense-api` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.api:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

5. Click **"Create Web Service"**
6. **Wait 2-3 minutes** for deployment (you'll see logs)

### Step 4: Add Backend Environment Variables

1. In the left sidebar, find your `dealsense-api` service
2. Click **"Environment"**
3. Add each variable:

```
AZURE_OPENAI_API_KEY = sk-...
AZURE_OPENAI_ENDPOINT = https://your-resource.openai.azure.com/
OPENAI_MODEL_NAME = gpt-4
OPENAI_EMBEDDING_MODEL = text-embedding-ada-002
AZURE_SEARCH_SERVICE_ENDPOINT = https://your-search.search.windows.net
AZURE_SEARCH_API_KEY = your-key
FRONTEND_URL = https://dealsense-ui.onrender.com
```

4. Service will **auto-redeploy** with new variables

### Step 5: Create Frontend Service

1. Click **"New +"** → **"Web Service"** again
2. Select same repository
3. Fill in:

| Field | Value |
|-------|-------|
| Name | `dealsense-ui` |
| Environment | `Node` |
| Build Command | `cd ui/seller_panel && npm install && npm run build` |
| Start Command | `cd ui/seller_panel && npm start` |
| Instance Type | Free |

### Step 6: Add Frontend Environment Variables

1. Go to **"Environment"** for `dealsense-ui`
2. Add:

```
VITE_API_URL = https://dealsense-api.onrender.com
NODE_ENV = production
```

### Step 7: Access Your App! 🎉

Once both services are deployed:

- **Frontend**: `https://dealsense-ui.onrender.com`
- **API Docs**: `https://dealsense-api.onrender.com/docs` (Swagger)
- **Health Check**: `https://dealsense-api.onrender.com/api/health`

**Share the frontend URL with anyone!**

---

## Detailed Setup

### Getting Azure Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **"Azure OpenAI"**
3. Click your resource → **"Keys and Endpoint"**
4. Copy:
   - **API Key** → `AZURE_OPENAI_API_KEY`
   - **Endpoint** → `AZURE_OPENAI_ENDPOINT`

For Azure AI Search:
1. Search for **"Azure AI Search"** in portal
2. Click your service → **"Keys"**
3. Copy the **Admin Key** → `AZURE_SEARCH_API_KEY`
4. Copy **Endpoint** URL → `AZURE_SEARCH_SERVICE_ENDPOINT`

### Using render.yaml (Alternative)

Instead of manual setup, Render can auto-deploy using `render.yaml`:

**No additional steps needed!** The file is already in your repo.

When you push code:
```bash
git push origin main
```

Render will automatically read `render.yaml` and deploy both services.

---

## Environment Variables

### Required Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI URL | `https://resource.openai.azure.com/` |
| `OPENAI_MODEL_NAME` | LLM model | `gpt-4` |
| `AZURE_SEARCH_SERVICE_ENDPOINT` | Search endpoint | `https://search.search.windows.net` |
| `AZURE_SEARCH_API_KEY` | Search API key | `...` |

### Optional Variables

| Variable | Purpose |
|----------|---------|
| `REDIS_URL` | Caching (if Redis is set up) |
| `LOG_LEVEL` | Logging level (default: INFO) |
| `ENVIRONMENT` | Environment name (production/dev) |

### How to Set Variables on Render

1. Go to service settings
2. Click **"Environment"**
3. Click **"Add Environment Variable"**
4. Enter **Key** and **Value**
5. Click **"Save"**
6. Service auto-redeploys

---

## Post-Deployment

### Verify Everything Works

```bash
# Test backend health
curl https://dealsense-api.onrender.com/api/health

# Expected response:
# {"status":"healthy"}
```

### View Logs

1. Click on service in Render Dashboard
2. Click **"Logs"** tab
3. Watch real-time logs as app runs

### Check Deployment Status

1. Click on service
2. Look at **"Events"** tab
3. See deployment history

---

## Troubleshooting

### Backend Won't Start

**Error in logs**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Ensure `requirements.txt` is up to date
```bash
pip freeze > requirements.txt
git push
```

---

### Missing Environment Variables

**Error**: `KeyError: 'AZURE_OPENAI_API_KEY'`

**Solution**: 
1. Go to backend service → Environment
2. Add the missing variable
3. Service will redeploy automatically

---

### Frontend Can't Connect to API

**Symptom**: "Cannot fetch from backend"

**Solution**:
1. Verify `VITE_API_URL` is set to exact backend URL
2. Check backend service is running (test `/api/health`)
3. Ensure `FRONTEND_URL` is set on backend (for CORS)

---

### Service Keeps Crashing

**Reason**: Free tier services spin down after 15 minutes of inactivity

**Solutions**:
- **Option 1**: Add a health check cron job
- **Option 2**: Upgrade to Starter plan ($7/month)

---

### Build Takes Too Long

**Reason**: Installing dependencies is slow on free tier

**Solution**: Upgrade to Starter or Professional plan

---

## Scaling & Costs

### Free Tier

- ✅ Always on (if auto-spinning disabled)
- ✅ Spins down after 15 min of inactivity
- ✅ Cold starts: 30-60 seconds
- ✅ 0.5 GB RAM
- ✅ Shared CPU

**Cost**: Free (1 service)

### Starter Plan

- ✅ Always on (no spin down)
- ✅ 1 GB RAM
- ✅ Dedicated CPU
- ✅ No cold starts
- ✅ Custom domain

**Cost**: $7/month per service ($14 for both)

### Upgrade Steps

1. Click service → Settings
2. Look for "Plan" section
3. Click **"Upgrade"**
4. Select **"Starter"**
5. Confirm payment

---

## Monitoring & Maintenance

### Monitor Performance

1. Go to service → **"Metrics"**
2. View:
   - CPU usage
   - Memory usage
   - Requests per second
   - Errors

### Set Up Alerts

1. Click service → **"Notifications"**
2. Enable email alerts for:
   - Failed deployments
   - Service crashes
   - High memory usage

### Update Code

Just push to GitHub:
```bash
git push origin main
```

Render automatically redeploys!

---

## Sharing with Your Team

### Share These Links

- **Frontend**: `https://dealsense-ui.onrender.com`
- **API Docs**: `https://dealsense-api.onrender.com/docs`

### What They Can Do

✅ Browse all deals  
✅ Search documents  
✅ Get AI insights  
✅ Generate talking points  
✅ View credible references  

**All without installing anything!**

---

## Advanced: Custom Domain

To use your own domain (e.g., `dealsense.yourcompany.com`):

1. Click service → **"Settings"**
2. Look for **"Custom Domains"**
3. Add your domain
4. Update DNS records (instructions provided)
5. Render handles SSL automatically

---

## FAQ

### Q: Can I use the free tier in production?

**A**: Not recommended. Services spin down after 15 minutes. Use Starter plan for production.

### Q: How do I debug issues?

**A**: Check **Logs** and **Events** tabs in Render Dashboard. They show all errors and deployment details.

### Q: Can I deploy multiple branches?

**A**: Yes! Create a new Web Service for each branch. Each gets its own URL.

### Q: How do I rollback to a previous version?

**A**: Go to **Events** tab, find the previous deployment, click **"Redeploy"**.

### Q: Is data persistent?

**A**: Not in `/tmp`. Use blob storage (Azure) for persistent data.

---

## Next Steps

1. ✅ Deploy backend
2. ✅ Deploy frontend
3. ✅ Test on Render URLs
4. ✅ Share with team
5. ✅ Monitor in dashboard
6. 🚀 Celebrate! 🎉

---

**Questions?** Check [render.com/docs](https://render.com/docs) or the [Render Support](https://render.com/support) page.

**Ready to deploy?** Follow the [Quick Deploy](#quick-deploy) section!
