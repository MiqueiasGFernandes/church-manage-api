# Workflow de testes E2E via HTTP

## 1. Descobrir o comportamento

1. Ler `AGENTS.md` e localizar requisitos, critérios de aceite, regras de domínio, ADRs e contrato OpenAPI relacionados.
2. Inspecionar rota, schemas, mapeamento de erros, caso de uso, persistência e testes existentes do módulo.
3. Formular cada cenário como uma regra observável pelo cliente da API:
   - estado inicial e identidade do ator;
   - requisição HTTP;
   - status, headers e corpo esperados;
   - estado observável após a operação;
   - comportamento proibido ou invariante preservada.
4. Priorizar fluxos críticos e regressões reais. Não duplicar validações triviais já cobertas adequadamente por testes unitários ou de integração.

## 2. Definir a fronteira E2E

- Entrar sempre pela API HTTP com `httpx.AsyncClient`.
- Preferir `ASGITransport(app=app)` para testar a aplicação FastAPI no mesmo processo, salvo quando o requisito exigir servidor, rede ou ciclo de vida reais.
- Usar o composition root real. Não instanciar nem chamar diretamente casos de uso, repositories ou entidades para executar a ação sob teste.
- Não mockar domínio, aplicação, rota, repository ou Unit of Work. Substituir somente fronteiras externas não determinísticas, como e-mail ou pagamentos, pelos mecanismos oficiais de injeção de dependência.
- Preparar e verificar o cenário por endpoints públicos sempre que isso mantiver o teste claro. Consultar diretamente o banco apenas para criar pré-condições sem API disponível, limpar dados ou confirmar efeitos que não são observáveis por HTTP.
- Não acessar serviços externos reais nem depender da ordem de execução dos testes.

## 3. Projetar os cenários

Para cada regra relevante, considerar:

1. caminho feliz e resposta pública;
2. violação da regra e erro HTTP estável;
3. ausência de efeitos parciais após falha;
4. repetição da requisição quando houver requisito de idempotência;
5. autenticação, autorização e permissões;
6. isolamento multi-tenant: um ator da igreja A não acessa nem altera recursos da igreja B;
7. limites e transições de estado relevantes;
8. proteção de dados sensíveis em corpos e mensagens de erro.

Não afirmar regras apenas por status genérico. Validar o código de erro, campos relevantes da resposta e o estado final necessário para demonstrar o comportamento.

## 4. Organizar fixtures e dados

- Manter testes E2E em `tests/e2e/`, salvo convenção diferente já consolidada no repositório.
- Centralizar fixtures reutilizáveis em `tests/e2e/conftest.py` apenas quando houver reutilização real.
- Criar um cliente assíncrono tipado, por exemplo:

```python
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def api_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
```

- Usar builders ou factories tipados para payloads válidos. Alterar somente o campo relevante nos casos inválidos.
- Gerar identificadores e valores únicos por teste para permitir execução isolada e paralela.
- Não incluir segredos reais. Senhas e tokens de teste devem ser obviamente fictícios.
- Limpar somente as tabelas ou registros pertencentes ao cenário. Quando `TRUNCATE` for a convenção necessária, executá-lo antes e depois do escopo e preservar a ordem segura entre tabelas.
- Usar PostgreSQL configurado para testes. Nunca apontar fixtures destrutivas para banco de desenvolvimento ou produção.

## 5. Escrever o teste

- Usar Arrange, Act e Assert, com nome que expresse o comportamento de negócio.
- Anotar integralmente funções, fixtures, payloads e estruturas JSON. Usar `TypedDict`, modelos Pydantic ou validação explícita em vez de `Any` e `cast` para esconder tipos desconhecidos.
- Realizar a ação por HTTP:

```python
async def test_rejects_duplicate_church_document(
    api_client: AsyncClient,
) -> None:
    request_payload: ChurchRegistrationPayload = church_payload()

    first_response = await api_client.post("/api/v1/churches", json=request_payload)
    duplicate_response = await api_client.post("/api/v1/churches", json=request_payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["code"] == "church_document_already_registered"
```

- Encadear chamadas HTTP quando a própria API puder montar e observar o fluxo completo.
- Comparar somente campos determinísticos. Para UUIDs e timestamps, validar formato e relações em vez de fixar valores frágeis.
- Verificar que respostas e erros não expõem senha, hash, token, SQL, nomes de tabelas ou detalhes internos.
- Não testar detalhes como quantidade de chamadas a métodos internos, classes concretas resolvidas ou formato ORM.

## 6. Fazer TDD e diagnosticar falhas

1. Adicionar ou ajustar um cenário por vez.
2. Executá-lo e confirmar que falha pelo motivo esperado quando representar comportamento ainda ausente ou uma regressão reproduzida.
3. Se a tarefa incluir implementação, fazer a menor alteração de produção necessária usando a skill apropriada à camada afetada.
4. Reexecutar o teste específico até passar.
5. Executar o conjunto E2E e os testes correlatos para detectar efeitos colaterais.

Não enfraquecer assertions, aceitar múltiplos status ou pular testes para mascarar falhas. Distinguir defeito do produto, ambiente mal configurado e expectativa incorreta antes de alterar código.

## 7. Validar

Adaptar os caminhos e variáveis à configuração do repositório. Executar, no mínimo:

```bash
uv run pytest tests/e2e/<arquivo>.py -q
uv run ruff format --check tests/e2e
uv run ruff check tests/e2e
uv run pyright
```

Depois, executar a suíte completa quando o custo for aceitável:

```bash
uv run pytest
```

Se PostgreSQL for necessário, iniciar o serviço e aplicar o SQL canônico conforme as instruções do repositório antes do teste. Informar explicitamente qualquer validação não executada e o risco restante.

## 8. Critérios de conclusão

- O teste entra pela API usando `httpx` e cobre uma regra de negócio identificável.
- A composição interna relevante é real e as substituições limitam-se a fronteiras externas.
- O teste é determinístico, isolado, fortemente tipado e independente da ordem.
- Persistência e isolamento por tenant usam PostgreSQL real quando aplicáveis.
- Assertions demonstram resposta pública e efeitos relevantes, inclusive ausência de efeitos em falhas.
- Teste específico, Ruff e Pyright passam; a suíte completa passa ou sua não execução é justificada.
