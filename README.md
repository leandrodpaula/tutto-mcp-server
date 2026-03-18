# Tutto MCP Server

Um servidor MCP (Model Context Protocol) implementado em Python usando FastMCP. O protocolo MCP permite que modelos de linguagem interajam com ferramentas e recursos externos de forma padronizada.

---

## 🎯 O que o projeto faz

O **Tutto MCP Server** atua como uma ponte entre modelos de linguagem e sistemas externos. Ele expõe:
- **Tools (Ferramentas)**: Funções executáveis que o LLM pode chamar para realizar ações no sistema (ex: salvar/ler dados, realizar cálculos). Exemplo das ferramentas padrão: `hello`, `add_numbers`, `create_tenant` e `get_tenant` (com integração assíncrona com MongoDB).
- **Resources (Recursos)**: Informações dinâmicas expostas ao modelo na forma de "arquivos textuais ou URIs" (ex: configuração via `config://server`).

A arquitetura possui persistência usando **MongoDB** via driver assíncrono `motor`.

---

## 🏗️ Estrutura do Projeto

O projeto adota uma arquitetura modular focada no domínio:

```text
tutto-mcp-server/
├── src/
│   ├── core/                  # Configurações e conexão ao banco de dados (MongoDB)
│   ├── models/                # Modelos de dados e schemas de validação (Pydantic)
│   ├── repositories/          # Data Access Layer
│   ├── services/              # Lógica e regras de negócio
│   ├── mcp/                   # Camada de interface MCP (Tools e Resources)
│   └── main.py                # Ponto inicialização do FastMCP
├── terraform/                 # Infraestrutura as Code (IaC) para GCP
├── .github/workflows/         # Pipeline CI/CD (GitHub Actions)
├── tests/                     # Testes unitários do servidor e das ferramentas
├── Dockerfile                 # Configuração para empacotamento em contêiner
└── pyproject.toml             # Configuração do projeto (uv-ready)
```

---

## 🚀 Instalação e Execução Local

### Pré-requisitos
- Python 3.10+
- (Recomendado) `uv` para gestão rápida de dependências.
- Uma instância do banco de dados MongoDB.

### 1. Clonando o repositório
```bash
git clone https://github.com/leandrodpaula/tutto-mcp-server.git
cd tutto-mcp-server
```

### 2. Instalando as Dependências

Usando **uv** (fortemente recomendado):
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Usando **pip**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Variáveis de Ambiente
Crie seu `.env` copiando o arquivo de exemplo:
```bash
cp .env.example .env
```
Preencha as variáveis exigidas, com destaque para a conexão do banco de dados:
```env
MONGODB_URL="mongodb://seu_usuario:sua_senha@localhost:27017"
MONGODB_DATABASE_NAME="tutto_db"
```

### 4. Executando o Servidor Localmente

Através da CLI injetada pelo projeto:
```bash
tutto-mcp-server
```

Ou usando módulo Python:
```bash
python -m src.main
```

---

## 🐳 Uso via Docker

A aplicação pode rodar através do Docker contendo o instalador super rápido da Astral (`uv`):

1. **Build da Imagem**:
   ```bash
   docker build -t tutto-mcp-server .
   ```
2. **Executar o Contêiner** (substituindo o MONGODB_URL com uma connection string acessível de dentro do docker):
   ```bash
   docker run -p 8080:8080 -e PORT=8080 -e MONGODB_URL="mongodb://..." -e MONGODB_DATABASE_NAME="tutto_db" tutto-mcp-server
   ```
   *Nota: O container exportará o FastMCP usando o transporte SSE (Server-Sent Events) apropriado para instâncias stand-alone / cloud.*

---

## ☁️ Como roda no Google Cloud (GCP)

A aplicação é preparada para rodar nativamente em **Serverless** na Google Cloud Platform (GCP).
Os recursos são totalmente provisionados via **Terraform** presente na pasta `/terraform/`:

- **Google Cloud Run**: O serviço em si é executado como um contêiner no Cloud Run. O Terraform ajusta o número de instâncias, os limites de recursos (ex: CPU/RAM) e mapeamentos de portas de forma autoescalável.
- **Google Artifact Registry**: As imagens Docker geradas nos builds são hospedadas de forma privada nele.
- **Google Secret Manager**: Segredos, como a string de conexão do Banco de Dados (`MONGODB_URL`), são extraídos do Secret Manager durante o spin-up do Cloud Run, em vez de vazarem por meio de variáveis abertas do Terraform.
- **State do Terraform**: Fica gravado utilizando Cloud Storage (`backend "gcs"`).

---

## 🔄 Pipeline CI/CD

O projeto conta com automação via GitHub Actions (`.github/workflows/deploy.yml`) focada em branches centrais:

1. **Build & Push (`build-and-push`)**:
   - Acionado via `push` nas branches `develop` ou `main`.
   - Autentica no GCP a partir de secrets no repositório.
   - Faz o build da imagem Docker (usando a tag baseada no número de execuções GitHub) e envia para o Artifact Registry.
2. **Deploy Homologação (`deploy-hml`)**:
   - Acionado no trigger da branch `develop` ou `main`.
   - Lê os arquivos do Terraform (`terraform/`).
   - Inicializa no workspace de Homologação e executa o `terraform apply`.
3. **Deploy Produção (`deploy-prd`)**:
   - Acionado apenas após o HML e exclusivamente na branch `main`.
   - Roda o Terraform no workspace apontado para Produção e atualiza o serviço no Google Cloud Run que ficará disponível em escala produtiva.

---

## 🛠️ Desenvolvimento

### Executando Testes
Toda a infraestrutura de testes unitários foi organizada e isolada via `pytest`.

```bash
# Rodar todos os testes
pytest

# Obter o relatório de cobertura
pytest --cov=src
```

### Formatação de Código e Typings

O pacote disponibiliza comandos essenciais (`[dev]` dependencies):

```bash
# Formatar com Black
black src/ tests/

# Teste estático e Linter Rápido
ruff check src/ tests/

# Type checking Estrito
mypy src/
```

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença
Este projeto está sob a licença [MIT](LICENSE).
Link do Projeto: [https://github.com/leandrodpaula/tutto-mcp-server](https://github.com/leandrodpaula/tutto-mcp-server)