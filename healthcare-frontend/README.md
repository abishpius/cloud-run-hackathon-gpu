# Healthcare Assistant - Frontend

A Python-based web frontend for the Healthcare Assistant AI system, built with Streamlit and deployed on Google Cloud Run.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)

## Overview

This is the frontend application for the Healthcare Assistant, providing:

- 🔐 **User Authentication** - Secure login system
- 💬 **Chat Interface** - Interactive conversation with Dr. Cloud
- 🎨 **Clean UI** - Modern, responsive design
- ☁️ **Cloud Native** - Deployed on Google Cloud Run
- 🐍 **Pure Python** - No HTML/CSS/JS required

## Features

### Authentication
- Username/password login
- Session management
- Secure cookie-based auth
- Demo credentials included

### Chat Interface
- Real-time messaging with Dr. Cloud
- Message history
- New conversation support
- Typing indicators
- Error handling

### User Experience
- Responsive design
- Mobile-friendly
- Medical disclaimer
- Quick tips and guidance
- Emergency information

## Architecture

```
┌─────────────────────────────┐
│   Streamlit Frontend        │
│                             │
│  ├─ Login Page              │
│  ├─ Chat Interface          │
│  └─ Session Management      │
└─────────────────────────────┘
            │ HTTPS
            ▼
┌─────────────────────────────┐
│   Healthcare Assistant API  │
│   (FastAPI Backend)         │
└─────────────────────────────┘
```

## Project Structure

```
healthcare-frontend/
├── app.py                      # Main application with login
├── pages/
│   ├── 1_💬_Chat.py           # Chat interface
│   └── 2_📊_History.py        # History page (placeholder)
├── components/
│   ├── __init__.py
│   └── api_client.py          # Backend API integration
├── config/
│   ├── __init__.py
│   ├── settings.py            # Configuration
│   └── users.yaml             # User credentials
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Helper functions
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── deploy.sh                  # Deployment script
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Backend API running (see main project README)
- pip (Python package manager)

### Local Development

1. **Clone and navigate to frontend directory**:
   ```bash
   cd healthcare-frontend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   nano .env  # Update BACKEND_API_URL
   ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

6. **Access the app**:
   Open browser to: http://localhost:8501

### Demo Login

Use these credentials to test the app:

- **Username**: `demo`
- **Password**: `demo123`

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Backend API URL (required)
BACKEND_API_URL=http://localhost:8080

# Authentication (change in production)
COOKIE_KEY=your_secret_key

# User database
USERS_FILE=config/users.yaml
```

### Adding Users

Edit `config/users.yaml` to add users:

```python
# Generate password hash
import bcrypt
password = "your_password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
```

Then add to `users.yaml`:

```yaml
credentials:
  usernames:
    newuser:
      email: newuser@example.com
      name: New User
      password: <hashed_password_here>
```

## Deployment

### Option 1: Using Deployment Script

```bash
# Make script executable
chmod +x deploy.sh

# Deploy (replace with your backend URL)
./deploy.sh --backend-url https://your-backend-service-url
```

### Option 2: Manual gcloud Deployment

```bash
# Set variables
export PROJECT_ID="your-project-id"
export BACKEND_URL="https://your-backend-service-url"
export SERVICE_NAME="healthcare-frontend"

# Build container
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars "BACKEND_API_URL=${BACKEND_URL}"
```

### Option 3: Docker Local Testing

```bash
# Build image
docker build -t healthcare-frontend .

# Run container
docker run -p 8080:8080 \
  -e BACKEND_API_URL=http://host.docker.internal:8080 \
  healthcare-frontend
```

## Cloud Run Configuration

Recommended settings:

- **Memory**: 1 GiB
- **CPU**: 1
- **Max Instances**: 5
- **Concurrency**: 80
- **Timeout**: 300 seconds

## API Integration

The frontend communicates with the backend using:

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/session/new` | Create new chat session |
| `POST /api/v1/chat` | Send message and get response |
| `GET /health` | Check backend health |

See `components/api_client.py` for implementation details.

## Development

### Running in Development Mode

```bash
# With auto-reload
streamlit run app.py

# With debug output
streamlit run app.py --logger.level=debug
```

### Code Structure

- **app.py**: Main entry point, handles authentication
- **pages/**: Multi-page app structure (Streamlit convention)
- **components/**: Reusable components (API client, etc.)
- **config/**: Configuration and settings
- **utils/**: Helper functions and utilities

### Adding New Features

1. **New page**:
   ```bash
   # Create new page file
   touch pages/3_📈_Analytics.py
   ```

2. **New API method**:
   Edit `components/api_client.py` to add new methods

3. **New configuration**:
   Add to `config/settings.py`

## Customization

### Changing Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0066CC"  # Change primary color
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Updating Branding

Edit `config/settings.py`:

```python
APP_NAME: str = "Your App Name"
APP_SUBTITLE: str = "Your Subtitle"
PAGE_ICON: str = "🏥"  # Change emoji icon
```

## Security Considerations

### Production Checklist

- [ ] Change `COOKIE_KEY` to a strong secret
- [ ] Use external authentication (Firebase Auth, Auth0)
- [ ] Enable HTTPS only
- [ ] Implement rate limiting
- [ ] Use Secret Manager for credentials
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Review CORS settings
- [ ] Implement audit logging

### Authentication Options

For production, consider:

1. **Firebase Authentication**
2. **Auth0**
3. **Google Identity Platform**
4. **OAuth 2.0**

Replace `streamlit-authenticator` with production auth.

## Troubleshooting

### Common Issues

**Issue**: Can't connect to backend
```bash
# Check BACKEND_API_URL in .env
# Verify backend is running
curl http://localhost:8080/health
```

**Issue**: Login not working
```bash
# Check users.yaml exists
# Verify password hash is correct
# Check COOKIE_KEY is set
```

**Issue**: Port already in use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

**Issue**: Deployment fails
```bash
# Check gcloud authentication
gcloud auth list

# Verify project ID
gcloud config get-value project

# Check Cloud Run logs
gcloud run services logs read healthcare-frontend
```

## Performance

- **Cold Start**: ~5-10 seconds
- **Warm Request**: <1 second
- **Average Page Load**: 1-2 seconds

## Cost Estimation

Monthly costs (moderate usage):

- Cloud Run: $5-15/month
- **Total**: ~$5-15/month

(Backend costs separate)

## Roadmap

- [ ] Enhanced authentication (OAuth)
- [ ] Chat history persistence
- [ ] Export conversations
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Mobile app version
- [ ] Real-time streaming responses
- [ ] User profile management

## Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web framework
- **[streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)** - Authentication
- **[Requests](https://requests.readthedocs.io/)** - HTTP client
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Password hashing
- **[PyYAML](https://pyyaml.org/)** - Configuration
- **[Google Cloud Run](https://cloud.google.com/run)** - Hosting

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues:

1. Check this README
2. Review backend connectivity
3. Check Cloud Run logs
4. Open an issue on GitHub

## License

Apache License 2.0 - See main project LICENSE file

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Integrates with Healthcare Assistant backend
- Powered by Google ADK and Gemini

---

**Built with ❤️ using Streamlit and Python**
