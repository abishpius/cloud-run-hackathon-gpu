# Healthcare Assistant - Cloud Run Deployment Guide

This guide explains how to deploy the Healthcare Assistant agent as a Cloud Run backend service.

## Overview

The Healthcare Assistant is built using:
- **Google ADK (Agent Development Kit)**: Multi-agent orchestration framework
- **FastAPI**: High-performance Python web framework
- **Cloud Run**: Serverless container platform

## Architecture

### Main Components

1. **main.py**: FastAPI application with RESTful endpoints
2. **Healthcare_Assistant/**: Agent system with orchestrator and sub-agents
   - Dr. Cloud (root agent/orchestrator)
   - Symptom Analysis Agent
   - Lab Results Interpreter Agent
   - Medication Interaction Agent
   - Lifestyle Recommendations Agent
   - Specialist Referral Agent
   - Clinical Documentation Agent

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/health` | Health check for Cloud Run |
| POST | `/api/v1/session/new` | Create new session |
| POST | `/api/v1/chat` | Send message (non-streaming) |
| POST | `/api/v1/chat/stream` | Send message (streaming SSE) |
| GET | `/api/v1/session/state` | Get session state |
| DELETE | `/api/v1/session` | Delete session |

## Local Development

### Prerequisites

- Python 3.11+
- Google Cloud account with Vertex AI enabled
- Required environment variables (see `.env` file)

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp Healthcare_Assistant/.env .env
   # Edit .env with your configuration
   ```

3. **Run locally**:
   ```bash
   python main.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

4. **Test the API**:
   ```bash
   # Health check
   curl http://localhost:8080/health

   # Create new session
   curl -X POST http://localhost:8080/api/v1/session/new \
     -H "Content-Type: application/json" \
     -d '{}'

   # Send message
   curl -X POST http://localhost:8080/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "session_id": "session_456",
       "message": "I have a headache and fever"
     }'
   ```

## Cloud Run Deployment

### Method 1: Ollama MedGemma Deployment with GPU

This method deploys the Healthcare Assistant using Ollama's MedGemma model on Cloud Run with NVIDIA L4 GPU acceleration.

#### Prerequisites

- Google Cloud project with billing enabled
- GPU quota in your region (NVIDIA L4)
- gcloud CLI installed and configured
- Cloud Storage bucket for model files

#### Step 1: Install Ollama and Set Up MedGemma Model

If you haven't already set up the MedGemma model, follow these steps in Cloud Shell:

**1.1 Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**1.2 Pull the MedGemma model:**
```bash
ollama pull alibayram/medgemma
```

**1.3 Create a custom model:**

Create a file named `medgemma-modelfile` with the following content:
```
FROM alibayram/medgemma
```

Then create the custom model:
```bash
ollama create medgemma-custom -f medgemma-modelfile
```

**1.4 Set up your GCS bucket:**
```bash
# Set your GCS bucket name
export BUCKET_NAME=ap-medgemma

# Create the GCS bucket (if it doesn't exist)
gsutil mb gs://${BUCKET_NAME}
```

**1.5 Upload model files to Cloud Storage:**
```bash
# Navigate to Ollama models directory
cd /usr/share/ollama/.ollama/models

# Upload all model files to GCS
gsutil -m cp -r . gs://${BUCKET_NAME}/
```

#### Step 2: Build and Push Container Image

```bash
# Build the container image with Cloud Build
gcloud builds submit --tag gcr.io/hackathons-461900/ollama-medgemma-adk
```

This command will:
- Build the Docker image defined in your Dockerfile
- Push it to Google Container Registry
- Make it available for Cloud Run deployment

#### Step 3: Deploy to Cloud Run with GPU

```bash
gcloud run deploy medgemma-service \
  --image gcr.io/hackathons-461900/ollama-medgemma-adk \
  --concurrency 4 \
  --cpu 8 \
  --gpu 1 \
  --gpu-type nvidia-l4 \
  --max-instances 1 \
  --memory 32Gi \
  --allow-unauthenticated \
  --no-cpu-throttling \
  --timeout=600 \
  --region us-central1 \
  --add-volume name=model-vol,type=cloud-storage,bucket=ap-medgemma \
  --add-volume-mount volume=model-vol,mount-path=/models \
  --set-env-vars OLLAMA_MODELS=/ollama-models,GOOGLE_CLOUD_PROJECT=hackathons-461900,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=1,ROOT_MODEL=gemini-2.5-flash,SYMPTOM_AGENT_MODEL=gemini-2.5-flash,DOCUMENTATION_AGENT_MODEL=gemini-2.5-flash,LIFESTYLE_AGENT_MODEL=gemini-2.5-flash,MEDICAL_LABS_AGENT_MODEL=gemini-2.5-flash,MEDICATIONS_AGENT_MODEL=gemini-2.5-flash,SPECIALIST_AGENT_MODEL=gemini-2.5-flash,AGENT_PATH=./Healthcare_Assistant,SERVICE_NAME=healthcare-assistant-agent-service,APP_NAME=healthcare-assistant-app,FIRESTORE_COLLECTION=healthcare-assistant,OLLAMA_API_BASE=http://localhost:11434
```

#### Deployment Configuration Details

| Parameter | Value | Description |
|-----------|-------|-------------|
| `--concurrency` | 4 | Max concurrent requests per instance (GPU memory constraint) |
| `--cpu` | 8 | Number of vCPUs for optimal performance |
| `--gpu` | 1 | Number of GPUs per instance |
| `--gpu-type` | nvidia-l4 | GPU type (NVIDIA L4 for inference) |
| `--max-instances` | 1 | Maximum instances (adjust based on GPU quota) |
| `--memory` | 32Gi | Memory allocation for model loading |
| `--no-cpu-throttling` | - | Disable CPU throttling for consistent performance |
| `--timeout` | 600 | Request timeout in seconds (10 minutes) |
| `--add-volume` | GCS bucket | Mount Cloud Storage bucket containing model files |
| `--add-volume-mount` | /models | Mount path inside container |

#### Environment Variables for Ollama Deployment

| Variable | Value | Purpose |
|----------|-------|---------|
| `OLLAMA_MODELS` | /ollama-models | Directory for Ollama model storage |
| `OLLAMA_API_BASE` | http://localhost:11434 | Ollama API endpoint |
| `GOOGLE_CLOUD_PROJECT` | hackathons-461900 | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | us-central1 | GCP region |
| `ROOT_MODEL` | gemini-2.5-flash | Model for root agent (can use Ollama or Vertex AI) |
| `*_AGENT_MODEL` | gemini-2.5-flash | Models for sub-agents |

#### Step 4: Verify Deployment

After deployment completes, test your service:

```bash
# Get the service URL
gcloud run services describe medgemma-service --region us-central1 --format 'value(status.url)'

# Test health endpoint
curl https://YOUR-SERVICE-URL/health

# Create a session
curl -X POST https://YOUR-SERVICE-URL/api/v1/session/new \
  -H "Content-Type: application/json"

# Send a medical query
curl -X POST https://YOUR-SERVICE-URL/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_test",
    "session_id": "session_test",
    "message": "I have a persistent cough and fever for 3 days"
  }'
```

### Method 2: Using gcloud CLI (Standard Vertex AI Deployment)

1. **Set environment variables**:
   ```bash
   export PROJECT_ID="hackathons-461900"
   export REGION="us-central1"
   export SERVICE_NAME="healthcare-assistant-agent-service"
   ```

2. **Build and deploy**:
   ```bash
   # Build container with Cloud Build
   gcloud builds submit --tag gcr.io/${GOOGLE_CLOUD_PROJECT}/${SERVICE_NAME}

   # Deploy to Cloud Run
   gcloud run deploy ${SERVICE_NAME} \
     --image gcr.io/${GOOGLE_CLOUD_PROJECT}/${SERVICE_NAME} \
     --platform managed \
     --region ${GOOGLE_CLOUD_LOCATION} \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --max-instances 2 \
     --set-env-vars "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},GOOGLE_GENAI_USE_VERTEXAI=1,ROOT_MODEL=gemini-2.5-flash,APP_NAME=healthcare-assistant-app"
   ```

### Method 2: Using Cloud Console

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click "Create Service"
3. Select "Continuously deploy from a repository" or "Deploy one revision from an existing container image"
4. Configure:
   - **Container image**: `gcr.io/PROJECT_ID/SERVICE_NAME`
   - **Region**: us-central1
   - **Authentication**: Allow unauthenticated invocations (or configure as needed)
   - **Memory**: 2 GiB
   - **CPU**: 2
   - **Maximum instances**: 10
   - **Request timeout**: 300 seconds

5. Add environment variables:
   ```
   GOOGLE_CLOUD_PROJECT=hackathons-461900
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=1
   ROOT_MODEL=gemini-2.5-flash
   SYMPTOM_AGENT_MODEL=gemini-2.5-flash
   DOCUMENTATION_AGENT_MODEL=gemini-2.5-flash
   LIFESTYLE_AGENT_MODEL=gemini-2.5-flash
   MEDICAL_LABS_AGENT_MODEL=gemini-2.5-flash
   MEDICATIONS_AGENT_MODEL=gemini-2.5-flash
   SPECIALIST_AGENT_MODEL=gemini-2.5-flash
   APP_NAME=healthcare-assistant-app
   FIRESTORE_COLLECTION=healthcare-assistant
   ```

6. Click "Create"

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | hackathons-461900 |
| `GOOGLE_CLOUD_LOCATION` | GCP region | us-central1 |
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI | 1 |
| `ROOT_MODEL` | Root agent model | gemini-2.5-flash |
| `APP_NAME` | Application name | healthcare-assistant-app |
| `PORT` | Server port | 8080 (default) |

### Optional Environment Variables

Additional agent-specific model configurations:
- `SYMPTOM_AGENT_MODEL`
- `DOCUMENTATION_AGENT_MODEL`
- `LIFESTYLE_AGENT_MODEL`
- `MEDICAL_LABS_AGENT_MODEL`
- `MEDICATIONS_AGENT_MODEL`
- `SPECIALIST_AGENT_MODEL`

## Usage Examples

### Python Client

```python
import requests
import json

BASE_URL = "https://healthcare-assistant-agent-service-HASH-uc.a.run.app"

# Create session
response = requests.post(f"{BASE_URL}/api/v1/session/new")
session_data = response.json()
user_id = session_data["user_id"]
session_id = session_data["session_id"]

# Send message
chat_response = requests.post(
    f"{BASE_URL}/api/v1/chat",
    json={
        "user_id": user_id,
        "session_id": session_id,
        "message": "I have a persistent cough and slight fever for 3 days"
    }
)

print(chat_response.json()["response"])

# Get session state
state_response = requests.get(
    f"{BASE_URL}/api/v1/session/state",
    params={"user_id": user_id, "session_id": session_id}
)
print(state_response.json())
```

### JavaScript/Node.js Client

```javascript
const BASE_URL = "https://healthcare-assistant-agent-service-HASH-uc.a.run.app";

// Create session
const sessionResponse = await fetch(`${BASE_URL}/api/v1/session/new`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
});

const { user_id, session_id } = await sessionResponse.json();

// Send message
const chatResponse = await fetch(`${BASE_URL}/api/v1/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id,
    session_id,
    message: "I have a persistent cough and slight fever for 3 days"
  })
});

const result = await chatResponse.json();
console.log(result.response);
```

### Streaming Example

```python
import requests
import json

BASE_URL = "https://your-service-url"

# Stream events
response = requests.post(
    f"{BASE_URL}/api/v1/chat/stream",
    json={
        "user_id": user_id,
        "session_id": session_id,
        "message": "What medications interact with aspirin?"
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            event_data = json.loads(line[6:])
            print(f"Event: {event_data['type']}, Content: {event_data['content']}")
```

## Monitoring

### Cloud Run Metrics

Monitor your service in the Cloud Console:
- Request count and latency
- Container instance count
- CPU and memory utilization
- Error rates

### Logging

View logs in Cloud Logging:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}" --limit 50
```

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check environment variables are set correctly
   - Verify Vertex AI API is enabled
   - Check service account permissions

2. **Timeout errors**
   - Increase request timeout in Cloud Run settings
   - Optimize agent prompts for faster responses
   - Consider async/streaming endpoints for long operations

3. **Memory issues**
   - Increase memory allocation (2Gi recommended minimum)
   - Monitor memory usage in Cloud Run metrics

4. **Authentication errors**
   - Ensure service account has Vertex AI User role
   - Verify GOOGLE_CLOUD_PROJECT is set correctly

### Ollama-Specific Troubleshooting

1. **GPU quota errors**
   - Check your GPU quota in the GCP Console: IAM & Admin > Quotas
   - Request quota increase for "NVIDIA L4 GPUs" in your region
   - Typical quota: 0-1 GPUs by default, may need to request more

2. **Model not loading from GCS**
   - Verify the GCS bucket exists: `gsutil ls gs://ap-medgemma`
   - Check bucket permissions: Service account needs Storage Object Viewer role
   - Verify model files were uploaded correctly
   - Check Cloud Run logs for mount errors

3. **Ollama server not starting**
   - Check Dockerfile has Ollama installation steps
   - Verify OLLAMA_API_BASE is set to `http://localhost:11434`
   - Check that the startup script starts Ollama before the FastAPI app
   - View logs: `gcloud run services logs read medgemma-service --limit 100`

4. **High memory usage / OOM errors**
   - MedGemma model requires significant memory (8-16GB+ for the model)
   - Ensure memory is set to at least 32Gi
   - Reduce concurrency if memory issues persist
   - Monitor memory: `gcloud monitoring timeseries list --filter metric.type="run.googleapis.com/container/memory/utilization"`

5. **Slow inference / cold starts**
   - First request may take 30-60 seconds as model loads into GPU memory
   - Consider using min-instances=1 to keep service warm (costs more)
   - Cold start time: ~60-90 seconds with GPU and large model
   - Warm requests: ~2-5 seconds depending on query complexity

6. **Volume mount issues**
   - Ensure the GCS bucket name is correct in the deploy command
   - Verify the mount path `/models` is accessible
   - Check Cloud Run logs for mount-related errors
   - Service account needs `storage.objectViewer` role on the bucket

7. **Model compatibility issues**
   - Ensure you're using the correct model name: `medgemma-custom`
   - Verify model was created with: `ollama create medgemma-custom -f medgemma-modelfile`
   - Check model exists in Ollama: `ollama list` (during setup)
   - Model files must be in GGUF or Ollama's native format

## Security Considerations

1. **Authentication**: Consider adding authentication middleware for production
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Data Privacy**: Healthcare data is sensitive - ensure compliance with HIPAA/regulations
4. **Environment Variables**: Use Secret Manager for sensitive configuration
5. **CORS**: Configure CORS appropriately for your frontend domains

## Performance Considerations

### Ollama MedGemma with GPU
- **Cold Start**: 60-90 seconds (model loading + GPU initialization)
- **Warm Request**: 2-5 seconds (depending on query complexity)
- **Concurrent Requests**: 4 max (GPU memory constraint)
- **Cost**: ~$0.50-1.00/hour for L4 GPU + compute + storage
- **Best For**: Medical-specific queries requiring domain expertise

### Standard Vertex AI Deployment
- **Cold Start**: 3-5 seconds
- **Warm Request**: 1-3 seconds
- **Concurrent Requests**: 80 max per instance
- **Cost**: ~$0.01-0.05 per request (usage-based)
- **Best For**: General healthcare queries, high concurrency needs

## Cost Optimization

### Ollama GPU Deployment
- Use `--min-instances 0` to scale to zero when not in use
- Consider scheduling: turn off during off-peak hours
- Use `--max-instances 1` unless you have high GPU quota
- Monitor usage and optimize concurrency settings

### Standard Deployment
- Use auto-scaling with appropriate min/max instances
- Implement caching for frequently asked questions
- Use request batching where possible

## Next Steps

- Set up continuous deployment with Cloud Build triggers
- Implement authentication (Firebase Auth, OAuth, etc.)
- Add monitoring and alerting
- Configure custom domain
- Implement caching for common queries
- Add request validation and rate limiting
- Set up Cloud Monitoring dashboards for GPU metrics
- Configure log-based alerts for errors and performance issues

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
