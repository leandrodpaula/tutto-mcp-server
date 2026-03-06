#!/bin/bash

export PROJECT_ID="tutto-assistants"
export REGION="southamerica-east1"
export SERVICE_NAME="tutto-mcp-server"

# Ambiente padrão 
ENV_NAME="${1:-hml}"

# Monta o caminho da imagem no Artifact Registry associando ao repositório terraformado
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${SERVICE_NAME}-repo-${ENV_NAME}/${SERVICE_NAME}:${ENV_NAME}"

echo "Iniciando build e push da imagem usando GCP CLI (Cloud Build)..."
echo "Ambiente alvo: ${ENV_NAME}"
echo "Imagem: ${IMAGE_PATH}"

# Utiliza o Cloud Build para realizar o build baseado no Dockerfile local
gcloud builds submit --tag "${IMAGE_PATH}" .

echo "Build e push concluídos com sucesso!"
