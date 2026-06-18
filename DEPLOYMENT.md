# 🚀 FinSight Deployment Guide

## Overview

This guide covers deploying FinSight to production using:
- **Frontend:** Vercel
- **Backend:** Vercel Functions
- **Database:** Qdrant Cloud

---

## Prerequisites

1. **Vercel Account** - https://vercel.com
2. **Qdrant Cloud Account** - https://cloud.qdrant.io
3. **GitHub** - For CI/CD (recommended)
4. **Groq API Key** - Already configured

---

## Step 1: Setup Qdrant Cloud

### 1.1 Create Qdrant Cloud Cluster
1. Go to https://cloud.qdrant.io
2. Sign up / Login
3. Click "Create Cluster"
4. Choose:
   - **Cluster name:** `finsight`
   - **Region:** Choose closest to your users
   - **Tier:** Free tier (for testing)
5. Wait for cluster to be ready

### 1.2 Get Connection Details
1. Click your cluster
2. Copy:
   - **Cluster URL** (looks like: `https://xxxx-eu-west-1-0.ts.cloud.qdrant.io:6333`)
   - **API Key** (long string)

### 1.3 Migrate Data from Local to Cloud

```powershell
cd c:\Users\sathi\finsight
venv\Scripts\activate

# Set environment variables for cloud
$env:QDRANT_URL = "https://YOUR_CLUSTER_ID.eu-west-1-0.ts.cloud.qdrant.io:6333"
$env:QDRANT_API_KEY = "YOUR_API_KEY_HERE"

# Run indexer again (it will upload to cloud)
python backend\ingestion\indexer.py
```

This will upload all 37,170 chunks to Qdrant Cloud.

---

## Step 2: Deploy to Vercel

### 2.1 Prepare Git Repository

```powershell
cd c:\Users\sathi\finsight
git init
git add .
git commit -m "Initial commit - FinSight deployment"
```

### 2.2 Push to GitHub

1. Create new repo on GitHub
2. Push your code:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/finsight.git
git branch -M main
git push -u origin main
```

### 2.3 Deploy to Vercel

1. Go to https://vercel.com/new
2. Import from GitHub repo
3. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `./frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

### 2.4 Add Environment Variables in Vercel

In Vercel dashboard, go to Settings → Environment Variables and add:

```
GROQ_API_KEY = your_groq_key
QDRANT_URL = https://YOUR_CLUSTER_ID.eu-west-1-0.ts.cloud.qdrant.io:6333
QDRANT_API_KEY = your_qdrant_api_key
QDRANT_COLLECTION_NAME = finsight
EMBEDDING_MODEL = BAAI/bge-small-en-v1.5
ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
NEXT_PUBLIC_API_URL = https://your-vercel-app.vercel.app/api
```

### 2.5 Deploy
Click "Deploy" and wait for build to complete.

---

## Step 3: Verify Deployment

### Test API
```powershell
$apiUrl = "https://your-vercel-app.vercel.app/api"

# Test health
curl $apiUrl/health

# Test query
curl -X POST $apiUrl/query `
  -H "Content-Type: application/json" `
  -d '{"question": "What was Apple revenue in 2023?"}'
```

### Test Frontend
Open https://your-vercel-app.vercel.app in browser

---

## Troubleshooting

### Backend not responding
1. Check Vercel Functions logs
2. Verify Qdrant Cloud URL is correct
3. Confirm API key has correct permissions

### Data not found
1. Verify indexing completed to Qdrant Cloud
2. Check collection name matches: `finsight`
3. Confirm point count is 37,170

### CORS errors
1. Update `ALLOWED_ORIGINS` env variable
2. Include exact URL: `https://your-vercel-app.vercel.app`

---

## Local Development

To test locally after deployment changes:

```powershell
# Terminal 1: Backend
cd c:\Users\sathi\finsight
venv\Scripts\activate
uvicorn backend.api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Then open http://localhost:3000

---

## Monitoring & Maintenance

### Check Qdrant Cloud Status
- https://cloud.qdrant.io → Your Cluster

### View Vercel Logs
- https://vercel.com → Project → Deployments → View Logs

### Update Data
To re-index new data to Qdrant Cloud:
1. Update `data/processed/chunks.jsonl`
2. Run `python backend\ingestion\indexer.py` with cloud env vars

---

## Cost Estimation

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Vercel | 100GB bandwidth/mo | Suitable for production |
| Qdrant Cloud | Free tier up to 5M vectors | Handles 37K vectors easily |
| Groq API | Pay-per-use | ~$0.15 per 1M tokens |

---

## Next Steps

1. ✅ Test deployment thoroughly
2. ✅ Set up custom domain (optional)
3. ✅ Configure monitoring/alerts
4. ✅ Plan scaling strategy

For help: https://vercel.com/support
