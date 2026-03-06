# Tutto MCP Server

Um servidor MCP (Model Context Protocol) implementado em Python usando FastMCP. O protocolo MCP (Model Context Protocol) permite que modelos de linguagem interajam com ferramentas e recursos externos de forma padronizada.

---

## 🏗️ Estrutura do Projeto

O projeto adota uma arquitetura modular focada no domínio, simplificando a extensão:

```
tutto-mcp-server/
├── src/
│   ├── core/                  # Configurações globais e inicialização de banco de dados
│   ├── models/                # Modelos de dados e schemas de validação (ex: tenant.py)
│   ├── repositories/          # Operações diretas no banco de dados (Data Access Layer)
│   ├── services/              # Lógica e regras de negócio
│   ├── mcp/                   # Camada de interface do Model Context Protocol (tools, resources)
│   └── main.py                # Ponto de entrada e inicialização do FastMCP
├── tests/                     # Testes unitários do servidor e das ferramentas
├── pyproject.toml             # Configuração do projeto e dependências modernas (uv-ready)
└── README.md                  # Central de Documentação
```

---

## 🚀 Instalação e Configuração

O projeto delega o gerenciamento de dependências ao `pyproject.toml`. É fortemente encorajado o uso do **uv** para gerenciar o pacote, garantindo um ambiente ágil.

### Clone do repositório
```bash
git clone https://github.com/leandrodpaula/tutto-mcp-server.git
cd tutto-mcp-server
```

### Instalação Simplificada (usando uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

*Alternativamente, usando pip tradicional:*
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Configure suas variáveis de ambiente:
```bash
cp .env.example .env
```
*(Preencha dados como o URI do MongoDB `MONGODB_URL` e o `DATABASE_NAME`)*

---

## 💻 Uso

### Executando o Servidor

O script configurado no `pyproject.toml` disponibiliza o comando direto na CLI do seu ambiente virtual:

```bash
tutto-mcp-server
```

Ou, utilizando como módulo Python rodando a partir da raiz:

```bash
python -m src.main
```

### Exemplo de Ferramentas Disponíveis

O servidor vem com ferramentas base que demonstram o roteamento do FastMCP:

- **hello**: Cumprimenta uma pessoa
- **add_numbers**: Adiciona dois números
- **create_tenant** / **get_tenant**: Exemplos de interação assíncrona com MongoDB.

### Exemplo de Recursos Disponíveis

- **config://server**: Obtém informações de configuração do servidor.

---

## 🏛️ Arquitetura e Fluxo de Dados

A base arquitetural utiliza o **FastMCP** acionando recursos internos baseados na Inversão de Dependência via pacotes no diretório `src/`:

```
Cliente MCP
    ↓
FastMCP Server (src/main.py)
    ↓
Tool / Resource Handlers (src/mcp)
    ↓
Services (src/services/...) → Models (src/models/...)
    ↓
Repositories (src/repositories/...)
    ↓
MongoDB (Motor AsyncIO Handler em src/core/)
```

### Padrões de Design e Extensibilidade

Para adicionar novas ferramentas, crie um módulo dentro de `src/mcp/` (p.ex: `billing_tools.py`) e registre a função com o decorador `@mcp.tool()` através de uma assinatura clara de _type hints_:

```python
from fastmcp import FastMCP

def register_billing_tools(mcp: FastMCP):
    @mcp.tool()
    def calculate_tax(amount: float) -> float:
        """
        Calcula os impostos para um valor em BRL.
        """
        return amount * 0.15
```

Registre as novas instâncias importando no `src/main.py` e acoplando-as ao `mcp`.

---

## 🛠️ Desenvolvimento

### Executando Testes

Toda a infraestrutura de testes unitários foi organizada e isolada. Para testar suas lógicas:

```bash
pytest
```
Para obter o relatório de cobertura:
```bash
pytest --cov=src
```

### Formatação de Código e Typings

O pacote disponibiliza comandos essenciais dos _dependencies_ (`[dev]`):

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
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Contato
Leandro D Paula - leandrodpaula@example.com

Link do Projeto: [https://github.com/leandrodpaula/tutto-mcp-server](https://github.com/leandrodpaula/tutto-mcp-server)