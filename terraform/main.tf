/**
 * Healthcare Assistant - Terraform Configuration
 *
 * This Terraform configuration deploys the Healthcare Assistant agent system
 * to Google Cloud Run with all required infrastructure.
 *
 * Resources created:
 * - Cloud Run service
 * - Firestore database
 * - Service account with appropriate permissions
 * - Required API enablement
 */

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Data sources
data "google_project" "project" {
  project_id = var.project_id
}

# Local variables
locals {
  service_name = var.service_name
  labels = merge(
    var.labels,
    {
      "app"         = "healthcare-assistant"
      "environment" = var.environment
      "managed-by"  = "terraform"
    }
  )

  # Environment variables for Cloud Run
  env_vars = {
    GOOGLE_CLOUD_PROJECT          = var.project_id
    GOOGLE_CLOUD_LOCATION         = var.region
    GOOGLE_GENAI_USE_VERTEXAI     = "1"
    ROOT_MODEL                    = var.root_model
    SYMPTOM_AGENT_MODEL           = var.symptom_agent_model
    DOCUMENTATION_AGENT_MODEL     = var.documentation_agent_model
    LIFESTYLE_AGENT_MODEL         = var.lifestyle_agent_model
    MEDICAL_LABS_AGENT_MODEL      = var.medical_labs_agent_model
    MEDICATIONS_AGENT_MODEL       = var.medications_agent_model
    SPECIALIST_AGENT_MODEL        = var.specialist_agent_model
    APP_NAME                      = var.app_name
    FIRESTORE_COLLECTION          = var.firestore_collection
  }
}

################################################################################
# Enable Required APIs
################################################################################

resource "google_project_service" "cloud_run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firestore" {
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "vertex_ai" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "compute" {
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

################################################################################
# Service Account for Cloud Run
################################################################################

resource "google_service_account" "cloud_run_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "Service Account for Healthcare Assistant Cloud Run"
  description  = "Service account used by Healthcare Assistant Cloud Run service"

  depends_on = [google_project_service.cloud_run]
}

# Grant Vertex AI User role to service account
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Firestore User role to service account
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud Run Invoker role (if needed for internal calls)
resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

################################################################################
# Firestore Database
################################################################################

resource "google_firestore_database" "healthcare_db" {
  count = var.create_firestore_database ? 1 : 0

  provider = google-beta

  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.firestore]
}

################################################################################
# Artifact Registry Repository
################################################################################

resource "google_artifact_registry_repository" "healthcare_repo" {
  provider = google-beta

  location      = var.region
  repository_id = var.artifact_registry_repo
  description   = "Docker repository for Healthcare Assistant"
  format        = "DOCKER"

  labels = local.labels

  depends_on = [google_project_service.artifact_registry]
}

################################################################################
# Cloud Run Service
################################################################################

resource "google_cloud_run_v2_service" "healthcare_assistant" {
  name     = local.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  labels = local.labels

  template {
    # Service account
    service_account = google_service_account.cloud_run_sa.email

    # Scaling configuration
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # Timeout
    timeout = "${var.timeout}s"

    containers {
      # Container image - will be updated by CI/CD or manual deployment
      image = var.container_image

      # Resource allocation
      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }

        cpu_idle          = true
        startup_cpu_boost = true
      }

      # Environment variables
      dynamic "env" {
        for_each = local.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Ports
      ports {
        name           = "http1"
        container_port = var.container_port
      }

      # Startup probe
      startup_probe {
        http_get {
          path = "/health"
          port = var.container_port
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }

      # Liveness probe
      liveness_probe {
        http_get {
          path = "/health"
          port = var.container_port
        }
        initial_delay_seconds = 30
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    # Maximum request timeout
    max_instance_request_concurrency = var.max_concurrency
  }

  # Traffic configuration
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.cloud_run,
    google_service_account.cloud_run_sa,
    google_project_iam_member.vertex_ai_user,
    google_project_iam_member.firestore_user
  ]
}

################################################################################
# IAM Policy for Cloud Run Service (Public Access)
################################################################################

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.allow_unauthenticated_access ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.healthcare_assistant.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

################################################################################
# Cloud Build Trigger (Optional - for CI/CD)
################################################################################

resource "google_cloudbuild_trigger" "deploy_trigger" {
  count = var.enable_cicd ? 1 : 0

  name        = "${var.service_name}-deploy"
  description = "Trigger for deploying Healthcare Assistant on push to ${var.cicd_branch}"
  location    = var.region

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = var.cicd_branch
    }
  }

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t",
        "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.service_name}:$COMMIT_SHA",
        "-t",
        "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.service_name}:latest",
        "."
      ]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "push",
        "--all-tags",
        "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.service_name}"
      ]
    }

    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", var.service_name,
        "--image", "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.service_name}:$COMMIT_SHA",
        "--region", var.region,
        "--platform", "managed"
      ]
    }

    options {
      logging = "CLOUD_LOGGING_ONLY"
    }
  }

  depends_on = [
    google_project_service.cloud_build,
    google_artifact_registry_repository.healthcare_repo
  ]
}
