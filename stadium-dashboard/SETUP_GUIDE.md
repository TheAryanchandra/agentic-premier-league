# 🚀 Stadium Dashboard - 45 Min Complete Setup Guide

## STEP 0: Prerequisites (5 mins)

### Install Required Tools
```bash
# Check if you have these installed
python --version          # Should be 3.8+
node --version           # Should be 16+
gcloud --version         # Google Cloud CLI

# If you don't have gcloud:
# Download from: https://cloud.google.com/sdk/docs/install
```

### Get Your Firebase Credentials
1. Go to: https://console.firebase.google.com
2. Click "Create Project" → Name it "stadium-dashboard"
3. Enable Firestore Database (free tier)
4. Go to Settings → Service Accounts
5. Click "Generate New Private Key"
6. Save as `firebase-key.json` in your project root

---

## STEP 1: Local Setup & Testing (0-15 mins)

### 1.1 Create Project Structure
```bash
mkdir stadium-dashboard
cd stadium-dashboard

# Create folders
mkdir backend frontend
```

### 1.2 Copy Backend Files
```bash
# Copy the FastAPI code (main.py from above)
# Place in: stadium-dashboard/backend/main.py

# Copy requirements.txt
# Place in: stadium-dashboard/backend/requirements.txt

# Copy your firebase-key.json
# Place in: stadium-dashboard/backend/firebase-key.json
```

### 1.3 Setup Backend Locally
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test run (without Firebase, will use mock data)
python main.py
```

**If successful, you should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 1.4 Test API in Browser
```
http://localhost:8000/docs    # OpenAPI docs
http://localhost:8000/health  # Health check
http://localhost:8000/density # Get current density (mock data)
```

✅ **If this works, Backend is ready!**

---

## STEP 2: Frontend Setup (15-25 mins)

### 2.1 Copy Frontend Files
```bash
cd ../frontend

# Copy the HTML file (index.html from above)
# Place in: stadium-dashboard/frontend/index.html
```

### 2.2 Install Frontend Dependencies
```bash
# Create package.json
cat > package.json << 'EOF'
{
  "name": "stadium-dashboard",
  "version": "1.0.0",
  "scripts": {
    "dev": "python -m http.server 3000",
    "build": "echo 'Static build complete'"
  }
}
EOF

# Install http server
pip install http.server
```

### 2.3 Test Frontend Locally
```bash
# Start frontend server
python -m http.server 3000

# Open in browser
http://localhost:3000
```

**You should see:**
- Stadium Experience Dashboard title
- 6 zone cards with density
- Admin panel to update crowd counts
- Real-time refresh every 5 seconds

✅ **If this works, Frontend is ready!**

---

## STEP 3: Test Full Stack Locally (25-35 mins)

### 3.1 Keep Backend Running
```bash
# In terminal 1 - Backend
cd backend
python main.py
# Runs on http://localhost:8000
```

### 3.2 Start Frontend
```bash
# In terminal 2 - Frontend
cd frontend
python -m http.server 3000
# Opens at http://localhost:3000
```

### 3.3 Test Complete Flow
1. Open http://localhost:3000 in browser
2. You should see all zones with crowd data
3. Go to Admin Panel
4. Select a zone (e.g., "North Stand")
5. Enter a number (e.g., "3000")
6. Click "Update"
7. Watch the card update in real-time

✅ **If this works, Full Stack is ready!**

---

## STEP 4: Deploy to Cloud Run (35-45 mins)

### 4.1 Setup Google Cloud Project
```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Initialize gcloud
gcloud init

# Set default project
gcloud config set project $PROJECT_ID
```

### 4.2 Enable Required APIs
```bash
gcloud services enable \
  cloudrun.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

### 4.3 Build & Push Docker Image
```bash
cd backend

# Build Docker image
docker build -t stadium-api:latest .

# Tag for Google Cloud
docker tag stadium-api:latest gcr.io/$PROJECT_ID/stadium-api:latest

# Configure Docker auth
gcloud auth configure-docker

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/stadium-api:latest
```

### 4.4 Deploy Backend to Cloud Run
```bash
gcloud run deploy stadium-api \
  --image=gcr.io/$PROJECT_ID/stadium-api:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --timeout=3600

# Note the URL: https://stadium-api-xxxxx.run.app
```

### 4.5 Deploy Frontend to Cloud Storage (Static Site)
```bash
cd ../frontend

# Create Cloud Storage bucket
gsutil mb gs://$PROJECT_ID-stadium-dashboard/

# Upload frontend
gsutil -m cp index.html gs://$PROJECT_ID-stadium-dashboard/

# Make it public
gsutil iam ch allUsers:objectViewer gs://$PROJECT_ID-stadium-dashboard/

# Configure for static site
gsutil web set -m index.html gs://$PROJECT_ID-stadium-dashboard/

# Get URL
echo "Frontend deployed at:"
echo "https://storage.googleapis.com/$PROJECT_ID-stadium-dashboard/index.html"
```

### 4.6 Update Frontend API URL
Edit your `index.html` and change:
```javascript
const API_URL = 'https://stadium-api-xxxxx.run.app'  // Your Cloud Run URL
```

Redeploy:
```bash
gsutil -m cp index.html gs://$PROJECT_ID-stadium-dashboard/
```

✅ **Your dashboard is now live!**

---

## STEP 5: Test Production (40-45 mins)

### 5.1 Verify API
```bash
curl https://stadium-api-xxxxx.run.app/health
# Should return: {"status":"healthy","timestamp":"..."}
```

### 5.2 Verify Frontend
Open in browser:
```
https://storage.googleapis.com/$PROJECT_ID-stadium-dashboard/index.html
```

### 5.3 Test Full Flow
1. Open the production frontend URL
2. Staff panel should work
3. Try updating a zone
4. Should update in real-time

✅ **Everything is live!**

---

## Quick Reference: Important URLs

| Component | URL |
|-----------|-----|
| Backend API | `https://stadium-api-xxxxx.run.app` |
| API Docs | `https://stadium-api-xxxxx.run.app/docs` |
| Frontend | `https://storage.googleapis.com/$PROJECT_ID-stadium-dashboard/index.html` |
| Firebase Console | https://console.firebase.google.com |
| GCP Console | https://console.cloud.google.com |

---

## Cost Estimate (45 mins → Full Event)

- **Cloud Run**: ~₹5-15 (backend)
- **Cloud Storage**: Free tier (frontend)
- **Firebase**: Free tier (25k reads/day)
- **Total**: ₹5-15 for entire 5-hour IPL match

✅ **Within your $5 credit!**

---

## Troubleshooting

### "Firebase not initialized"
- Make sure `firebase-key.json` is in the backend folder
- The app will still work with mock data if Firebase isn't configured

### "API not responding"
- Check if backend is running: `curl http://localhost:8000/health`
- Check Cloud Run logs: `gcloud run logs stadium-api --region=$REGION`

### "Frontend can't reach API"
- Make sure API_URL in index.html is correct
- Check CORS is enabled (it is by default in main.py)

### "Docker build fails"
- Make sure you're in the `backend` directory
- Ensure `firebase-key.json` exists
- Run `pip install -r requirements.txt` locally first

---

## Next Steps (After 45 mins)

1. **Add real data**: Replace mock data with actual stadium sensor data
2. **Add Firebase**: Uncomment Firestore code for persistent storage
3. **Add alerts**: Staff can create emergency alerts
4. **Add more zones**: Customize for your specific venue
5. **Mobile app**: Use same API for iOS/Android

---

## Files Checklist

- ✅ `backend/main.py` - FastAPI backend
- ✅ `backend/requirements.txt` - Dependencies
- ✅ `backend/Dockerfile` - Docker config
- ✅ `backend/firebase-key.json` - Firebase credentials
- ✅ `frontend/index.html` - React dashboard
- ✅ `README.md` - This file

---

**Ready? Start with Step 0 and go! You'll be live in 45 minutes.** 🚀
