variable "project_id" {
  type        = string
  description = "ID do projeto GCP"
}

variable "service_name" {
  type        = string
  description = "Nome do serviço/aplicação associado"
}

variable "environment" {
  type        = string
  description = "Ambiente (hml, prd)"
}

variable "region" {
  type        = string
  description = "Região principal do GCP"
}

variable "image_tag" {
  type        = string
  description = "Tag da imagem Docker (ex: commit sha)"
  default     = "latest"
}
