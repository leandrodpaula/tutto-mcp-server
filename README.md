# Tutto MCP Server

Um servidor MCP (Model Context Protocol) implementado em Python usando FastMCP.

## 📋 Descrição

Este projeto implementa um servidor MCP utilizando o framework FastMCP, fornecendo uma estrutura base para criar ferramentas e recursos que podem ser utilizados por clientes MCP.

## 🏗️ Estrutura do Projeto

```
tutto-mcp-server/
├── src/
│   └── tutto_mcp_server/
│       ├── __init__.py          # Módulo principal do pacote
│       ├── server.py             # Implementação do servidor MCP
│       └── tools/                # Diretório para ferramentas customizadas
├── tests/                        # Testes unitários
├── pyproject.toml                # Configuração do projeto e dependências
├── requirements.txt              # Dependências de produção
├── requirements-dev.txt          # Dependências de desenvolvimento
└── README.md                     # Este arquivo
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Instalação do Pacote

1. Clone o repositório:
```bash
git clone https://github.com/leandrodpaula/tutto-mcp-server.git
cd tutto-mcp-server
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -e .
```

Ou para desenvolvimento:
```bash
pip install -e ".[dev]"
```

Ou usando requirements.txt:
```bash
pip install -r requirements.txt
# Para desenvolvimento:
pip install -r requirements-dev.txt
```

## 💻 Uso

### Executando o Servidor

Você pode executar o servidor de várias formas:

1. Usando o comando instalado:
```bash
tutto-mcp-server
```

2. Como módulo Python:
```bash
python -m tutto_mcp_server.server
```

3. Diretamente:
```bash
python src/tutto_mcp_server/server.py
```

### Ferramentas Disponíveis

O servidor vem com ferramentas de exemplo:

- **hello**: Cumprimenta uma pessoa
  ```python
  hello(name="João")  # Retorna: "Hello, João! Welcome to Tutto MCP Server."
  ```

- **add_numbers**: Adiciona dois números
  ```python
  add_numbers(a=5, b=3)  # Retorna: 8
  ```

### Recursos Disponíveis

- **config://server**: Obtém informações de configuração do servidor

## 🛠️ Desenvolvimento

### Estrutura de Código

Para adicionar novas ferramentas ao servidor, edite o arquivo `src/tutto_mcp_server/server.py`:

```python
@mcp.tool()
def sua_ferramenta(parametro: str) -> str:
    """
    Descrição da sua ferramenta.
    
    Args:
        parametro: Descrição do parâmetro
        
    Returns:
        Descrição do retorno
    """
    return f"Resultado: {parametro}"
```

### Executando Testes

```bash
pytest
```

Com cobertura:
```bash
pytest --cov=tutto_mcp_server
```

### Formatação de Código

```bash
# Formatar com black
black src/ tests/

# Verificar com ruff
ruff check src/ tests/

# Type checking com mypy
mypy src/
```

## 📦 Dependências

### Principais
- **fastmcp**: Framework para construção de servidores MCP

### Desenvolvimento
- **pytest**: Framework de testes
- **black**: Formatador de código
- **ruff**: Linter
- **mypy**: Type checker

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Contato

Leandro D Paula - leandrodpaula@example.com

Link do Projeto: [https://github.com/leandrodpaula/tutto-mcp-server](https://github.com/leandrodpaula/tutto-mcp-server)