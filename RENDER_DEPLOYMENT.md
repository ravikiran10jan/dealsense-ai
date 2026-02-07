# DealSense AI - Render.com Deployment Guide

This guide explains how to deploy DealSense AI to Render.com for public access.

## Prerequisites

1. **GitHub Account**: Push your repository to GitHub
2. **Render.com Account**: Sign up at [render.com](https://render.com)
3. **Environment Variables**: Prepare your Azure credentials and API keys

## Deployment Steps

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### Step 2: Connect GitHub to Render.com

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Click **"Connect GitHub"** and authorize Render.com
5. Select your `dealsense-ai` repository

### Step 3: Configure Backend Service

1. **Name**: `dealsense-api`
2. **Environment**: Python 3.10
3. **Build Command**: 
   ```bash
   pip install -r requirements.txt
   ```
4. **Start Command**: 
   ```bash
   uvicorn backend.api:app --host 0.0.0.0 --port $PORT
   ```
5. **Plan**: Free (or Starter for better performance)

### Step 4: Add Environment Variables

In the Render dashboard, add these environment variables for the backend:

```
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
OPENAI_API_VERSION=2024-02-01
OPENAI_MODEL_NAME=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

AZURE_SEARCH_SERVICE_ENDPOINT=your_search_endpoint
AZURE_SEARCH_API_KEY=your_search_key
AZURE_SEARCH_INDEX_NAME=deals-index

FRONTEND_URL=https://your-frontend-url.onrender.com
REDIS_URL=redis://your-redis-url  # Optional, for caching
```

### Step 5: Deploy Frontend

1. Create another Web Service:
   - **Name**: `dealsense-ui`
   - **Environment**: Node.js 18
   - **Build Command**: 
     ```bash
     cd ui/seller_panel && npm install && npm run build
     ```
   - **Start Command**: 
     ```bash
     cd ui/seller_panel && npm start
     ```

2. Add environment variables:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   NODE_ENV=production
   ```

### Step 6: Update CORS in Backend

The backend automatically adds the frontend URL to CORS allowlist if `FRONTEND_URL` is set as an environment variable.

## Deployment Options

### Option A: Using render.yaml (Recommended)

Place `render.yaml` in your repository root. Render will automatically detect and deploy both services.

1. Push the repository
2. Go to Render Dashboard
3. Click **"New +"** → **"Web Service"**
4. Connect your repo
5. Render will read `render.yaml` and deploy both services

### Option B: Manual Configuration

Deploy each service separately through the dashboard.

## Post-Deployment

### Verify Services Are Running

- **Backend API**: `https://your-api.onrender.com/docs` (Swagger UI)
- **Frontend UI**: `https://your-frontend.onrender.com`

### Test the API

```bash
curl -X GET "https://your-api.onrender.com/health"
```

### Troubleshooting

**Backend won't start:**
- Check logs in Render Dashboard
- Verify all required environment variables are set
- Ensure Python version is 3.10+

**Frontend won't connect to backend:**
- Verify `VITE_API_URL` is set correctly
- Check CORS configuration in `backend/api.py`
- Ensure `FRONTEND_URL` is set in backend environment

**Vector store not found:**
- Place pre-built vector store in `backend/vector_store/dealsense_faiss/`
- Or trigger ingestion endpoint after deployment

### Performance Considerations

**Free Tier Limitations:**
- Services spin down after 15 minutes of inactivity
- Cold starts may take 30-60 seconds
- Limited to 0.5 GB RAM

**Upgrade to Starter Plan for:**
- Always-on services
- 1 GB RAM
- Better performance
- Custom domains

## Sharing with Others

Once deployed, share these links:

- **Frontend**: `https://your-frontend.onrender.com`
- **API Docs**: `https://your-api.onrender.com/docs`

No installation required—users can access directly via the browser!

## Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_OPENAI_API_KEY` | OpenAI API authentication | `sk-...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://your-resource.openai.azure.com/` |
| `FRONTEND_URL` | Frontend URL for CORS | `https://your-frontend.onrender.com` |
| `VITE_API_URL` | Backend API URL for frontend | `https://your-api.onrender.com` |
| `REDIS_URL` | Redis connection (optional) | `redis://host:port` |

## Scaling & Monitoring

- Monitor logs in Render Dashboard
- Use health checks to ensure uptime
- Consider upgrading to Starter Plan for production use

---

**Need help?** Check [Render.com Docs](https://render.com/docs) or [DealSense AI Architecture](./docs/architecture.md)
