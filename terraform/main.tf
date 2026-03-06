# Habilitando a API do Cloud Run
resource "google_project_service" "cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"

  disable_on_destroy = false
}

# Deploy do serviço Tutto MCP Server no Cloud Run
resource "google_cloud_run_v2_service" "default" {
  name     = "${var.service_name}-cloud-run-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  project  = var.project_id

  template {
    service_account = google_service_account.component_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${data.google_artifact_registry_repository.registry.repository_id}/${var.service_name}:${var.environment}"

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name = "MONGODB_URL"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret_version.mongodb_connection_version.secret
            version = data.google_secret_manager_secret_version.mongodb_connection_version.version
          }
        }
      }

      env {
        name  = "DATABASE_NAME"
        value = "${var.project_id}_db" # Placeholder para nome de banco genérico 
      }

      # Mapeamento do FastMCP
      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = var.environment == "prd" ? 1 : 0
      max_instance_count = 10
    }
  }

  depends_on = [google_project_service.cloud_run]
}

resource "google_cloud_run_v2_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  project  = google_cloud_run_v2_service.default.project
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.component_sa.email}"
}

output "service_url" {
  value       = google_cloud_run_v2_service.default.uri
  description = "A URL pública do Tutto MCP Server"
}
