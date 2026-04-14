output "sae_namespace_id" {
  value       = alicloud_sae_namespace.default.namespace_id
  description = "ID do namespace SAE"
}

output "sae_application_id" {
  value       = alicloud_sae_application.default.id
  description = "ID da aplicação SAE"
}

output "service_url" {
  value       = "http://${alicloud_slb_load_balancer.default.address}"
  description = "URL pública do Tutto MCP Server via SLB"
}

output "acr_repository_url" {
  value       = local.image_url
  description = "URL completa da imagem no Container Registry"
}

output "kms_secret_name" {
  value       = alicloud_kms_secret.mongodb_url.secret_name
  description = "Nome do segredo KMS com a connection string MongoDB"
}
