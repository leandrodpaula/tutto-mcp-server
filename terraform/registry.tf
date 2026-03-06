data "google_artifact_registry_repository" "registry" {
  repository_id = "${var.project_id}-registry"
  location      = var.region
}
