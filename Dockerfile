FROM python:3.11-slim

# Evitar gravação de bytecode e forçar log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurações do UV para o Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /code

# Instalar 'uv' utilizando o script oficial no path
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar arquivos de configuração do projeto 
COPY pyproject.toml .

# Sincronizar dependências no root do container de forma otimizada
RUN uv pip install --system -e .

# Copiar a aplicação para dentro do contâiner
COPY src/ ./src/

# Garantir que o módulo 'src' seja encontrado pelo Python
ENV PYTHONPATH=/code

# Variável usada no Google Cloud Run
ENV PORT=8080

# Iniciar via FastMCP CLI forçando o protocolo SSE para ambientes serverless
CMD fastmcp run src/main.py:mcp --transport sse --host 0.0.0.0 --port $PORT
