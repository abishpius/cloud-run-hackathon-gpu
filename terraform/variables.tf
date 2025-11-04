/**
 * Healthcare Assistant - Terraform Variables
 *
 * This file defines all input variables for the Healthcare Assistant
 * infrastructure deployment.
 */

################################################################################
# Project Configuration
################################################################################

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
}

variable "region" {
  description = "The GCP region for deploying resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "production"
}

variable "labels" {
  description = "Additional labels to apply to all resources"
  type        = map(string)
  default     = {}
}

################################################################################
# Cloud Run Service Configuration
################################################################################

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "healthcare-assistant-agent-service"
}

variable "container_image" {
  description = "Container image URL for the Cloud Run service"
  type        = string
  default     = "gcr.io/cloudrun/placeholder"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8080
}

variable "memory" {
  description = "Memory allocation for Cloud Run service (e.g., 512Mi, 1Gi, 2Gi)"
  type        = string
  default     = "2Gi"
}

variable "cpu" {
  description = "CPU allocation for Cloud Run service (e.g., 1, 2, 4)"
  type        = string
  default     = "2"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "max_concurrency" {
  description = "Maximum number of concurrent requests per instance"
  type        = number
  default     = 80
}

variable "timeout" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "allow_unauthenticated_access" {
  description = "Allow unauthenticated access to the Cloud Run service"
  type        = bool
  default     = true
}

################################################################################
# Application Configuration
################################################################################

variable "app_name" {
  description = "Application name for the agent system"
  type        = string
  default     = "healthcare-assistant-app"
}

variable "root_model" {
  description = "Gemini model for the root agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "symptom_agent_model" {
  description = "Gemini model for the symptom analysis agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "documentation_agent_model" {
  description = "Gemini model for the clinical documentation agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "lifestyle_agent_model" {
  description = "Gemini model for the lifestyle recommendations agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "medical_labs_agent_model" {
  description = "Gemini model for the medical labs interpreter agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "medications_agent_model" {
  description = "Gemini model for the medication interaction agent"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "specialist_agent_model" {
  description = "Gemini model for the specialist referral agent"
  type        = string
  default     = "gemini-2.5-flash"
}

################################################################################
# Firestore Configuration
################################################################################

variable "create_firestore_database" {
  description = "Whether to create a Firestore database (set to false if already exists)"
  type        = bool
  default     = false
}

variable "firestore_location" {
  description = "Location for Firestore database"
  type        = string
  default     = "us-central"
}

variable "firestore_collection" {
  description = "Firestore collection name for healthcare data"
  type        = string
  default     = "healthcare-assistant"
}

################################################################################
# Artifact Registry Configuration
################################################################################

variable "artifact_registry_repo" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "healthcare-assistant"
}

################################################################################
# CI/CD Configuration
################################################################################

variable "enable_cicd" {
  description = "Enable Cloud Build trigger for CI/CD"
  type        = bool
  default     = false
}

variable "github_owner" {
  description = "GitHub repository owner (required if enable_cicd is true)"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository name (required if enable_cicd is true)"
  type        = string
  default     = ""
}

variable "cicd_branch" {
  description = "Git branch to trigger deployments"
  type        = string
  default     = "main"
}
