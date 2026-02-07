# 🚀 Render.com Deployment Cheat Sheet

## One-Command Deployment

```bash
# 1. Push to GitHub
git add . && git commit -m "Deploy to Render" && git push origin main

# 2. Go to Render Dashboard and click "New +" → "Web Service"
# 3. Connect GitHub repository
# 4. Set environment variables
# 5. Done! Share the URL
```

---

## Files Created for Render.com

| File | Purpose |
|------|---------|
| `render.yaml` | Auto-deploys both backend and frontend |
| `Procfile` | Specifies how to start the backend |
| `.render-runtime.txt` | Specifies Python version (3.10) |
| `RENDER_DEPLOYMENT.md` | Full deployment documentation |
| `RENDER_QUICK_START.md` | 5-minute quick start guide |
| `DEPLOYMENT_GUIDE.md` | Comprehensive guide with troubleshooting |

---

## Your Public URLs

After deployment:

```
Frontend: https://dealsense-ui.onrender.com
Backend:  https://dealsense-api.onrender.com
API Docs: https://dealsense-api.onrender.com/docs
Health:   https://dealsense-api.onrender.com/api/health
```

---

## Required Environment Variables

### Backend (`dealsense-api`)

```
AZURE_OPENAI_API_KEY = your_key
AZURE_OPENAI_ENDPOINT = https://resource.openai.azure.com/
OPENAI_MODEL_NAME = gpt-4
OPENAI_EMBEDDING_MODEL = text-embedding-ada-002
AZURE_SEARCH_SERVICE_ENDPOINT = https://search.search.windows.net
AZURE_SEARCH_API_KEY = your_key
FRONTEND_URL = https://dealsense-ui.onrender.com
```

### Frontend (`dealsense-ui`)

```
VITE_API_URL = https://dealsense-api.onrender.com
NODE_ENV = production
```

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check `requirements.txt` syntax, view logs |
| Frontend shows blank page | Verify `VITE_API_URL` environment variable |
| Can't connect API | Test health endpoint, check CORS |
| Services keep stopping | Upgrade from free to Starter plan |
| Build takes forever | Upgrade plan for faster build servers |

---

## Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Support**: https://render.com/support
- **Status**: https://status.render.com

---

## Costs

| Plan | Price | Best For |
|------|-------|----------|
| Free | $0/month | Development, testing |
| Starter | $7/month/service | Light production use |
| Standard | $25/month/service | Production workloads |
| Pro | $100/month/service | Enterprise scale |

---

## Share Your App

Send this to users:

```
🎉 Check out DealSense AI!

Frontend: https://dealsense-ui.onrender.com

No installation needed - just open the link!
```

---

## Monitor Your App

```
Logs:        Service → Logs tab
Metrics:     Service → Metrics tab
Events:      Service → Events tab (deployment history)
Environment: Service → Environment tab (edit variables)
Settings:    Service → Settings tab (upgrade plan)
```

---

## Redeploy Latest Code

```bash
# Just push to GitHub - Render auto-redeploys!
git push origin main
```

---

## Rollback to Previous Version

1. Go to Service → **Events**
2. Find previous successful deployment
3. Click **"Redeploy"**

---

That's it! Your app is now live and shareable! 🚀
