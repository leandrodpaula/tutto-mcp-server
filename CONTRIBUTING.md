# Contribuindo para Tutto MCP Server

Obrigado por considerar contribuir para o Tutto MCP Server! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### Reportando Bugs

Ao reportar bugs, por favor inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Versão do Python e sistema operacional
- Logs relevantes

### Sugerindo Melhorias

Para sugerir melhorias:
- Use a aba Issues do GitHub
- Descreva claramente a melhoria proposta
- Explique por que seria útil
- Se possível, forneça exemplos de uso

### Pull Requests

1. **Fork o repositório** e crie sua branch a partir de `main`
2. **Faça suas alterações** seguindo as diretrizes de código
3. **Adicione testes** para novas funcionalidades
4. **Execute os testes** localmente antes de enviar
5. **Atualize a documentação** se necessário
6. **Envie o Pull Request**

## Diretrizes de Código

### Estilo de Código

- Use **Black** para formatação (line-length=100)
- Use **Ruff** para linting
- Use **mypy** para type checking
- Siga PEP 8 e PEP 257 para docstrings

### Testes

- Escreva testes para todas as novas funcionalidades
- Mantenha a cobertura de testes acima de 80%
- Use pytest para todos os testes
- Nomeie os testes descritivamente

### Commits

- Use mensagens de commit claras e descritivas
- Siga o padrão: `tipo: descrição`
  - `feat:` Nova funcionalidade
  - `fix:` Correção de bug
  - `docs:` Mudanças na documentação
  - `test:` Adição ou modificação de testes
  - `refactor:` Refatoração de código
  - `style:` Mudanças de formatação
  - `chore:` Manutenção geral

## Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/leandrodpaula/tutto-mcp-server.git
cd tutto-mcp-server

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instale dependências de desenvolvimento
pip install -e ".[dev]"

# Execute os testes
pytest

# Verifique o código
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Processo de Review

- Todos os PRs precisam de pelo menos uma aprovação
- Os testes de CI devem passar
- O código deve estar formatado corretamente
- A documentação deve estar atualizada

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros da comunidade

## Dúvidas?

Se tiver dúvidas sobre como contribuir, abra uma issue ou entre em contato através do email: leandrodpaula@example.com

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a Licença MIT.
