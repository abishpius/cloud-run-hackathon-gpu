#!/bin/bash

################################################################################
# Healthcare Assistant Frontend - Cloud Run Deployment Script
#
# This script automates the deployment of the Healthcare Assistant frontend
# to Google Cloud Run.
#
# Usage:
#   ./deploy.sh [OPTIONS]
#
################################################################################

set -e
set -o pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default configuration
DEFAULT_PROJECT_ID="hackathons-461900"
DEFAULT_REGION="us-central1"
DEFAULT_SERVICE_NAME="healthcare-frontend"
DEFAULT_MEMORY="1Gi"
DEFAULT_CPU="1"
DEFAULT_MAX_INSTANCES="5"

# Configuration variables
PROJECT_ID="${PROJECT_ID:-$DEFAULT_PROJECT_ID}"
REGION="${REGION:-$DEFAULT_REGION}"
SERVICE_NAME="${SERVICE_NAME:-$DEFAULT_SERVICE_NAME}"
MEMORY="${MEMORY:-$DEFAULT_MEMORY}"
CPU="${CPU:-$DEFAULT_CPU}"
MAX_INSTANCES="${MAX_INSTANCES:-$DEFAULT_MAX_INSTANCES}"
BACKEND_URL="${BACKEND_URL:-}"

# Helper functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --service-name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --backend-url)
            BACKEND_URL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --project-id PROJECT_ID     GCP project ID"
            echo "  --region REGION             GCP region"
            echo "  --service-name NAME         Cloud Run service name"
            echo "  --backend-url URL           Backend API URL"
            echo "  --help                      Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate backend URL
if [ -z "$BACKEND_URL" ]; then
    print_error "Backend URL is required. Use --backend-url option."
    echo ""
    echo "Example:"
    echo "  ./deploy.sh --backend-url https://your-backend-service-url"
    exit 1
fi

print_info "Starting deployment..."
echo "  Project ID:    $PROJECT_ID"
echo "  Region:        $REGION"
echo "  Service Name:  $SERVICE_NAME"
echo "  Backend URL:   $BACKEND_URL"
echo ""

# Set project
print_info "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Build container
print_info "Building container image..."
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

if gcloud builds submit --tag "$IMAGE_NAME" --project="$PROJECT_ID" .; then
    print_success "Container built successfully"
else
    print_error "Failed to build container"
    exit 1
fi

# Deploy to Cloud Run
print_info "Deploying to Cloud Run..."

if gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory "$MEMORY" \
    --cpu "$CPU" \
    --max-instances "$MAX_INSTANCES" \
    --set-env-vars "BACKEND_API_URL=${BACKEND_URL}" \
    --project "$PROJECT_ID"; then

    print_success "Frontend deployed successfully!"
else
    print_error "Failed to deploy frontend"
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --format='value(status.url)')

print_success "Deployment completed!"
echo ""
print_info "Frontend URL: $SERVICE_URL"
echo ""
print_info "Test your deployment:"
echo "  open $SERVICE_URL"
echo ""
