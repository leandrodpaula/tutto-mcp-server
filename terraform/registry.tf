data "google_artifact_registry_repository" "registry" {
  repository_id = "${var.service_name}-repo-${var.environment}"
  location      = var.region
}
