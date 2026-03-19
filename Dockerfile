FROM python:3.11-slim

# Evitar gravação de bytecode e forçar log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurações do UV para o Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /tutto-mcp-server

# Instalar 'uv' utilizando o script oficial no path
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar arquivos de projeto
COPY pyproject.toml uv.lock ./

# Instalar dependências de forma gerenciada (sem virtualenv no container forçado)
RUN uv sync --frozen --no-cache

# Copiar a aplicação para dentro do contâiner
COPY src/ /tutto-mcp-server/src/

# Garantir que o módulo 'src' seja encontrado pelo Python
ENV PYTHONPATH=/tutto-mcp-server

# Variável usada no Google Cloud Run
ENV PORT=8000

# Iniciar a aplicação utilizando o UV
CMD ["uv", "run", "python", "-m", "src.main"]
