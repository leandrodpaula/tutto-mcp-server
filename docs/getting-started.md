# Guia de Início Rápido

## O que é MCP?

MCP (Model Context Protocol) é um protocolo que permite que modelos de linguagem interajam com ferramentas e recursos externos de forma padronizada.

## Instalação

### Requisitos
- Python 3.10+
- pip

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/leandrodpaula/tutto-mcp-server.git
cd tutto-mcp-server
```

2. Instale as dependências:
```bash
pip install -e .
```

## Primeiro Servidor

O arquivo `src/tutto_mcp_server/server.py` contém um servidor básico com ferramentas de exemplo.

### Executando

```bash
tutto-mcp-server
```

ou

```bash
python src/tutto_mcp_server/server.py
```

## Adicionando Ferramentas

### Exemplo: Ferramenta Simples

```python
from fastmcp import FastMCP

mcp = FastMCP("Meu Servidor")

@mcp.tool()
def minha_ferramenta(parametro: str) -> str:
    """Descrição da ferramenta."""
    return f"Processado: {parametro}"
```

### Exemplo: Ferramenta com Múltiplos Parâmetros

```python
@mcp.tool()
def calcular(operacao: str, a: float, b: float) -> float:
    """
    Realiza operações matemáticas.
    
    Args:
        operacao: Tipo de operação (add, sub, mul, div)
        a: Primeiro número
        b: Segundo número
    
    Returns:
        Resultado da operação
    """
    if operacao == "add":
        return a + b
    elif operacao == "sub":
        return a - b
    elif operacao == "mul":
        return a * b
    elif operacao == "div":
        return a / b if b != 0 else 0
    else:
        raise ValueError(f"Operação inválida: {operacao}")
```

## Adicionando Recursos

Recursos fornecem acesso a dados:

```python
@mcp.resource("data://exemplo")
def obter_dados() -> str:
    """Retorna dados de exemplo."""
    return "Meus dados aqui"
```

## Organização de Código

### Estrutura Recomendada

```
src/tutto_mcp_server/
├── server.py              # Servidor principal
├── tools/                 # Ferramentas organizadas
│   ├── text_tools.py     # Ferramentas de texto
│   ├── math_tools.py     # Ferramentas matemáticas
│   └── file_tools.py     # Ferramentas de arquivo
└── config.py             # Configurações
```

### Registrando Ferramentas de Módulos

Em `tools/text_tools.py`:

```python
from fastmcp import FastMCP

def register_text_tools(mcp: FastMCP):
    @mcp.tool()
    def uppercase(text: str) -> str:
        return text.upper()
```

No `server.py`:

```python
from fastmcp import FastMCP
from tutto_mcp_server.tools.text_tools import register_text_tools

mcp = FastMCP("Tutto MCP Server")
register_text_tools(mcp)

if __name__ == "__main__":
    mcp.run()
```

## Testes

### Executando Testes

```bash
pytest
```

### Escrevendo Testes

```python
def test_minha_ferramenta():
    from tutto_mcp_server.server import minha_ferramenta
    
    resultado = minha_ferramenta("teste")
    assert "teste" in resultado
```

## Próximos Passos

1. Explore os exemplos em `src/tutto_mcp_server/tools/`
2. Adicione suas próprias ferramentas
3. Configure variáveis de ambiente em `.env`
4. Leia a documentação do FastMCP: https://github.com/jlowin/fastmcp

## Recursos Adicionais

- [Documentação do FastMCP](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Exemplos de Servidores MCP](https://github.com/modelcontextprotocol)
