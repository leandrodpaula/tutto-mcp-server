resource "google_service_account" "component_sa" {
  account_id   = "${var.service_name}-sa-${var.environment}"
  display_name = "Service account for ${var.service_name}"
}
