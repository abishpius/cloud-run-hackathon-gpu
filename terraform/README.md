# Healthcare Assistant - Terraform Infrastructure

This directory contains Terraform configurations for deploying the Healthcare Assistant infrastructure to Google Cloud Platform.

## Overview

The Terraform configuration provisions:

- ✅ Cloud Run service with auto-scaling
- ✅ Service account with appropriate IAM permissions
- ✅ Artifact Registry repository for container images
- ✅ Firestore database (optional)
- ✅ Required Google Cloud APIs
- ✅ Cloud Build trigger for CI/CD (optional)

## Prerequisites

1. **Terraform** installed (>= 1.0)
   ```bash
   # macOS
   brew install terraform

   # Windows (with Chocolatey)
   choco install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **gcloud CLI** installed and authenticated
   ```bash
   gcloud auth application-default login
   ```

3. **GCP Project** with billing enabled

4. **Container Image** built and pushed (see main README.md)

## Quick Start

### 1. Configure Variables

```bash
# Copy example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit with your configuration
nano terraform.tfvars
```

**Required variables to update:**
- `project_id`: Your GCP project ID
- `container_image`: Your built container image URL

### 2. Initialize Terraform

```bash
terraform init
```

This downloads required providers and sets up the backend.

### 3. Review the Plan

```bash
terraform plan
```

This shows what resources will be created/modified.

### 4. Apply the Configuration

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5. Get Output Information

```bash
terraform output
```

This displays the service URL and other important information.

## Configuration Files

### main.tf

Main Terraform configuration with resource definitions:
- Google Cloud APIs
- Service account and IAM bindings
- Artifact Registry repository
- Cloud Run service
- Firestore database (optional)
- Cloud Build trigger (optional)

### variables.tf

Input variable definitions with descriptions and defaults.

### outputs.tf

Output values displayed after deployment:
- Service URL
- API endpoints
- Service account details
- Test commands

### terraform.tfvars

Your configuration values (not tracked in git).

## Important Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `project_id` | GCP Project ID | `my-project-123` |
| `container_image` | Container image URL | `gcr.io/my-project/app:latest` |

### Common Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `region` | GCP region | `us-central1` |
| `service_name` | Cloud Run service name | `healthcare-assistant-agent-service` |
| `memory` | Memory allocation | `2Gi` |
| `cpu` | CPU allocation | `2` |
| `max_instances` | Max instances | `10` |
| `allow_unauthenticated_access` | Public access | `true` |

### Agent Models

| Variable | Description | Default |
|----------|-------------|---------|
| `root_model` | Root agent model | `gemini-2.5-flash` |
| `symptom_agent_model` | Symptom agent model | `gemini-2.5-flash` |
| `documentation_agent_model` | Documentation agent model | `gemini-2.5-flash` |
| `lifestyle_agent_model` | Lifestyle agent model | `gemini-2.5-flash` |
| `medical_labs_agent_model` | Lab agent model | `gemini-2.5-flash` |
| `medications_agent_model` | Medication agent model | `gemini-2.5-flash` |
| `specialist_agent_model` | Specialist agent model | `gemini-2.5-flash` |

## Complete Workflow

### First-Time Deployment

```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Configure variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Update project_id and container_image

# 3. Initialize Terraform
terraform init

# 4. Review plan
terraform plan

# 5. Apply configuration
terraform apply

# 6. Get service URL
terraform output service_url
```

### Building and Pushing Container Image

Before applying Terraform, you need a container image:

```bash
# Go back to project root
cd ..

# Set variables
export PROJECT_ID="your-project-id"
export SERVICE_NAME="healthcare-assistant-agent-service"

# Build and push
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Update terraform.tfvars with the image URL
# Then run terraform apply
```

### Updating the Deployment

```bash
# 1. Build new container image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}:v2

# 2. Update terraform.tfvars with new image
# container_image = "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:v2"

# 3. Apply changes
terraform apply
```

## Terraform Commands

### Common Commands

```bash
# Initialize (first time or after adding providers)
terraform init

# Format code
terraform fmt

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply

# Show current state
terraform show

# List resources
terraform state list

# Get outputs
terraform output

# Destroy all resources (⚠️ CAUTION)
terraform destroy
```

### Advanced Commands

```bash
# Plan with variables file
terraform plan -var-file="production.tfvars"

# Apply without confirmation (CI/CD)
terraform apply -auto-approve

# Target specific resource
terraform apply -target=google_cloud_run_v2_service.healthcare_assistant

# Refresh state
terraform refresh

# Import existing resource
terraform import google_cloud_run_v2_service.healthcare_assistant projects/PROJECT_ID/locations/REGION/services/SERVICE_NAME
```

## State Management

### Local State (Default)

By default, Terraform stores state locally in `terraform.tfstate`.

**⚠️ Warning:** Do not commit `terraform.tfstate` to git!

### Remote State (Recommended for Teams)

Use GCS bucket for remote state:

Add to `main.tf`:

```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state-bucket"
    prefix = "healthcare-assistant"
  }
}
```

Create the bucket:

```bash
gsutil mb gs://my-terraform-state-bucket
gsutil versioning set on gs://my-terraform-state-bucket
```

## Outputs

After applying, you'll get outputs like:

```
service_url = "https://healthcare-assistant-agent-service-abc123-uc.a.run.app"
health_endpoint = "https://healthcare-assistant-agent-service-abc123-uc.a.run.app/health"
api_docs_url = "https://healthcare-assistant-agent-service-abc123-uc.a.run.app/docs"
```

Test the deployment:

```bash
# Health check
curl $(terraform output -raw service_url)/health

# API docs
open $(terraform output -raw api_docs_url)
```

## Firestore Configuration

### New Firestore Database

If you need to create a new Firestore database:

```hcl
create_firestore_database = true
firestore_location = "us-central"
```

### Existing Firestore Database

If you already have a Firestore database:

```hcl
create_firestore_database = false
```

## CI/CD with Cloud Build

Enable automatic deployments from GitHub:

```hcl
enable_cicd = true
github_owner = "your-username"
github_repo = "cloud-run-hackathon-gpu"
cicd_branch = "main"
```

This creates a Cloud Build trigger that:
1. Builds container on push to main
2. Pushes to Artifact Registry
3. Deploys to Cloud Run

## Security Best Practices

### 1. Use Remote State with Encryption

```hcl
terraform {
  backend "gcs" {
    bucket  = "terraform-state-bucket"
    prefix  = "healthcare-assistant"
    encryption_key = "your-encryption-key"
  }
}
```

### 2. Restrict Access

```hcl
allow_unauthenticated_access = false
```

Then add IAM bindings for authorized users.

### 3. Use Secret Manager for Sensitive Data

Instead of environment variables for secrets:

```hcl
# Add secret from Secret Manager
env {
  name = "API_KEY"
  value_source {
    secret_key_ref {
      secret  = "api-key"
      version = "latest"
    }
  }
}
```

### 4. Enable VPC Connector (Private Networking)

```hcl
# In Cloud Run service template
vpc_access {
  connector = google_vpc_access_connector.connector.name
  egress    = "PRIVATE_RANGES_ONLY"
}
```

## Cost Optimization

### Reduce Costs

```hcl
# Use smaller resources for dev
memory        = "512Mi"
cpu           = "1"
max_instances = 3

# Set minimum instances to 0 (cold starts OK for dev)
min_instances = 0
```

### Production Settings

```hcl
# Better performance for production
memory        = "2Gi"
cpu           = "2"
min_instances = 1  # Avoid cold starts
max_instances = 20
```

## Troubleshooting

### Issue: terraform init fails

```bash
# Clear cache and retry
rm -rf .terraform
terraform init
```

### Issue: Permission denied

```bash
# Re-authenticate
gcloud auth application-default login

# Check project
gcloud config get-value project
```

### Issue: Service fails to deploy

```bash
# Check Cloud Run logs
gcloud run services logs read healthcare-assistant-agent-service --limit 50

# Verify container image exists
gcloud container images list
```

### Issue: APIs not enabled

```bash
# Manually enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## Cleanup

To destroy all resources:

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy (⚠️ CAUTION - this is irreversible!)
terraform destroy
```

## Additional Resources

- [Terraform GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Terraform Guide](https://cloud.google.com/run/docs/deploying#terraform)
- [Terraform Best Practices](https://cloud.google.com/docs/terraform/best-practices)

## Support

For issues:
1. Check Cloud Run logs: `gcloud run services logs read SERVICE_NAME`
2. Review Terraform plan: `terraform plan`
3. Validate configuration: `terraform validate`
4. Check outputs: `terraform output`
