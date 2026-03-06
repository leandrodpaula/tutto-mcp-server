#!/bin/bash

export PROJECT_ID="tutto-assistants"
export REGION="southamerica-east1"
export SERVICE_NAME="tutto-mcp-server"

# Tag padrão do build
IMAGE_TAG="${1:-latest}"

# Monta o caminho da imagem no Artifact Registry associando ao repositório unificado
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${SERVICE_NAME}/${SERVICE_NAME}:${IMAGE_TAG}"

echo "Iniciando build e push da imagem usando GCP CLI (Cloud Build)..."
echo "Tag alvo: ${IMAGE_TAG}"
echo "Imagem: ${IMAGE_PATH}"

# Utiliza o Cloud Build para realizar o build baseado no Dockerfile local
gcloud builds submit --tag "${IMAGE_PATH}" .

echo "Build e push concluídos com sucesso!"
