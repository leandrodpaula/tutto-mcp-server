# Arquitetura do Tutto MCP Server

## Visão Geral

O Tutto MCP Server é construído usando FastMCP, um framework Python que simplifica a criação de servidores MCP (Model Context Protocol).

## Componentes Principais

### 1. Server (`server.py`)

O componente central que:
- Inicializa o FastMCP
- Registra ferramentas e recursos
- Gerencia conexões de clientes
- Processa solicitações

### 2. Tools (`tools/`)

Módulos que contêm ferramentas específicas:
- **text_tools.py**: Processamento de texto
- **math_tools.py**: Operações matemáticas (exemplo)
- **file_tools.py**: Operações com arquivos (exemplo)

### 3. Configuration

Gerenciamento de configuração através de:
- Variáveis de ambiente (`.env`)
- pyproject.toml
- Configurações runtime

## Fluxo de Dados

```
Cliente MCP
    ↓
[Conexão]
    ↓
FastMCP Server
    ↓
[Roteamento]
    ↓
Tool/Resource Handler
    ↓
[Processamento]
    ↓
Resposta → Cliente
```

## Padrões de Design

### 1. Registro de Ferramentas

```python
@mcp.tool()
def ferramenta(params) -> resultado:
    """Docstring serve como descrição."""
    return resultado
```

### 2. Modularização

Cada módulo de ferramentas:
- É independente
- Tem função `register_*_tools(mcp)`
- Pode ser ativado/desativado facilmente

### 3. Type Hints

Todas as funções usam type hints para:
- Validação automática de parâmetros
- Documentação clara
- Melhor IDE support

## Extensibilidade

### Adicionando Nova Ferramenta

1. Crie arquivo em `tools/`
2. Defina função com decorador `@mcp.tool()`
3. Registre no server.py (opcional)

### Adicionando Novo Recurso

1. Use decorador `@mcp.resource(uri)`
2. Retorne dados no formato esperado

## Segurança

### Considerações

- Validação de entrada via type hints
- Sanitização de strings (implementar conforme necessário)
- Rate limiting (adicionar se necessário)
- Autenticação (adicionar se necessário)

### Boas Práticas

- Nunca executar código arbitrário
- Validar todos os inputs
- Limitar acesso a recursos do sistema
- Logar operações sensíveis

## Performance

### Otimizações

- FastMCP é assíncrono por natureza
- Use `async/await` para I/O bound operations
- Cache resultados quando apropriado
- Minimize processamento bloqueante

### Monitoramento

- Logs estruturados
- Métricas de performance
- Tracking de erros

## Deployment

### Opções

1. **Local**: Desenvolvimento e testes
2. **Docker**: Container isolado
3. **Cloud**: AWS Lambda, Google Cloud Functions
4. **Server**: VM tradicional com systemd

### Variáveis de Ambiente

Configuradas via `.env`:
- `SERVER_NAME`: Nome do servidor
- `LOG_LEVEL`: Nível de logging
- `DEBUG`: Modo debug

## Manutenção

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Operação executada")
```

### Versionamento

- Seguir Semantic Versioning
- Atualizar `__version__` em `__init__.py`
- Documentar mudanças em CHANGELOG

## Testing

### Estrutura de Testes

```
tests/
├── test_server.py       # Testes do servidor
├── test_tools.py        # Testes de ferramentas
└── conftest.py          # Fixtures pytest
```

### Tipos de Testes

1. **Unit Tests**: Ferramentas individuais
2. **Integration Tests**: Servidor completo
3. **E2E Tests**: Cliente → Servidor → Resposta
