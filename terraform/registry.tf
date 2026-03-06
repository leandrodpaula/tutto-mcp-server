data "google_artifact_registry_repository" "registry" {
  repository_id = "artefacts"
  location      = var.region
}
