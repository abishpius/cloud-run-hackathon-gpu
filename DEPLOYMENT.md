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

### Method 1: Using gcloud CLI

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

## Security Considerations

1. **Authentication**: Consider adding authentication middleware for production
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Data Privacy**: Healthcare data is sensitive - ensure compliance with HIPAA/regulations
4. **Environment Variables**: Use Secret Manager for sensitive configuration
5. **CORS**: Configure CORS appropriately for your frontend domains

## Next Steps

- Set up continuous deployment with Cloud Build triggers
- Implement authentication (Firebase Auth, OAuth, etc.)
- Add monitoring and alerting
- Configure custom domain
- Implement caching for common queries
- Add request validation and rate limiting

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
