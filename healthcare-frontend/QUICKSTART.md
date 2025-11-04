# Healthcare Assistant Frontend - Quick Start Guide

Get your frontend up and running in 5 minutes!

## Step 1: Navigate to Frontend Directory

```bash
cd healthcare-frontend
```

## Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Backend URL

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
# For local development, set:
# BACKEND_API_URL=http://localhost:8080
```

**On Windows:**
```bash
copy .env.example .env
notepad .env
```

## Step 5: Start Backend (If Not Running)

In a separate terminal:

```bash
# Go back to main project
cd ..

# Start backend
python main.py
```

Backend should be running at: http://localhost:8080

## Step 6: Run Frontend

```bash
# In healthcare-frontend directory
streamlit run app.py
```

The app will open automatically in your browser at: http://localhost:8501

## Step 7: Login

Use demo credentials:

- **Username**: `demo`
- **Password**: `demo123`

## Step 8: Start Chatting

1. Click **💬 Chat** in the sidebar
2. Type a message like: "I have a headache and fever"
3. Wait for Dr. Cloud's response
4. Continue the conversation!

## Common Issues

### Backend Connection Error

**Problem**: Frontend can't connect to backend

**Solution**:
1. Make sure backend is running: `curl http://localhost:8080/health`
2. Check `.env` file has correct `BACKEND_API_URL`
3. Restart frontend

### Import Errors

**Problem**: ModuleNotFoundError

**Solution**:
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

**Problem**: Port 8501 is busy

**Solution**:
```bash
# Use different port
streamlit run app.py --server.port 8502
```

## Deploy to Cloud Run

### Prerequisites
1. Backend deployed to Cloud Run
2. Backend URL (e.g., https://backend-abc123-uc.a.run.app)

### Deploy Frontend

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy (replace with your backend URL)
./deploy.sh --backend-url https://your-backend-url
```

**Or manually:**

```bash
export PROJECT_ID="your-project-id"
export BACKEND_URL="https://your-backend-url"

gcloud builds submit --tag gcr.io/${PROJECT_ID}/healthcare-frontend

gcloud run deploy healthcare-frontend \
  --image gcr.io/${PROJECT_ID}/healthcare-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "BACKEND_API_URL=${BACKEND_URL}"
```

## Next Steps

- [ ] Customize branding in `config/settings.py`
- [ ] Add more users in `config/users.yaml`
- [ ] Explore chat interface features
- [ ] Test different health queries
- [ ] Deploy to Cloud Run

## Need Help?

- Check [README.md](README.md) for full documentation
- Review backend [DEPLOYMENT.md](../DEPLOYMENT.md)
- Check Cloud Run logs if deployed

---

**Happy chatting with Dr. Cloud! 🏥**
