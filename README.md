# Church Manage API

API HTTP para gestão de igrejas. A versão atual implementa o cadastro inicial de uma igreja,
incluindo sua congregação sede, o primeiro administrador, o vínculo administrativo e as
configurações padrão.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Stack tecnológica](#stack-tecnológica)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Banco de dados](#banco-de-dados)
- [API](#api)
- [Testes e qualidade](#testes-e-qualidade)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Documentação](#documentação)
- [Limitações atuais](#limitações-atuais)

## Funcionalidades

- Cadastro público de igreja por `POST /api/v1/churches`.
- Criação da congregação sede e do primeiro administrador.
- Criação do vínculo do administrador e das configurações iniciais da igreja.
- Validação de CNPJ, e-mail, telefone, slug e fuso horário no domínio.
- Detecção de e-mail, slug e CNPJ duplicados.
- Hash de senhas com Argon2.
- Verificação de e-mail por token opaco, armazenado somente como hash.
- Sessões com access token JWT curto e refresh token opaco rotativo em cookie HttpOnly.
- Autorização RBAC com permissões explícitas e isolamento por igreja.
- Detecção de reutilização de refresh token com revogação da sessão.
- Auditoria persistente de eventos de autenticação, sessão e autorização.
- Rate limiting em login, verificação de e-mail e renovação da sessão.
- Persistência opcional em PostgreSQL com transação atômica para o cadastro completo.
- Respostas tipadas e documentação OpenAPI.

## Arquitetura

O projeto utiliza um monólito modular orientado por casos de uso e organizado segundo Clean
Architecture:

- `domain`: entidades, value objects e regras de negócio;
- `application`: DTOs, casos de uso, contratos de repositórios e demais portas;
- `infrastructure`: implementações técnicas dos contratos internos;
- `presentation`: rotas HTTP, schemas e tradução de erros.

As dependências são compostas com Dependency Injector no composition root em
`src/app/container.py`. O domínio não depende do FastAPI nem das implementações de
infraestrutura.

## Stack tecnológica

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python 3.12 ou superior |
| API | FastAPI e Uvicorn |
| Validação HTTP | Pydantic 2 |
| Injeção de dependências | Dependency Injector |
| Hash de senha | Argon2 |
| Persistência | SQLAlchemy 2 assíncrono e SQL PostgreSQL versionado |
| Banco de dados | PostgreSQL com asyncpg |
| Gerenciamento de dependências | uv |
| Testes | Pytest e pytest-asyncio |
| Qualidade | Ruff e Pyright |

## Requisitos

- Python 3.12 ou superior.
- [uv](https://docs.astral.sh/uv/) instalado.
- Docker com Compose para executar o PostgreSQL local de testes.

O backend em memória continua disponível para desenvolvimento e testes sem banco.

## Instalação

Clone o repositório e entre no diretório do projeto:

```bash
git clone https://github.com/MiqueiasGFernandes/church-manage-api.git
cd church-manage-api
```

Crie o ambiente virtual e instale as dependências, incluindo as ferramentas de
desenvolvimento:

```bash
uv sync
```

## Configuração

Use o arquivo `.env.example` como referência e exporte as variáveis quando quiser usar
PostgreSQL:

```bash
export PERSISTENCE_BACKEND=postgresql
export DATABASE_URL=postgresql+asyncpg://church_manage:church_manage@localhost:5433/church_manage_test
```

| Variável | Valor padrão | Descrição |
|---|---|---|
| `APP_ENV` | `development` | Ambiente explícito: `development`, `test` ou `production`. Produção ativa validação fail-fast de segurança. |
| `PERSISTENCE_BACKEND` | `memory` | Use `postgresql` para ativar o repository SQLAlchemy. |
| `DATABASE_URL` | vazio | URL assíncrona no formato `postgresql+asyncpg://...`. |
| `AUTH_TOKEN_SECRET` | aleatório por processo | Segredo HMAC Base64 URL-safe. Em produção deve ser explícito, estável, diverso e representar ao menos 32 bytes. |
| `AUTH_COOKIE_SECURE` | `false` | Use `true` em produção HTTPS para proteger o refresh cookie. |
| `EMAIL_BACKEND` | `memory` | Use `smtp` para entregar verificações fora de testes/desenvolvimento. |
| `SMTP_HOST` / `SMTP_PORT` | vazio / `587` | Servidor SMTP usado pelo adapter de e-mail. |
| `SMTP_SENDER` | vazio | Remetente das mensagens de verificação. |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | vazio | Credenciais SMTP, quando exigidas. |
| `SMTP_USE_TLS` | `true` | Ativa STARTTLS no SMTP. |
| `PUBLIC_APP_URL` | vazio | URL do frontend usada no link de confirmação. |

Com `APP_ENV=production`, a aplicação interrompe a inicialização se PostgreSQL e
`DATABASE_URL`, segredo HMAC seguro, cookie `Secure`, SMTP com TLS ou
`PUBLIC_APP_URL` HTTPS não estiverem configurados. Gere um segredo compatível com:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

O processo precisa receber essas variáveis de ambiente; o projeto não carrega arquivos `.env`
automaticamente.

## Execução

Inicie o servidor de desenvolvimento:

```bash
uv run uvicorn --app-dir src app.main:app --reload
```

A API ficará disponível em `http://localhost:8000`.

## Banco de dados

Suba o PostgreSQL local de testes:

```bash
docker compose up -d postgres
```

O container executa automaticamente `scripts/init-db.sql` ao inicializar o banco. Confira o
estado do serviço:

```bash
docker compose ps
```

Para encerrar e descartar os dados temporários:

```bash
docker compose down
```

O cadastro persiste igreja, endereço, congregação sede, administrador, vínculo e configurações
na mesma transação. Constraints de e-mail, slug, documento e vínculo protegem conflitos
concorrentes.

## API

Com a aplicação em execução:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI gerado pela aplicação: `http://localhost:8000/openapi.json`

O contrato versionado está em [`docs/openapi/openapi.yaml`](docs/openapi/openapi.yaml). Ele
contém os schemas, exemplos e respostas dos endpoints de cadastro, autenticação e autorização.

Fluxos de identidade disponíveis:

- `POST /api/v1/auth/verify-email` confirma o token de uso único;
- `POST /api/v1/auth/verify-email/resend` reenvia a confirmação com resposta neutra;
- `POST /api/v1/auth/forgot-password` solicita recuperação sem enumerar contas;
- `POST /api/v1/auth/reset-password` redefine a senha e revoga as sessões;
- `POST /api/v1/auth/change-password` altera a senha autenticada;
- `POST /api/v1/auth/login` cria a sessão e define o refresh cookie;
- `POST /api/v1/auth/refresh` rotaciona o refresh token;
- `POST /api/v1/auth/logout` revoga a sessão atual;
- `POST /api/v1/auth/logout-all` revoga todas as sessões do usuário;
- `GET /api/v1/auth/sessions` lista sessões ativas;
- `DELETE /api/v1/auth/sessions/{session_id}` revoga uma sessão própria;
- `GET /api/v1/auth/me` retorna a identidade e os vínculos ativos;
- `GET /api/v1/churches/{church_id}/me` exige `church:read` naquela igreja.

## Testes e qualidade

Execute a suíte de testes:

```bash
uv run pytest
```

Com o PostgreSQL do Compose em execução, valide o fluxo real de persistência:

```bash
PERSISTENCE_BACKEND=postgresql \
DATABASE_URL=postgresql+asyncpg://church_manage:church_manage@localhost:5433/church_manage_test \
uv run pytest tests/integration/test_register_church_http.py
```

Verifique o lint:

```bash
uv run ruff check .
```

Verifique a formatação do código-fonte e dos testes:

```bash
uv run ruff format --check src tests
```

Execute a análise estática de tipos em modo estrito:

```bash
uv run pyright
```

O hook executa a suíte completa e exige cobertura mínima de 91%. Como os testes E2E usam o
PostgreSQL real, mantenha o serviço de teste ativo:

```bash
docker compose up -d postgres
```

Instale o hook antes de realizar commits:

```bash
uv run pre-commit install
```

Para executar o hook manualmente em todos os arquivos:

```bash
uv run pre-commit run --all-files
```

Para aplicar a formatação em `src` e `tests`:

```bash
uv run ruff format src tests
```

## Estrutura do projeto

```text
.
├── docs/
│   └── openapi/
├── src/
│   ├── app/
│   └── modules/
│       └── organizations/
│           ├── application/
│           ├── domain/
│           ├── infrastructure/
│           └── presentation/
├── tests/
│   ├── integration/
│   └── unit/
├── scripts/
│   └── init-db.sql
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## Documentação

- [Contrato OpenAPI](docs/openapi/openapi.yaml)

## Limitações atuais

- O backend em memória perde os dados quando o processo é reiniciado; use PostgreSQL para
  persistência durável.
- A suíte Python valida mappers e transações; o schema SQL deve ser validado no PostgreSQL
  local fornecido pelo Docker Compose.
- O repositório não possui uma licença declarada.
