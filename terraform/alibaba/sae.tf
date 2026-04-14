resource "alicloud_sae_namespace" "default" {
  namespace_id              = var.sae_namespace_id
  namespace_name            = "${var.service_name}-${var.environment}"
  namespace_description     = "Namespace SAE para ${var.service_name} - ${var.environment}"
  enable_micro_registration = false
}

resource "alicloud_sae_application" "default" {
  app_name          = "${var.service_name}-app-${var.environment}"
  app_description   = "Aplicação ${var.service_name} no ambiente ${var.environment}"
  namespace_id      = alicloud_sae_namespace.default.namespace_id
  package_type      = "Image"
  image_url         = local.image_url
  vpc_id            = alicloud_vpc.default.id
  vswitch_id        = alicloud_vswitch.default.id
  security_group_id = alicloud_security_group.default.id
  timezone          = "America/Sao_Paulo"
  replicas          = 1
  cpu               = 500
  memory            = 1024

  envs = jsonencode([
    {
      name  = "ENVIRONMENT"
      value = var.environment
    },
    {
      name  = "MONGODB_URL"
      value = alicloud_kms_secret.mongodb_url.secret_data
    },
    {
      name  = "MONGODB_DATABASE_NAME"
      value = var.mongodb_database_name
    },
    {
      name  = "SERVER_PORT"
      value = tostring(var.app_port)
    },
    {
      name  = "MCP_TRANSPORT"
      value = "http"
    }
  ])
}

# SLB para expor a aplicação publicamente
resource "alicloud_slb_load_balancer" "default" {
  load_balancer_name = "${var.service_name}-slb-${var.environment}"
  address_type       = "internet"
  load_balancer_spec = "slb.s1.small"
  vswitch_id         = alicloud_vswitch.default.id
}

resource "alicloud_sae_ingress" "default" {
  namespace_id  = alicloud_sae_namespace.default.namespace_id
  slb_id        = alicloud_slb_load_balancer.default.id
  listener_port = "80"

  default_rule {
    app_id         = alicloud_sae_application.default.id
    container_port = var.app_port
  }

  rules {
    app_id         = alicloud_sae_application.default.id
    container_port = var.app_port
    domain         = alicloud_slb_load_balancer.default.address
    path           = "/"
    app_name       = alicloud_sae_application.default.app_name
  }
}
