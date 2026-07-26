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
- [Execução](#execução)
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
- Publicação do evento de domínio `ChurchRegistered`.
- Respostas tipadas e documentação OpenAPI.

## Arquitetura

O projeto utiliza um monólito modular orientado por casos de uso e organizado segundo Clean
Architecture:

- `domain`: entidades, value objects, eventos e regras de negócio;
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
| Gerenciamento de dependências | uv |
| Testes | Pytest e pytest-asyncio |
| Qualidade | Ruff e Pyright |

## Requisitos

- Python 3.12 ou superior.
- [uv](https://docs.astral.sh/uv/) instalado.

O estado atual da aplicação não exige banco de dados nem variáveis de ambiente.

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

## Execução

Inicie o servidor de desenvolvimento:

```bash
uv run uvicorn --app-dir src app.main:app --reload
```

A API ficará disponível em `http://localhost:8000`.

## API

Com a aplicação em execução:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI gerado pela aplicação: `http://localhost:8000/openapi.json`

O contrato versionado está em [`docs/openapi/openapi.yaml`](docs/openapi/openapi.yaml). Ele
contém os schemas, exemplos e respostas possíveis do endpoint de cadastro.

## Testes e qualidade

Execute a suíte de testes:

```bash
uv run pytest
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

Instale o hook que executa os testes unitários e exige cobertura mínima de 91% antes de cada
commit:

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
├── pyproject.toml
└── uv.lock
```

## Documentação

- [Contrato OpenAPI](docs/openapi/openapi.yaml)

## Limitações atuais

- A persistência e a publicação de eventos usam implementações em memória.
- Os dados são perdidos quando o processo da aplicação é reiniciado.
- Ainda não há migrations, configuração de banco de dados ou suporte a Docker no repositório.
- O repositório não possui uma licença declarada.
