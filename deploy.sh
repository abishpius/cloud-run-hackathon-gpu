#!/bin/bash

################################################################################
# Healthcare Assistant - Cloud Run Deployment Script
#
# This script automates the deployment of the Healthcare Assistant agent
# to Google Cloud Run. It handles:
# - Prerequisites validation
# - Docker image building
# - Container registry push
# - Cloud Run service deployment
# - Environment variable configuration
#
# Usage:
#   ./deploy.sh [OPTIONS]
#
# Options:
#   --project-id    GCP project ID (default: from .env or hackathons-461900)
#   --region        GCP region (default: us-central1)
#   --service-name  Cloud Run service name (default: healthcare-assistant-agent-service)
#   --memory        Memory allocation (default: 2Gi)
#   --cpu           CPU allocation (default: 2)
#   --max-instances Maximum instances (default: 10)
#   --allow-unauth  Allow unauthenticated access (default: yes)
#   --help          Display this help message
#
################################################################################

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_PROJECT_ID="hackathons-461900"
DEFAULT_REGION="us-central1"
DEFAULT_SERVICE_NAME="healthcare-assistant-agent-service"
DEFAULT_MEMORY="2Gi"
DEFAULT_CPU="2"
DEFAULT_MAX_INSTANCES="10"
DEFAULT_TIMEOUT="300"
DEFAULT_ALLOW_UNAUTH="yes"

# Configuration variables
PROJECT_ID=""
REGION="${DEFAULT_REGION}"
SERVICE_NAME="${DEFAULT_SERVICE_NAME}"
MEMORY="${DEFAULT_MEMORY}"
CPU="${DEFAULT_CPU}"
MAX_INSTANCES="${DEFAULT_MAX_INSTANCES}"
TIMEOUT="${DEFAULT_TIMEOUT}"
ALLOW_UNAUTH="${DEFAULT_ALLOW_UNAUTH}"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

show_help() {
    cat << EOF
Healthcare Assistant - Cloud Run Deployment Script

Usage:
    ./deploy.sh [OPTIONS]

Options:
    --project-id PROJECT_ID        GCP project ID (default: from .env or ${DEFAULT_PROJECT_ID})
    --region REGION                GCP region (default: ${DEFAULT_REGION})
    --service-name SERVICE_NAME    Cloud Run service name (default: ${DEFAULT_SERVICE_NAME})
    --memory MEMORY                Memory allocation (default: ${DEFAULT_MEMORY})
    --cpu CPU                      CPU allocation (default: ${DEFAULT_CPU})
    --max-instances NUM            Maximum instances (default: ${DEFAULT_MAX_INSTANCES})
    --timeout SECONDS              Request timeout (default: ${DEFAULT_TIMEOUT})
    --no-unauth                    Require authentication
    --help                         Display this help message

Examples:
    # Deploy with defaults
    ./deploy.sh

    # Deploy to specific project
    ./deploy.sh --project-id my-project-123

    # Deploy with custom resources
    ./deploy.sh --memory 4Gi --cpu 4 --max-instances 20

    # Deploy with authentication required
    ./deploy.sh --no-unauth

EOF
    exit 0
}

################################################################################
# Parse command line arguments
################################################################################

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
        --memory)
            MEMORY="$2"
            shift 2
            ;;
        --cpu)
            CPU="$2"
            shift 2
            ;;
        --max-instances)
            MAX_INSTANCES="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --no-unauth)
            ALLOW_UNAUTH="no"
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

################################################################################
# Load configuration from .env if available
################################################################################

load_env_config() {
    local env_file="${SCRIPT_DIR}/Healthcare_Assistant/.env"

    if [ -f "$env_file" ]; then
        print_info "Loading configuration from .env file..."

        # Source the .env file
        set -a
        source "$env_file"
        set +a

        # Use values from .env if not specified via command line
        if [ -z "$PROJECT_ID" ] && [ ! -z "$GOOGLE_CLOUD_PROJECT" ]; then
            PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
        fi

        if [ "$REGION" == "$DEFAULT_REGION" ] && [ ! -z "$GOOGLE_CLOUD_LOCATION" ]; then
            REGION="$GOOGLE_CLOUD_LOCATION"
        fi

        if [ "$SERVICE_NAME" == "$DEFAULT_SERVICE_NAME" ] && [ ! -z "$SERVICE_NAME" ]; then
            SERVICE_NAME="${SERVICE_NAME:-$DEFAULT_SERVICE_NAME}"
        fi
    fi

    # Use default if still not set
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID="$DEFAULT_PROJECT_ID"
    fi
}

################################################################################
# Validation Functions
################################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    local missing_tools=()

    # Check for gcloud
    if ! command -v gcloud &> /dev/null; then
        missing_tools+=("gcloud")
    fi

    # Check for docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_info "Please install the missing tools and try again."
        exit 1
    fi

    print_success "All prerequisites installed"

    # Check if logged in to gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        print_error "Not logged in to gcloud. Please run: gcloud auth login"
        exit 1
    fi

    print_success "Authenticated with gcloud"
}

validate_project() {
    print_header "Validating GCP Project"

    print_info "Setting project to: $PROJECT_ID"

    if ! gcloud config set project "$PROJECT_ID" &> /dev/null; then
        print_error "Failed to set project. Please verify the project ID: $PROJECT_ID"
        exit 1
    fi

    print_success "Project validated: $PROJECT_ID"
}

enable_apis() {
    print_header "Enabling Required APIs"

    local apis=(
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "artifactregistry.googleapis.com"
        "firestore.googleapis.com"
        "aiplatform.googleapis.com"
    )

    print_info "Enabling APIs (this may take a few minutes)..."

    for api in "${apis[@]}"; do
        print_info "Enabling $api..."
        if gcloud services enable "$api" --project="$PROJECT_ID" 2>&1 | grep -q "ERROR"; then
            print_warning "Could not enable $api - it may already be enabled or you may lack permissions"
        fi
    done

    print_success "APIs enabled"
}

################################################################################
# Build and Deploy Functions
################################################################################

build_container() {
    print_header "Building Container Image"

    local image_name="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

    print_info "Building image: $image_name"
    print_info "This may take several minutes..."

    # Build using Cloud Build (recommended) or local Docker
    if gcloud builds submit --tag "$image_name" --project="$PROJECT_ID" --timeout=20m .; then
        print_success "Container built successfully: $image_name"
        echo "$image_name"
    else
        print_error "Failed to build container"
        print_info "Trying local Docker build as fallback..."

        if docker build -t "$image_name" .; then
            print_info "Pushing to Container Registry..."
            docker push "$image_name"
            print_success "Container built and pushed successfully (via Docker)"
            echo "$image_name"
        else
            print_error "Failed to build container with both Cloud Build and Docker"
            exit 1
        fi
    fi
}

deploy_to_cloud_run() {
    local image_name="$1"

    print_header "Deploying to Cloud Run"

    print_info "Service: $SERVICE_NAME"
    print_info "Region: $REGION"
    print_info "Memory: $MEMORY"
    print_info "CPU: $CPU"
    print_info "Max Instances: $MAX_INSTANCES"
    print_info "Timeout: ${TIMEOUT}s"

    local auth_flag="--allow-unauthenticated"
    if [ "$ALLOW_UNAUTH" == "no" ]; then
        auth_flag="--no-allow-unauthenticated"
    fi

    # Build environment variables from .env file
    local env_vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
    env_vars="${env_vars},GOOGLE_CLOUD_LOCATION=${REGION}"
    env_vars="${env_vars},GOOGLE_GENAI_USE_VERTEXAI=1"

    # Add model configurations
    env_vars="${env_vars},ROOT_MODEL=${ROOT_MODEL:-gemini-2.5-flash}"
    env_vars="${env_vars},SYMPTOM_AGENT_MODEL=${SYMPTOM_AGENT_MODEL:-gemini-2.5-flash}"
    env_vars="${env_vars},DOCUMENTATION_AGENT_MODEL=${DOCUMENTATION_AGENT_MODEL:-gemini-2.5-flash}"
    env_vars="${env_vars},LIFESTYLE_AGENT_MODEL=${LIFESTYLE_AGENT_MODEL:-gemini-2.5-flash}"
    env_vars="${env_vars},MEDICAL_LABS_AGENT_MODEL=${MEDICAL_LABS_AGENT_MODEL:-gemini-2.5-flash}"
    env_vars="${env_vars},MEDICATIONS_AGENT_MODEL=${MEDICATIONS_AGENT_MODEL:-gemini-2.5-flash}"
    env_vars="${env_vars},SPECIALIST_AGENT_MODEL=${SPECIALIST_AGENT_MODEL:-gemini-2.5-flash}"

    # Add app configuration
    env_vars="${env_vars},APP_NAME=${APP_NAME:-healthcare-assistant-app}"
    env_vars="${env_vars},FIRESTORE_COLLECTION=${FIRESTORE_COLLECTION:-healthcare-assistant}"

    print_info "Deploying service..."

    if gcloud run deploy "$SERVICE_NAME" \
        --image "$image_name" \
        --platform managed \
        --region "$REGION" \
        $auth_flag \
        --memory "$MEMORY" \
        --cpu "$CPU" \
        --timeout "$TIMEOUT" \
        --max-instances "$MAX_INSTANCES" \
        --set-env-vars "$env_vars" \
        --project "$PROJECT_ID"; then

        print_success "Service deployed successfully!"
        return 0
    else
        print_error "Failed to deploy service"
        return 1
    fi
}

get_service_url() {
    print_header "Service Information"

    local service_url=$(gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --project "$PROJECT_ID" \
        --format='value(status.url)')

    if [ ! -z "$service_url" ]; then
        print_success "Service URL: $service_url"
        echo ""
        print_info "Test your service with:"
        echo ""
        echo "  curl ${service_url}/health"
        echo ""
        print_info "API Documentation:"
        echo ""
        echo "  Swagger UI: ${service_url}/docs"
        echo "  ReDoc:      ${service_url}/redoc"
        echo ""
    else
        print_warning "Could not retrieve service URL"
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "Healthcare Assistant - Cloud Run Deployment"

    echo ""
    print_info "Starting deployment process..."
    echo ""

    # Load configuration
    load_env_config

    # Display configuration
    print_info "Configuration:"
    echo "  Project ID:      $PROJECT_ID"
    echo "  Region:          $REGION"
    echo "  Service Name:    $SERVICE_NAME"
    echo "  Memory:          $MEMORY"
    echo "  CPU:             $CPU"
    echo "  Max Instances:   $MAX_INSTANCES"
    echo "  Timeout:         ${TIMEOUT}s"
    echo "  Allow Unauth:    $ALLOW_UNAUTH"
    echo ""

    # Confirm deployment
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi

    # Execute deployment steps
    check_prerequisites
    validate_project
    enable_apis

    local image_name=$(build_container)

    if deploy_to_cloud_run "$image_name"; then
        get_service_url
        print_success "Deployment completed successfully!"
        exit 0
    else
        print_error "Deployment failed"
        exit 1
    fi
}

# Run main function
main
