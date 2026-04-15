# Tutto MCP Server

Servidor híbrido **FastAPI + MCP (Model Context Protocol)** para estabelecimentos de beleza e barbearias. A aplicação expõe tanto **rotas HTTP REST** quanto **ferramentas MCP** que permitem que modelos de linguagem (LLMs) interajam com o sistema — realizando CRUDs de tenants, usuários, agendamentos, assinaturas, cupons, sessões e mensagens pendentes.

---

## 🎯 O que o projeto faz

O **Tutto MCP Server** atua como uma ponte entre LLMs e sistemas externos, oferecendo:

- **API HTTP (FastAPI)**: endpoints REST para integração direta com outros serviços.
- **Tools MCP**: funções executáveis que o LLM pode invocar via protocolo MCP.
- **Persistência**: MongoDB assíncrono via `motor`.
- **Pagamentos**: integração com Mercado Pago para geração de links de pagamento.

Domínios principais:
- **Tenants** (estabelecimentos)
- **Users** (clientes)
- **Instructions** (serviços e produtos)
- **Schedules** (agendamentos)
- **Subscriptions / Plans / Coupons**
- **Sessions / Messages** (conversas e fila de mensagens pendentes)

---

## 🏗️ Arquitetura e Stack Tecnológica

| Tecnologia | Uso |
|------------|-----|
| Python 3.10+ | Linguagem principal |
| FastAPI | API HTTP e documentação automática (OpenAPI) |
| FastMCP | Framework MCP server |
| Motor | Driver assíncrono MongoDB |
| Pydantic / pydantic-settings | Validação de dados e configuração |
| mercadopago | SDK para geração de links de pagamento |
| validate-docbr | Validação de CPF/CNPJ |
| pytest / pytest-asyncio | Testes |
| Black / Ruff / mypy | Formatação, lint e type checking |
| uv | Gerenciamento de dependências e ambiente virtual |
| Docker | Containerização |
| Terraform (GCP) | Infraestrutura como código |
| GitHub Actions | CI/CD |

### Estrutura de pastas

```text
src/
├── core/              # Configurações, logging, conexão MongoDB e lifespan
├── models/            # Schemas Pydantic (Create, Update, Out)
├── repositories/      # Acesso a dados (padrão Repository)
├── services/          # Regras de negócio e validações
├── api/               # Camada HTTP (FastAPI routers)
│   ├── deps.py        # Dependências reutilizáveis (get_db)
│   └── routes/        # Routers (health, messages, etc.)
├── mcp/               # Camada MCP (registro de tools)
└── main.py            # FastAPI app principal + registro de tools MCP

terraform/             # IaC para GCP (Cloud Run, Artifact Registry, Secret Manager)
.github/workflows/     # Pipeline CI/CD
```

### Estrutura do Servidor

- **`src/main.py`**: Ponto de entrada que cria o app `FastAPI`, configura o objeto `FastMCP`, registra todas as tools e monta o MCP como sub-app ASGI em `/mcp` via `mcp.http_app()`.
- **`src/core/lifespan.py`**: lifespan compartilhado entre FastAPI e MCP para gerenciar a conexão com o MongoDB.

---

## 📝 Pré-requisitos

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/) (recomendado para gerenciamento de dependências)
- Uma instância do **MongoDB** acessível localmente ou na nuvem
- Conta no **Google Cloud Platform** (para deploy via Terraform)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) e [Terraform](https://developer.hashicorp.com/terraform/downloads) (para deploy manual)

---

## 🔧 Configuração de Ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

### Variáveis de ambiente

| Variável | Propósito | Obrigatória | Default |
|----------|-----------|-------------|---------|
| `MONGODB_URL` | Connection string do MongoDB | Sim | — |
| `MONGODB_DATABASE_NAME` | Nome do banco de dados | Não | `tuttoDb` |
| `MERCADO_PAGO_ACCESS_TOKEN` | Token de acesso do Mercado Pago | Sim (para pagamentos) | `""` |
| `MERCADO_PAGO_BACK_URL_BASE` | URL base para callbacks de pagamento | Não | `https://tutto.example.com` |
| `SERVER_PORT` | Porta HTTP do servidor | Não | `8000` |
| `MCP_TRANSPORT` | Transporte do FastMCP | Não | `http` |
| `LOG_LEVEL` | Nível de log | Não | `INFO` |

---

## 🚀 Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/leandrodpaula/tutto-mcp-server.git
cd tutto-mcp-server
```

### 2. Instale as dependências

Usando **uv** (recomendado):

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Ou com **pip**:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Execute o servidor

```bash
# Via CLI injetada pelo pacote
tutto-mcp-server

# Ou diretamente via módulo
python -m src.main
```

O servidor será iniciado em `http://localhost:8000` (ou na porta definida em `SERVER_PORT`).

### 4. Verifique se está funcionando

- **Health check**: `GET http://localhost:8000/healthz`
- **Documentação OpenAPI**: `http://localhost:8000/docs`
- **MCP (sub-app)**: montado em `http://localhost:8000/mcp`
- **Criar mensagem pending**: `POST http://localhost:8000/messages/pending`

### 🐳 Docker

Build e execução local via Docker:

```bash
# Build
docker build -t tutto-mcp-server .

# Run
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e MONGODB_URL="mongodb://..." \
  -e MONGODB_DATABASE_NAME="tutto_db" \
  tutto-mcp-server
```

---

## ☁️ Deploy no Google Cloud Run (Terraform)

A infraestrutura é 100% provisionada via **Terraform** na pasta `terraform/`.

### Recursos criados

- **Google Cloud Run**: serviço serverless que executa o container (escala 0–3, 256 MiB, CPU idle).
- **Google Artifact Registry**: repositório privado de imagens Docker.
- **Google Secret Manager**: segredos (ex: `MONGODB_URL`) injetados diretamente no container — nunca expostos como variáveis abertas no Terraform.
- **Cloud Storage**: backend remoto do estado Terraform (`<project_id>-tfstate`).

### CI/CD (GitHub Actions)

O workflow `.github/workflows/deploy.yml` possui os seguintes jobs:

1. **`build-and-push`**: faz o build da imagem Docker e envia para o Artifact Registry.
2. **`deploy-hml`**: executa `terraform apply` no workspace de **homologação** (`hml`). Disparado manualmente (`workflow_dispatch`) a partir das branches `develop` ou `main`.
3. **`deploy-prod`**: executa `terraform apply` no workspace de **produção** (`prd`). Disparado manualmente apenas a partir da branch `main`.
4. **`destroy-hml`**: destrói o ambiente de HML automaticamente via cron (4x ao dia).

> **Importante**: o deploy é acionado manualmente (`workflow_dispatch`). Merge na branch não dispara deploy automático.

### Deploy manual via Terraform (local)

Se preferir rodar o Terraform localmente:

```bash
# Configure o projeto gcloud
gcloud config set project <SEU_PROJECT_ID>
gcloud auth application-default login

# Inicialize o backend remoto
./terraform.sh

# Aplique para HML
cd terraform
terraform workspace select hml || terraform workspace new hml
terraform apply -auto-approve

# Aplique para PRD
terraform workspace select prd || terraform workspace new prd
terraform apply -auto-approve
```

---

## 🛠️ Desenvolvimento

### Testes

```bash
# Rodar todos os testes
pytest

# Cobertura
pytest --cov=src
```

### Qualidade de código

```bash
# Formatação
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

---

## 🏛️ Decisões de Arquitetura (ADR)

### Arquitetura Unificada

O projeto utiliza o `FastAPI` como servidor principal, que monta o `FastMCP` como um sub-app ASGI em `/mcp`. Isso permite que o servidor responda tanto a requisições HTTP REST quanto ao protocolo MCP no mesmo processo.

- `src/main.py` → Concentra a configuração do app FastAPI e a instância do MCP.
- `src/core/lifespan.py` → Lifespan compartilhado que garante uma única conexão com o MongoDB para ambas as camadas.

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

Link do Projeto: [https://github.com/leandrodpaula/tutto-mcp-server](https://github.com/leandrodpaula/tutto-mcp-server)
