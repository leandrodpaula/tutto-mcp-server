resource "alicloud_kms_secret" "mongodb_url" {
  secret_name = "${var.service_name}-mongodb-url-${var.environment}"
  description = "Connection string do MongoDB para ${var.service_name}"
  secret_data = var.mongodb_url
  version_id  = "v1"

  # O recovery window pode ser configurado conforme necessidade
  force_delete_without_recovery = true
}
