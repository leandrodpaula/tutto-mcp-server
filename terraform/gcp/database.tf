data "google_secret_manager_secret_version" "mongodb_connection_version" {
  secret = "${var.project_id}-mongodb-connection-${var.environment}"
}

resource "google_secret_manager_secret_iam_binding" "mongodb_connection_string_access" {
  secret_id = data.google_secret_manager_secret_version.mongodb_connection_version.secret
  role      = "roles/secretmanager.secretAccessor"

  members = [
    "serviceAccount:${google_service_account.component_sa.email}",
  ]
}


