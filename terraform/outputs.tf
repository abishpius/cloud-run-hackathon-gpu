/**
 * Healthcare Assistant - Terraform Outputs
 *
 * This file defines outputs that will be displayed after applying
 * the Terraform configuration.
 */

################################################################################
# Cloud Run Outputs
################################################################################

output "service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.healthcare_assistant.name
}

output "service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.healthcare_assistant.uri
}

output "service_location" {
  description = "Location of the Cloud Run service"
  value       = google_cloud_run_v2_service.healthcare_assistant.location
}

output "service_id" {
  description = "Unique identifier for the Cloud Run service"
  value       = google_cloud_run_v2_service.healthcare_assistant.id
}

################################################################################
# API Endpoints
################################################################################

output "health_endpoint" {
  description = "Health check endpoint URL"
  value       = "${google_cloud_run_v2_service.healthcare_assistant.uri}/health"
}

output "api_docs_url" {
  description = "Swagger API documentation URL"
  value       = "${google_cloud_run_v2_service.healthcare_assistant.uri}/docs"
}

output "redoc_url" {
  description = "ReDoc API documentation URL"
  value       = "${google_cloud_run_v2_service.healthcare_assistant.uri}/redoc"
}

output "new_session_endpoint" {
  description = "Create new session endpoint"
  value       = "${google_cloud_run_v2_service.healthcare_assistant.uri}/api/v1/session/new"
}

output "chat_endpoint" {
  description = "Chat endpoint (non-streaming)"
  value       = "${google_cloud_run_v2_service.healthcare_assistant.uri}/api/v1/chat"
}

output "chat_stream_endpoint" {
  description = "Chat streaming endpoint"
  value       = "${google_cloud_run_v2_service.healthcare_assistant.uri}/api/v1/chat/stream"
}

################################################################################
# Service Account Outputs
################################################################################

output "service_account_email" {
  description = "Email of the service account used by Cloud Run"
  value       = google_service_account.cloud_run_sa.email
}

output "service_account_id" {
  description = "ID of the service account used by Cloud Run"
  value       = google_service_account.cloud_run_sa.account_id
}

################################################################################
# Artifact Registry Outputs
################################################################################

output "artifact_registry_repository" {
  description = "Name of the Artifact Registry repository"
  value       = google_artifact_registry_repository.healthcare_repo.repository_id
}

output "artifact_registry_location" {
  description = "Location of the Artifact Registry repository"
  value       = google_artifact_registry_repository.healthcare_repo.location
}

output "container_image_base_url" {
  description = "Base URL for container images in Artifact Registry"
  value       = "${google_artifact_registry_repository.healthcare_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.healthcare_repo.repository_id}"
}

################################################################################
# Project Information
################################################################################

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

################################################################################
# Configuration Information
################################################################################

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

output "firestore_collection" {
  description = "Firestore collection name for healthcare data"
  value       = var.firestore_collection
}

output "resource_labels" {
  description = "Labels applied to all resources"
  value       = local.labels
}

################################################################################
# Testing Commands
################################################################################

output "test_commands" {
  description = "Commands to test the deployed service"
  value = {
    health_check = "curl ${google_cloud_run_v2_service.healthcare_assistant.uri}/health"
    create_session = "curl -X POST ${google_cloud_run_v2_service.healthcare_assistant.uri}/api/v1/session/new -H 'Content-Type: application/json' -d '{}'"
    view_api_docs = "open ${google_cloud_run_v2_service.healthcare_assistant.uri}/docs"
  }
}

################################################################################
# Deployment Summary
################################################################################

output "deployment_summary" {
  description = "Summary of the deployment"
  value = {
    service_url     = google_cloud_run_v2_service.healthcare_assistant.uri
    api_docs        = "${google_cloud_run_v2_service.healthcare_assistant.uri}/docs"
    health_endpoint = "${google_cloud_run_v2_service.healthcare_assistant.uri}/health"
    project         = var.project_id
    region          = var.region
    service_name    = google_cloud_run_v2_service.healthcare_assistant.name
    memory          = var.memory
    cpu             = var.cpu
    max_instances   = var.max_instances
  }
}
