# 🚀 Deploy DealSense AI to Render.com - Quick Start

Deploy your DealSense AI application live in **5 minutes** with no installation needed!

## What You Get

✅ **Live Frontend** - Accessible via `https://your-app.onrender.com`  
✅ **Live API** - With Swagger documentation  
✅ **Automatic Deployment** - Push to GitHub → Render deploys automatically  
✅ **No Server Management** - Render handles everything  

---

## Quick Deploy Steps

### 1️⃣ Push Code to GitHub

```bash
git add .
git commit -m "Add Render deployment config"
git push origin main
```

### 2️⃣ Sign Up for Render.com

- Go to [render.com](https://render.com)
- Sign up with GitHub (recommended)
- Go to Dashboard

### 3️⃣ Create Backend Service

**Click "New +" → "Web Service"**

| Setting | Value |
|---------|-------|
| **GitHub Repository** | Select `dealsense-ai` |
| **Name** | `dealsense-api` |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.api:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (or Starter for better performance) |

**Click "Create Web Service"**

### 4️⃣ Add Backend Environment Variables

In the Render Dashboard for `dealsense-api`:

1. Go to **Environment**
2. Click **"Add Environment Variable"** for each:

```env
AZURE_OPENAI_API_KEY = your_key_here
AZURE_OPENAI_ENDPOINT = https://your-resource.openai.azure.com/
OPENAI_MODEL_NAME = gpt-4
OPENAI_EMBEDDING_MODEL = text-embedding-ada-002

AZURE_SEARCH_SERVICE_ENDPOINT = https://your-search.search.windows.net
AZURE_SEARCH_API_KEY = your_search_key

FRONTEND_URL = https://dealsense-ui.onrender.com
```

> 💡 Copy your Azure credentials from [Azure Portal](https://portal.azure.com)

### 5️⃣ Create Frontend Service

**Click "New +" → "Web Service"**

| Setting | Value |
|---------|-------|
| **GitHub Repository** | Select `dealsense-ai` |
| **Name** | `dealsense-ui` |
| **Environment** | Node 18 |
| **Build Command** | `cd ui/seller_panel && npm install && npm run build` |
| **Start Command** | `cd ui/seller_panel && npm start` |

### 6️⃣ Add Frontend Environment Variables

1. Go to **Environment**
2. Add:

```env
VITE_API_URL = https://dealsense-api.onrender.com
NODE_ENV = production
```

### 7️⃣ Deploy!

Hit **"Deploy"** button. Render will:
- Pull your code from GitHub
- Install dependencies
- Build and start both services
- Assign public URLs

---

## 🎉 Access Your App

Once deployment completes (5-10 minutes):

- **Frontend**: `https://dealsense-ui.onrender.com`
- **API Docs**: `https://dealsense-api.onrender.com/docs`
- **Share with anyone**: They can use it without installation!

---

## Troubleshooting

### Backend service won't start

1. Check **Logs** in Render Dashboard
2. Verify all environment variables are set
3. Ensure `requirements.txt` has no syntax errors

**Common error**: Missing Azure credentials
```
Solution: Add AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
```

### Frontend shows "Cannot connect to API"

1. Verify `VITE_API_URL` is set to the exact backend URL
2. Check backend service is running (`https://your-api.onrender.com/docs`)
3. Verify `FRONTEND_URL` is set on backend service

### Services keep crashing

**Free tier limitation**: Services spin down after 15 minutes of inactivity

**Solution**: Upgrade to Starter plan (click Service → Settings → Plan)

---

## Using render.yaml (Advanced)

You can also deploy both services automatically using `render.yaml`:

```bash
# Just commit and push - Render reads render.yaml automatically
git push origin main
```

In Render Dashboard:
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo
3. Render will auto-detect `render.yaml` and deploy both services

---

## Sharing with Others

Send them this link:
```
https://dealsense-ui.onrender.com
```

**They can:**
- ✅ Browse deals
- ✅ Search documents
- ✅ Generate insights
- ❌ No installation required
- ❌ No local setup needed

---

## Performance Tips

| Issue | Solution |
|-------|----------|
| Slow startup | Upgrade to Starter Plan |
| Service goes idle | Add a cron job to ping `/health` every 5 min |
| Cold starts (30-60s) | Upgrade to Starter Plan ($7/month) |

---

## Next Steps

1. ✅ Deploy backend
2. ✅ Deploy frontend
3. 🔗 Share URL with team
4. 📊 Monitor in Render Dashboard
5. 🚀 Scale as needed

---

**Questions?** Check [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for full documentation.
