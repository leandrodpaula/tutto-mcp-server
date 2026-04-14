#!/bin/bash

# Script auxiliar para rodar Terraform na Alibaba Cloud
# Uso: ./terraform-alibaba.sh [apply|destroy|unlock|import] [args...]

set -e

export TF_VAR_region="cn-hangzhou"
export TF_VAR_environment="hml"
export TF_VAR_service_name="tutto-mcp-server"
export TF_VAR_sae_namespace_id="cn-hangzhou:tutto-hml"
export TF_VAR_mongodb_url="${MONGODB_URL:-mongodb://localhost:27017}"
export TF_VAR_mongodb_database_name="tuttoDb"

# Configurações do backend OSS (substitua pelo seu bucket real)
OSS_BUCKET="${ALIBABA_OSS_BUCKET:-tutto-terraform-state}"
OSS_PREFIX="${ALIBABA_OSS_PREFIX:-tutto-mcp-server/hml}"

cd terraform/alibaba || exit 1

# Inicializa o Terraform apontando para o backend OSS
terraform init \
  -backend-config="bucket=${OSS_BUCKET}" \
  -backend-config="prefix=${OSS_PREFIX}" \
  -backend-config="region=${TF_VAR_region}" \
  -reconfigure

# Aplica o Terraform
if [ "$1" == "apply" ]; then
  terraform apply -auto-approve
fi

# Destrói a infraestrutura
if [ "$1" == "destroy" ]; then
  terraform destroy -auto-approve
fi

# Desbloqueia o estado
if [ "$1" == "unlock" ]; then
  terraform force-unlock -force "$2"
fi

# Importa recursos existentes
if [ "$1" == "import" ]; then
  terraform import "$2" "$3"
fi
