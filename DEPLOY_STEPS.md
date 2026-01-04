# Steps to Deploy Fixed Backend to Railway

## The Issue
You're getting a 500 error because Railway is still running the OLD code without my fixes.

## How to Deploy the Fixes

### Option 1: Push from Your Local Machine (Recommended)

If you have the Railway project connected to a Git repository:

```bash
# Navigate to your backend folder
cd backend

# Add all changes
git add .

# Commit with a descriptive message
git commit -m "Fix: Add error handling and reduce dependencies for Railway"

# Push to your repository
git push

# Railway will automatically detect the push and redeploy
```

### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI if you haven't
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project (if not already linked)
railway link

# Deploy from the backend directory
cd backend
railway up
```

### Option 3: Redeploy from Railway Dashboard

1. Go to your Railway dashboard
2. Find your Jarvis backend project
3. Click on the deployment
4. Click "Deploy" to trigger a new deployment
5. Railway will pull the latest code and redeploy

## What to Check After Deployment

1. **Check Railway Logs**:
   - Go to Railway dashboard
   - Click on your project
   - View the deployment logs
   - Look for: "✅ Jarvis is ready!"
   - Or warnings about module initialization

2. **Test Health Endpoint**:
   ```
   https://jarvis-production-5709a.up.railway.app/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "orchestrator_ready": true,
     "modules": {
       "nlp": true,
       "cv": true,
       "text_to_3d": true,
       "scene_builder": true
     }
   }
   ```

3. **Test API Endpoint**:
   ```
   https://jarvis-production-5709a.up.railway.app/api/test
   ```
   Should return:
   ```json
   {
     "status": "ok",
     "message": "API is responding",
     "endpoint": "/api/test"
   }
   ```

4. **Try Your Frontend**:
   - Once health checks pass, try the frontend
   - Send a command like "Create a red cube"
   - It should work without 500 errors

## Files That Were Changed

These files have been updated with fixes:

- `backend/main.py` - Better initialization and CORS
- `backend/core/orchestrator.py` - Error handling for all modules
- `backend/api/routes.py` - Enhanced logging and test endpoint
- `backend/requirements-railway.txt` - Reduced dependencies

## If It Still Fails

Check the Railway logs for specific errors. The enhanced logging will show:
- Which modules failed to initialize
- Exact error messages with stack traces
- Request processing details

Common issues:
- Missing Python dependencies (check requirements-railway.txt is used)
- Memory limits exceeded (removed heavy ML libs to fix this)
- Startup timeout (improved initialization to prevent this)
