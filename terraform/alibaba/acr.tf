resource "alicloud_cr_namespace" "default" {
  name               = var.acr_namespace
  auto_create        = false
  default_visibility = "PRIVATE"
}

resource "alicloud_cr_repo" "default" {
  name      = var.service_name
  namespace = alicloud_cr_namespace.default.name
  summary   = "Repositório de imagens Docker do ${var.service_name}"
  repo_type = "PRIVATE"
  detail    = "Imagens container do Tutto MCP Server"
}

locals {
  acr_registry_domain = "registry-vpc.${var.region}.aliyuncs.com"
  image_url           = "${local.acr_registry_domain}/${alicloud_cr_namespace.default.name}/${alicloud_cr_repo.default.name}:${var.image_tag}"
}
