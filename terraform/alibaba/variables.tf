variable "region" {
  type        = string
  description = "Região principal da Alibaba Cloud (ex: cn-hangzhou, cn-shanghai)"
  default     = "cn-hangzhou"
}

variable "service_name" {
  type        = string
  description = "Nome do serviço/aplicação"
  default     = "tutto-mcp-server"
}

variable "environment" {
  type        = string
  description = "Ambiente (hml, prd)"
}

variable "image_tag" {
  type        = string
  description = "Tag da imagem Docker (ex: commit sha)"
  default     = "latest"
}

variable "mongodb_url" {
  type        = string
  description = "Connection string do MongoDB (será armazenado no KMS Secret)"
  sensitive   = true
}

variable "mongodb_database_name" {
  type        = string
  description = "Nome do banco de dados MongoDB"
  default     = "tuttoDb"
}

variable "sae_namespace_id" {
  type        = string
  description = "ID do namespace SAE (formato: {region}:{nome}, ex: cn-hangzhou:tutto-hml)"
}

variable "acr_namespace" {
  type        = string
  description = "Namespace do Container Registry (ACR)"
  default     = "tutto"
}

variable "app_port" {
  type        = number
  description = "Porta da aplicação container"
  default     = 8000
}
