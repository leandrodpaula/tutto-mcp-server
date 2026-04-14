# AGENTS.md — Tutto MCP Server

> Este arquivo é destinado a agentes de IA. Ele resume a arquitetura, convenções e processos deste projeto. A linguagem principal da documentação e dos comentários de código é o **português (Brasil)**.

---

## Visão Geral do Projeto

O **Tutto MCP Server** é um servidor MCP (Model Context Protocol) escrito em Python usando a biblioteca [FastMCP](https://github.com/jlowin/fastmcp). Ele atua como uma ponte entre modelos de linguagem (LLMs) e sistemas externos, expondo:

- **Tools (Ferramentas)**: funções executáveis que o LLM pode invocar (CRUDs, agendamentos, assinaturas, etc.).
- **Resources (Recursos)**: informações dinâmicas (ex: configuração via URI).

O domínio de negócio é uma plataforma SaaS para estabelecimentos de beleza/barbearias, oferecendo gestão de:

- **Tenants** (estabelecimentos)
- **Users** (clientes)
- **Instructions** (instruções, serviços e produtos do tenant)
- **Schedules** (agendamentos)
- **Subscriptions** (assinaturas)
- **Plans** (planos de assinatura: silver, gold, etc.)
- **Coupons** (cupons promocionais)
- **Sessions** (histórico de conversas)
- **Messages** (mensagens pendentes para processamento)

A arquitetura é **camada e orientada ao domínio**, com persistência em **MongoDB** via driver assíncrono `motor`.

---

## Stack Tecnológica

| Tecnologia | Uso |
|------------|-----|
| Python 3.10+ | Linguagem principal |
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

---

## Estrutura de Diretórios

```
src/
├── core/              # Configurações, logging e conexão MongoDB
│   ├── config.py      # Settings via pydantic-settings (lê .env)
│   ├── database.py    # MongoDBManager, connect_to_mongo(), get_database()
│   └── logging.py     # setup_logging(), get_logger(name)
├── models/            # Schemas Pydantic (Create, Update, Out)
├── repositories/      # Acesso a dados (padrão Repository)
├── services/          # Regras de negócio e validações
├── mcp/               # Camada de interface MCP (registro de tools)
│   ├── tenant_tools.py
│   ├── user_tools.py
│   ├── schedule_tools.py
│   ├── subscription_tools.py
│   ├── plan_tools.py
│   ├── coupon_tools.py
│   ├── session_tools.py
│   ├── message_tools.py
│   ├── worker_tools.py
│   └── text_tools.py
└── main.py            # Ponto de entrada FastMCP + lifespan + healthz

tests/                 # Testes com pytest
terraform/             # IaC para GCP (Cloud Run, Artifact Registry, Secret Manager)
scripts/               # Scripts utilitários (ex: init_database.py)
```

---

## Comandos de Build, Execução e Teste

### Instalação local

Recomenda-se o uso do `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Ou com `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Executar o servidor localmente

```bash
# Via CLI injetada pelo pacote
tutto-mcp-server

# Ou via módulo Python
python -m src.main
```

O servidor usa por padrão `transport=http` e porta `8000` (configuráveis via env `MCP_TRANSPORT` e `SERVER_PORT`).

### Docker

```bash
docker build -t tutto-mcp-server .
docker run -p 8080:8080 -e PORT=8080 -e MONGODB_URL=... tutto-mcp-server
```

### Testes

```bash
# Rodar todos os testes
pytest

# Relatório de cobertura (requer pytest-cov instalado)
pytest --cov=src
```

---

## Diretrizes de Estilo de Código

- **Black**: `line-length = 100` (configurado em `pyproject.toml`).
- **Ruff**: lint e organização de imports, target `py310`.
- **mypy**: type checking (não exige defs tipadas em 100% dos casos: `disallow_untyped_defs = false`).
- **Docstrings**: em português, descritivas.
- **Logging**: sempre use `get_logger(__name__)` de `src.core.logging`. O prefixo do logger é `tutto-mcp-server`.

### Comandos de qualidade

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

---

## Padrões de Arquitetura

Sempre que adicionar uma nova funcionalidade, siga as camadas abaixo:

### 1. Modelos (`src/models/`)

- Crie classes Pydantic para entrada, atualização e saída.
- Use `PyObjectId` (definido em `src/models/pyobjectid.py`) para campos de ID do MongoDB.
- Inclua `ConfigDict(from_attributes=True, populate_by_name=True)` nos modelos de saída (`*Out`).
- Use `json_schema_extra` nos campos para documentar exemplos.

### 2. Repositórios (`src/repositories/`)

- O repositório recebe `AsyncIOMotorDatabase` no `__init__`.
- Use uma coleção nomeada (ex: `self.collection = db["tenants"]`).
- Implemente `_map_doc(self, doc)` para converter `_id` → `id` (string) antes de retornar.
- Mantenha os métodos focados em CRUD e queries simples.

### 3. Serviços (`src/services/`)

- O serviço recebe o repositório correspondente no `__init__`.
- Defina uma exceção custom `*ServiceError` por domínio.
- Coloque validações de negócio, regras e orquestração aqui.
- Exemplo de serviços existentes: `TenantService`, `ScheduleService`, `SubscriptionService`.

### 4. MCP Tools (`src/mcp/`)

- Crie uma função `register_*_tools(mcp: FastMCP) -> None`.
- Dentro, defina as tools com o decorator `@mcp.tool()`.
- Padrão interno das tools:
  1. `db = get_database()`
  2. Instanciar repositório e serviço.
  3. Executar ação.
  4. Retornar mensagem amigável em string (o MCP espera strings de resposta).
  5. Logar erros com `logger.error(...)` e relançar a exceção.

### 5. Registro em `src/main.py`

- Importe e chame `register_*_tools(mcp)` na seção de registro de tools.

---

## Configuração e Variáveis de Ambiente

O arquivo `src/core/config.py` define `Settings` via `pydantic-settings`. Ele lê automaticamente do arquivo `.env`.

Principais variáveis:

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `MONGODB_URL` | Connection string do MongoDB | Sim |
| `MONGODB_DATABASE_NAME` | Nome do banco de dados | Sim |
| `MERCADO_PAGO_ACCESS_TOKEN` | Token do Mercado Pago | Sim (para pagamentos) |
| `MERCADO_PAGO_BACK_URL_BASE` | URL base para callbacks de pagamento | Não (default: `https://tutto.example.com`) |
| `SERVER_PORT` | Porta HTTP do servidor | Não (default: `8000`) |
| `MCP_TRANSPORT` | Transporte do FastMCP | Não (default: `http`) |
| `LOG_LEVEL` | Nível de log | Não (default: `INFO`) |

Use `.env.example` como base para criar seu `.env` local.

**Importante**: nunca commit secrets. Em produção (GCP), o `MONGODB_URL` vem do **Google Secret Manager**, não de variáveis abertas no Terraform.

---

## Deploy e Infraestrutura

### GCP (Produção/Homologação)

A aplicação roda no **Google Cloud Run**, provisionada via Terraform em `terraform/`:

- **Cloud Run**: serviço serverless autoescalável (0–3 instâncias, 256Mi, CPU idle).
- **Artifact Registry**: imagens Docker privadas.
- **Secret Manager**: segredos injetados diretamente nos containers.
- **Backend Terraform**: estado salvo em GCS (`<project_id>-tfstate`).

### CI/CD (GitHub Actions)

Workflow: `.github/workflows/deploy.yml`

- **build-and-push**: builda a imagem Docker e envia para o Artifact Registry.
- **deploy-hml**: roda `terraform apply` no workspace de homologação (branches `develop`/`main`).
- **deploy-prod**: roda `terraform apply` no workspace de produção (somente branch `main`).
- **destroy-hml**: destrói o ambiente de HML em cron schedule (4x ao dia).

O deploy é acionado via `workflow_dispatch` (manual) ou schedule.

### Scripts auxiliares

- `build.sh`: faz build e push da imagem via `gcloud builds submit`.
- `terraform.sh`: inicializa o Terraform localmente apontando para o backend GCS.

---

## Considerações de Segurança

- **Não hardcode secrets** no código ou no Terraform.
- O `MONGODB_URL` em produção é injetado pelo **Google Secret Manager**.
- O serviço Cloud Run é exposto publicamente (`allUsers` com `roles/run.invoker`).
- Tokens de autenticação de tenant são gerados automaticamente (`secrets.token_hex(16)`) no `TenantService`.
- A validação de CPF/CNPJ usa a biblioteca `validate-docbr` nos modelos Pydantic.

---

## Dicas para Agentes de IA

- Ao criar novos modelos, **sempre** reutilize `PyObjectId` para IDs do MongoDB.
- Ao criar novos repositórios, **sempre** implemente `_map_doc` para converter `_id` em `id`.
- Ao criar novos serviços, **sempre** defina uma exceção `*ServiceError`.
- Ao criar novas tools, mantenha o padrão de retornar `str` amigável e logar erros antes de relançar.
- Ao modificar `src/main.py`, lembre-se de importar e registrar o novo módulo de tools.
- A cobertura de testes ainda é inicial — adicione testes unitários para novas regras de negócio em `tests/`.
- A documentação do projeto (README.md, CONTRIBUTING.md) está em português; mantenha a consistência linguística.
