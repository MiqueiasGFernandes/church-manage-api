# AGENTS.md

## 1. Objetivo

Este documento define como agentes de IA devem trabalhar neste repositório.

Ele descreve:

* padrões técnicos obrigatórios;
* regras arquiteturais;
* critérios de qualidade;
* convenções de implementação;
* restrições para alterações automáticas;
* comandos de validação antes da conclusão de uma tarefa.

Este documento não deve duplicar requisitos de negócio, modelagem de domínio ou decisões arquiteturais extensas já registradas em outros arquivos.

Consulte também:

```text
docs/domain-model.md
docs/sdd.md
docs/architecture/
docs/adr/
README.md
```

Quando houver conflito, utilize a seguinte ordem de prioridade:

```text
1. Requisitos funcionais e critérios de aceite da tarefa
2. AGENTS.md
3. ADRs aceitos
4. SDD e documentação arquitetural
5. Modelagem de domínio
6. Padrões consolidados no código existente
7. Convenções oficiais das ferramentas
```

O agente não deve alterar silenciosamente uma decisão arquitetural existente.

---

## 2. Contexto técnico

O projeto é um SaaS multi-tenant para gestão de igrejas.

O backend utiliza:

```text
Python 3.12.x
FastAPI
Pydantic v2
SQLAlchemy 2.x
PostgreSQL
Pytest
Ruff
Pyright
Docker
```

A arquitetura padrão é:

```text
Monólito modular
Clean Architecture
DDD aplicado onde houver regras de negócio relevantes
Arquitetura orientada a casos de uso
Tipagem estática forte
```

O projeto deve permanecer portável entre provedores de infraestrutura.

Evite dependências desnecessárias de recursos exclusivos de uma cloud ou plataforma.

---

# 3. Regras gerais para agentes

Antes de alterar qualquer arquivo, o agente deve:

1. identificar o módulo afetado;
2. localizar os requisitos e regras de domínio relacionados;
3. analisar os padrões já utilizados no módulo;
4. verificar ADRs que possam restringir a implementação;
5. identificar os testes existentes;
6. definir a menor alteração capaz de atender à tarefa.

O agente deve preferir alterações:

* pequenas;
* incrementais;
* testáveis;
* reversíveis;
* compatíveis com o código existente.

Não realizar refatorações amplas que não sejam necessárias para a tarefa solicitada.

Não substituir tecnologias, bibliotecas ou padrões existentes sem justificativa explícita.

---

# 4. Clean Architecture

## 4.1 Regra de dependência

As dependências devem apontar para as camadas mais internas.

```text
Presentation
    ↓
Application
    ↓
Domain

Infrastructure
    ↓
Application
    ↓
Domain
```

A camada de domínio deve permanecer independente.

## 4.2 Camadas

### Domain

Contém:

* entidades;
* agregados;
* value objects;
* serviços de domínio;
* políticas;
* eventos de domínio;
* exceções de negócio;
* interfaces de repositório quando forem parte do vocabulário do domínio.

Não pode depender de:

* FastAPI;
* Pydantic;
* SQLAlchemy;
* bibliotecas HTTP;
* SDKs externos;
* banco de dados;
* sistema de arquivos;
* frameworks de filas;
* provedores de e-mail;
* bibliotecas específicas de cloud.

### Application

Contém:

* casos de uso;
* commands;
* queries;
* DTOs internos;
* portas de entrada e saída;
* interfaces para serviços externos;
* coordenação de transações;
* autorização de casos de uso;
* orquestração entre agregados.

A camada de aplicação pode depender do domínio.

Não deve depender diretamente de:

* modelos SQLAlchemy;
* clientes HTTP concretos;
* SDKs externos;
* detalhes de FastAPI;
* detalhes do banco de dados.

### Infrastructure

Contém:

* implementação de repositórios;
* modelos SQLAlchemy;
* configuração de banco;
* implementação de storage;
* provedores de e-mail;
* hashing de senha;
* autenticação;
* logging;
* filas;
* integrações externas;
* adaptadores concretos.

A infraestrutura implementa portas definidas nas camadas internas.

### Presentation

Contém:

* rotas FastAPI;
* schemas de request e response;
* resolução de dependências;
* autenticação HTTP;
* conversão de erros em respostas HTTP;
* documentação OpenAPI.

A camada HTTP não deve conter regras de negócio.

---

## 4.3 Dependências proibidas

Exemplos proibidos:

```python
# Domínio importando framework HTTP
from fastapi import HTTPException
```

```python
# Caso de uso importando modelo ORM
from modules.members.infrastructure.persistence.models import MemberModel
```

```python
# Entidade de domínio herdando modelo Pydantic
class Member(BaseModel):
    ...
```

```python
# Controller implementando regra de negócio
if request.status == "pending":
    request.status = "approved"
```

Exemplos corretos:

```python
class RegistrationRequest:
    def approve(self, approved_by: UserId) -> None:
        ...
```

```python
class ApproveRegistrationRequest:
    def __init__(
        self,
        repository: RegistrationRequestRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        ...
```

```python
@router.post("/{request_id}/approval")
async def approve_request(
    request_id: UUID,
    use_case: ApproveRegistrationRequestDependency,
) -> ApprovalResponse:
    result = await use_case.execute(...)
    return ApprovalResponse.from_result(result)
```

---

# 5. Estrutura de módulos

Organize o projeto por contexto de negócio.

```text
src/
├── app/
│   ├── main.py
│   ├── settings.py
│   ├── dependencies.py
│   └── lifecycle.py
│
├── modules/
│   ├── identity/
│   ├── organizations/
│   ├── members/
│   ├── community/
│   ├── events/
│   ├── communication/
│   └── finance/
│
├── shared/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
│
└── tests/
```

Cada módulo deve seguir, quando aplicável:

```text
module/
├── domain/
│   ├── entities/
│   ├── aggregates/
│   ├── value_objects/
│   ├── events/
│   ├── exceptions/
│   ├── policies/
│   └── repositories/
│
├── application/
│   ├── commands/
│   ├── queries/
│   ├── use_cases/
│   ├── dto/
│   ├── repositories/
│   └── ports/
│
├── infrastructure/
│   ├── persistence/
│   ├── repositories/
│   ├── mappers/
│   └── providers/
│
└── presentation/
    └── http/
        ├── routes/
        ├── schemas/
        └── dependencies.py
```

Evite estruturas globais organizadas apenas por tipo técnico:

```text
controllers/
services/
models/
repositories/
schemas/
```

## 5.1 Granularidade dos arquivos da camada de aplicação

Na camada de aplicação, mantenha responsabilidades arquiteturais distintas em
arquivos separados. Em especial:

* DTOs de entrada e saída devem ficar em módulos de `application/dto/`;
* contratos de repository devem ficar em módulos de `application/repositories/`;
* `application/ports/` deve conter apenas contratos de serviços externos e
  outras portas que não representem persistência;
* implementações de casos de uso devem ficar em módulos de `application/use_cases/`;
* erros específicos da aplicação devem ficar em módulos de `application/errors/`
  quando sua quantidade ou reutilização justificar a extração.

Não concentre DTOs, portas e implementação do caso de uso em um único arquivo.
A separação deve representar responsabilidades reais e evitar arquivos
demasiadamente grandes.

Cada caso de uso deve possuir obrigatoriamente seu próprio arquivo em
`application/use_cases/`, com nome em `snake_case` correspondente à intenção.
Por exemplo:

```text
application/use_cases/authenticate_user.py
application/use_cases/refresh_session.py
application/use_cases/logout_session.py
```

Não agrupe múltiplos casos de uso em módulos genéricos por assunto, como
`auth.py`, `users.py`, `members.py` ou `services.py`. Políticas e regras
compartilhadas podem ser extraídas para módulos próprios quando representarem
um conceito reutilizável real, sem transformar esses módulos em coleções de
casos de uso.

## 5.2 Nomenclatura das interfaces

Todas as interfaces devem usar o prefixo `I` no nome da classe, incluindo casos
de uso, repositories, gateways, serviços e demais portas. Exemplos:
`IRegisterChurch`, `IRegistrationRepository`, `IUnitOfWork` e `IEventPublisher`.

O nome do arquivo não deve usar o prefixo `i_`; deve acompanhar o conceito, como
`domain/use_cases/register_church.py` ou
`application/repositories/registration_repository.py`.

## 5.3 Contratos dos casos de uso e DIP

Cada implementação em `application/use_cases/<caso_de_uso>.py` deve possuir uma
interface de entrada correspondente, definida como `Protocol` em
`domain/use_cases/<caso_de_uso>.py`.

Exemplo:

```text
domain/use_cases/authenticate_user.py
    IAuthenticateUser

application/use_cases/authenticate_user.py
    AuthenticateUser
```

O contrato deve expor a mesma operação pública da implementação, com parâmetros
e retorno integralmente tipados. Seus tipos não podem introduzir dependências de
framework, infraestrutura ou apresentação no domínio.

Controllers, handlers, routers e demais consumidores externos devem depender da
interface `I<NomeDoCasoDeUso>`, nunca da implementação concreta. A implementação
concreta deve ser referenciada apenas no Composition Root e nos testes unitários
que exercitam diretamente o caso de uso.

Toda classe concreta de caso de uso deve implementar explicitamente sua
interface de domínio por herança, além de preservar integralmente a assinatura
do contrato. A conformidade deve ser verificada pelo Pyright.

Exemplo:

```python
class AuthenticateUser(IAuthenticateUser):
    async def execute(self, email: str, password: str) -> TokenPair:
        ...
```

Não depender somente da conformidade estrutural implícita do `Protocol`. A
implementação explícita torna o contrato arquitetural visível no código.

O container do Dependency Injector deve associar a interface à implementação
concreta e fornecer o contrato à camada de apresentação.

Não criar módulos agregadores ou arquivos-barrel que reexportem vários casos de
uso e restaurem o acoplamento removido. Cada consumidor deve importar o contrato
ou a implementação diretamente do módulo da intenção utilizada.

---

# 6. Tipagem forte em Python

A tipagem estática é obrigatória em todo código de produção.

O projeto deve ser validado com Pyright em modo estrito ou configuração equivalente.

Nenhum código de produção ou teste pode conter tipos inferidos como `Unknown`, `Unknown | ...`, `partially unknown` ou qualquer variação equivalente reportada pelo Pyright.

Todo valor, parâmetro, retorno, atributo, coleção, callback, dependência, resultado de biblioteca externa e estrutura intermediária deve possuir um tipo conhecido, explícito e verificável estaticamente.

É proibido concluir uma tarefa enquanto o Pyright reportar diagnósticos relacionados a tipos desconhecidos, incluindo, mas não se limitando a:

```text
reportUnknownArgumentType
reportUnknownLambdaType
reportUnknownMemberType
reportUnknownParameterType
reportUnknownVariableType
reportMissingTypeArgument
reportUntypedBaseClass
```

Esses diagnósticos não devem ser silenciados, rebaixados ou ignorados para permitir a conclusão da tarefa. A causa deve ser corrigida por meio de tipagem adequada, criação de contratos explícitos, validação de fronteira, stubs, wrappers tipados ou substituição da dependência problemática.

## 6.1 Regras obrigatórias

Toda função deve declarar:

* tipos dos parâmetros;
* tipo de retorno;
* tipos genéricos;
* tipos de atributos públicos;
* tipos de dependências injetadas.

Correto:

```python
async def get_member(
    church_id: ChurchId,
    member_id: MemberId,
) -> Member | None:
    ...
```

Incorreto:

```python
async def get_member(church_id, member_id):
    ...
```

Não utilizar `Any` como atalho.

```python
# Evitar
def process(payload: Any) -> Any:
    ...
```

Quando uma dependência externa retornar dados não tipados, validar e converter imediatamente.

```python
class ProviderResponse(BaseModel):
    message_id: str
    status: Literal["accepted", "rejected"]
```

Não propagar valores desconhecidos para o restante da aplicação.

Incorreto:

```python
response = external_client.send(payload)
message_id = response["message_id"]
```

Correto:

```python
raw_response: object = external_client.send(payload)
response = ProviderResponse.model_validate(raw_response)
message_id: str = response.message_id
```

Quando uma biblioteca não fornecer tipos completos, o agente deve, conforme o caso:

* instalar stubs oficiais ou mantidos;
* criar um wrapper tipado na camada de infraestrutura;
* definir `Protocol`, `TypedDict`, `dataclass` ou modelo Pydantic para o contrato;
* validar retornos externos como `object` antes de convertê-los;
* criar stubs locais `.pyi` quando não houver alternativa adequada;
* substituir a biblioteca por outra com suporte de tipagem, quando essa decisão estiver autorizada.

Não utilizar `Any`, `cast`, `# type: ignore`, configuração permissiva do Pyright ou anotações genéricas apenas para transformar um tipo desconhecido em aparentemente conhecido.

Uma coleção deve declarar tanto o tipo do contêiner quanto o tipo de seus elementos.

Incorreto:

```python
items = []
metadata: dict = {}
```

Correto:

```python
items: list[Member] = []
metadata: dict[str, str] = {}
```

Callbacks, decorators e funções de ordem superior também devem preservar integralmente os tipos de entrada e saída, utilizando `ParamSpec`, `TypeVar`, `Concatenate` ou protocolos de callback quando necessário.

## 6.2 Tipos de domínio

Evite utilizar `str` ou `UUID` indistintamente para conceitos diferentes.

Preferir tipos nominais:

```python
from typing import NewType
from uuid import UUID

ChurchId = NewType("ChurchId", UUID)
MemberId = NewType("MemberId", UUID)
UserId = NewType("UserId", UUID)
```

Ou value objects:

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MemberId:
    value: UUID
```

O projeto deve adotar uma das duas estratégias e mantê-la consistente.

Value objects são preferíveis quando houver:

* validação;
* normalização;
* comportamento;
* serialização específica;
* invariantes próprias.

## 6.3 Protocols

Utilize `Protocol` para portas e contratos estruturais.

```python
from typing import Protocol


class MemberRepository(Protocol):
    async def get_by_id(
        self,
        church_id: ChurchId,
        member_id: MemberId,
    ) -> Member | None:
        ...

    async def save(self, member: Member) -> None:
        ...
```

Não crie classes base abstratas apenas para compartilhar uma assinatura, salvo quando houver necessidade real de comportamento comum.

## 6.4 Generics

Use generics quando eliminarem duplicação de tipos sem esconder regras de negócio.

```python
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PaginatedResult(Generic[T]):
    items: tuple[T, ...]
    next_cursor: str | None
```

Evite abstrações genéricas como:

```python
GenericRepository[Entity]
GenericCrudService[Entity]
```

quando elas impedirem a expressão de operações específicas do domínio.

## 6.5 Collections

Prefira interfaces imutáveis em assinaturas públicas quando a mutabilidade não for necessária.

```python
from collections.abc import Sequence

def calculate_total(entries: Sequence[FinancialEntry]) -> Money:
    ...
```

Para resultados imutáveis:

```python
tuple[Member, ...]
```

Evite retornar listas mutáveis internas de agregados.

## 6.6 Optional

Use `T | None` apenas quando a ausência for válida no domínio.

```python
email: Email | None
```

Não transforme valores obrigatórios em opcionais apenas para facilitar criação de objetos incompletos.

Evite:

```python
class Member:
    id: MemberId | None
    church_id: ChurchId | None
    name: str | None
```

Prefira factories que garantam objetos válidos.

## 6.7 Literal e Enum

Use `Enum`, `StrEnum` ou `Literal` para conjuntos fechados.

```python
from enum import StrEnum


class MemberStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSFERRED = "transferred"
```

Não espalhe strings mágicas:

```python
if member.status == "active":
    ...
```

## 6.8 Type narrowing

Utilize verificações explícitas para narrowing.

```python
member = await repository.get_by_id(church_id, member_id)

if member is None:
    raise MemberNotFound(member_id)

member.activate()
```

Não utilize `cast` para esconder inconsistências de projeto.

`cast` só deve ser usado quando o tipo for garantido por uma condição que a ferramenta de análise não consiga inferir.

## 6.9 Type ignores

Evite:

```python
# type: ignore
```

Quando inevitável, especifique o código e documente o motivo.

```python
value = library_call()  # type: ignore[no-untyped-call] - biblioteca sem stubs
```

Não utilize `# type: ignore` genérico.

---

# 7. Modelagem de domínio no código

A modelagem detalhada está definida em `docs/domain-model.md`.

Este documento deve apenas orientar sua implementação.

## 7.1 Entidades e agregados

Entidades de domínio:

* não devem ser modelos ORM;
* não devem ser schemas Pydantic;
* devem proteger invariantes;
* devem expor comportamentos significativos;
* não devem permitir alteração arbitrária de estado.

Evitar:

```python
member.status = MemberStatus.INACTIVE
```

Preferir:

```python
member.deactivate(reason=reason, occurred_at=clock.now())
```

## 7.2 Value objects

Value objects devem ser:

* imutáveis;
* validados no momento da criação;
* comparáveis por valor;
* independentes de framework.

```python
@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()

        if not is_valid_email(normalized):
            raise InvalidEmail(normalized)

        object.__setattr__(self, "value", normalized)
```

## 7.3 Exceções de domínio

Exceções devem representar situações de negócio.

```python
class RegistrationRequestAlreadyProcessed(DomainError):
    ...
```

Evitar exceções genéricas para regras conhecidas:

```python
raise ValueError("Cannot approve request")
```

A camada HTTP deve converter exceções de domínio e aplicação em respostas apropriadas.

## 7.4 Eventos de domínio

Eventos representam fatos já ocorridos.

```python
@dataclass(frozen=True, slots=True)
class RegistrationRequestApproved:
    request_id: RegistrationRequestId
    member_id: MemberId
    approved_by: UserId
    occurred_at: datetime
```

Nomeie eventos no passado.

Correto:

```text
MemberRegistered
RegistrationRequestApproved
FinancialEntryReversed
```

Incorreto:

```text
RegisterMember
ApproveRequest
ReverseEntry
```

---

# 8. Casos de uso

Cada caso de uso deve representar uma intenção clara.

Exemplos:

```text
RegisterMember
ApproveRegistrationRequest
CreateCellGroup
RegisterContribution
PublishEvent
```

Um caso de uso deve:

1. validar autorização;
2. carregar agregados;
3. executar comportamentos de domínio;
4. persistir alterações;
5. coordenar a transação;
6. publicar eventos quando aplicável;
7. retornar um resultado tipado.

Exemplo:

```python
@dataclass(frozen=True, slots=True)
class ApproveRegistrationCommand:
    church_id: ChurchId
    request_id: RegistrationRequestId
    approved_by: UserId


@dataclass(frozen=True, slots=True)
class ApproveRegistrationResult:
    member_id: MemberId


class ApproveRegistrationRequest:
    def __init__(
        self,
        requests: RegistrationRequestRepository,
        members: MemberRepository,
        authorization: AuthorizationService,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ) -> None:
        self._requests = requests
        self._members = members
        self._authorization = authorization
        self._unit_of_work = unit_of_work
        self._clock = clock

    async def execute(
        self,
        command: ApproveRegistrationCommand,
    ) -> ApproveRegistrationResult:
        ...
```

Não utilizar classes genéricas chamadas apenas de:

```text
MemberService
FinanceService
EventService
```

quando elas acumularem múltiplas responsabilidades.

---

# 9. Commands, queries e DTOs

## 9.1 Commands

Commands representam intenções de mudança.

Devem ser imutáveis.

```python
@dataclass(frozen=True, slots=True)
class RegisterContributionCommand:
    church_id: ChurchId
    account_id: FinancialAccountId
    amount: Money
    occurred_at: datetime
    registered_by: UserId
```

## 9.2 Queries

Queries não devem alterar estado.

```python
@dataclass(frozen=True, slots=True)
class ListMembersQuery:
    church_id: ChurchId
    congregation_id: CongregationId | None
    cursor: str | None
    limit: int
```

## 9.3 DTOs

DTOs de aplicação não devem ser reutilizados automaticamente como schemas HTTP.

A camada HTTP deve converter:

```text
HTTP request
→ schema Pydantic
→ command/query
→ caso de uso
→ resultado
→ HTTP response
```

Essa separação evita que mudanças na API externa contaminem o núcleo da aplicação.

---

# 10. Pydantic

Pydantic deve ser utilizado nas fronteiras da aplicação.

Use para:

* requests HTTP;
* responses HTTP;
* configurações;
* validação de payloads externos;
* contratos de integração.

Não use Pydantic para entidades de domínio por padrão.

Exemplo:

```python
from pydantic import BaseModel, ConfigDict, Field


class CreateMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=150)
    email: str | None = Field(default=None, max_length=254)
```

Utilize:

```python
model_config = ConfigDict(extra="forbid")
```

em payloads de escrita, salvo quando houver razão explícita para aceitar campos extras.

Não exponha modelos ORM diretamente como respostas HTTP.

---

# 11. Persistência com SQLAlchemy

Utilize SQLAlchemy 2.x com APIs modernas e tipadas.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MemberModel(Base):
    __tablename__ = "members"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    church_id: Mapped[UUID] = mapped_column(index=True)
    name: Mapped[str]
```

Evite APIs legadas:

```python
session.query(MemberModel)
```

Preferir:

```python
statement = select(MemberModel).where(
    MemberModel.church_id == church_id,
    MemberModel.id == member_id,
)

result = await session.execute(statement)
model = result.scalar_one_or_none()
```

## 11.1 Separação ORM e domínio

Modelos ORM e entidades de domínio são objetos distintos.

Utilize mappers explícitos:

```python
class MemberMapper:
    @staticmethod
    def to_domain(model: MemberModel) -> Member:
        ...

    @staticmethod
    def to_model(entity: Member) -> MemberModel:
        ...
```

Não adicione métodos de regra de negócio a modelos SQLAlchemy.

## 11.2 Transações

A transação deve ser controlada pela aplicação através de uma abstração de Unit of Work.

```python
class UnitOfWork(Protocol):
    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
```

Casos de uso não devem executar `commit` diretamente em uma sessão SQLAlchemy concreta.

---

# 12. Schema do banco de dados

Não utilizar ferramentas de migration neste projeto. O schema PostgreSQL deve
ser mantido como SQL puro e versionado em `scripts/`.

O arquivo canônico de criação das tabelas deve:

* ser executável diretamente pelo `psql`;
* possuir constraints e índices nomeados quando forem referenciados pelo código;
* permanecer sincronizado com os modelos SQLAlchemy;
* utilizar comandos idempotentes quando isso não esconder incompatibilidades;
* ser montado no diretório `/docker-entrypoint-initdb.d/` do PostgreSQL local;
* ser validado contra PostgreSQL real antes da conclusão de alterações de schema.

Não utilizar `Base.metadata.create_all()` como mecanismo de atualização ou
inicialização do banco.

---

# 13. Multi-tenancy

O isolamento por tenant é obrigatório.

O identificador padrão é:

```python
church_id
```

Toda entidade persistida pertencente a uma igreja deve possuir `church_id`, salvo a própria entidade `Church`.

## 13.1 Consultas

Correto:

```python
statement = select(MemberModel).where(
    MemberModel.church_id == church_id,
    MemberModel.id == member_id,
)
```

Incorreto:

```python
statement = select(MemberModel).where(
    MemberModel.id == member_id,
)
```

O uso de UUID não elimina a necessidade de filtrar pelo tenant.

## 13.2 Repositórios

Correto:

```python
async def get_by_id(
    self,
    church_id: ChurchId,
    member_id: MemberId,
) -> Member | None:
    ...
```

Incorreto:

```python
async def get_by_id(
    self,
    member_id: MemberId,
) -> Member | None:
    ...
```

## 13.3 Escritas

Ao criar um recurso, o `church_id` deve vir do contexto autenticado ou de um fluxo interno confiável.

Não confiar em `church_id` enviado livremente pelo frontend para operações autenticadas.

## 13.4 Testes obrigatórios

Toda funcionalidade que acessa dados de tenant deve possuir teste demonstrando que:

```text
um usuário da igreja A
não consegue acessar ou modificar
dados da igreja B
```

---

# 14. FastAPI

Rotas devem ser pequenas.

Responsabilidades da rota:

1. validar o request;
2. obter identidade e contexto;
3. construir command ou query;
4. chamar o caso de uso;
5. mapear o resultado;
6. retornar a resposta HTTP.

Exemplo:

```python
@router.post(
    "/registration-requests/{request_id}/approval",
    response_model=ApproveRegistrationResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_registration_request(
    request_id: UUID,
    body: ApproveRegistrationRequestBody,
    actor: AuthenticatedActorDependency,
    use_case: ApproveRegistrationUseCaseDependency,
) -> ApproveRegistrationResponse:
    command = ApproveRegistrationCommand(
        church_id=actor.church_id,
        request_id=RegistrationRequestId(request_id),
        approved_by=actor.user_id,
    )

    result = await use_case.execute(command)

    return ApproveRegistrationResponse(
        member_id=result.member_id.value,
    )
```

Não acessar repositórios diretamente na rota.

Não colocar regras de autorização exclusivamente na rota.

Não retornar exceções internas ao cliente.

---

# 15. Injeção de dependências

O projeto deve utilizar obrigatoriamente a biblioteca **Dependency Injector** (`dependency-injector`) para composição das dependências da aplicação.

Ela é o padrão oficial de Injeção de Dependências do projeto.

Não utilizar outros containers (Injector, Dishka, Punq etc.) sem aprovação por ADR.

Toda dependência deve ser recebida pelo construtor da classe.

Correto:

```python
class RegisterMember:
    def __init__(
        self,
        repository: MemberRepository,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work
        self._clock = clock
```

Incorreto:

```python
class RegisterMember:
    def __init__(self) -> None:
        self._repository = SqlAlchemyMemberRepository(...)
```

Também é proibido criar dependências durante a execução:

```python
async def execute(...) -> None:
    repository = SqlAlchemyMemberRepository(...)
```

## 15.1 Composition Root

Toda composição de objetos deve ocorrer em um único Composition Root utilizando o Dependency Injector.

Exemplo:

```text
src/app/container.py
```

ou

```text
src/infrastructure/dependency_injection/
```

O container é responsável por registrar:

- configurações;
- sessão do banco de dados;
- Unit of Work;
- repositórios;
- gateways;
- serviços externos;
- casos de uso;
- handlers;
- providers compartilhados.

## 15.2 Providers

Utilize os providers do Dependency Injector conforme a responsabilidade:

- `providers.Singleton` para componentes compartilhados e thread-safe.
- `providers.Factory` para objetos sem estado ou que devam ser recriados.
- `providers.Resource` para recursos com ciclo de vida (ex.: conexões).
- `providers.Configuration` para configurações da aplicação.

Escolha o provider mais adequado ao ciclo de vida da dependência.

## 15.3 Integração com FastAPI

A camada HTTP deve apenas resolver dependências registradas no container.

Exemplo:

```python
@router.post("/members")
@inject
async def create_member(
    request: CreateMemberRequest,
    use_case: RegisterMember = Depends(
        Provide[Container.register_member_use_case]
    ),
):
    ...
```

O uso de `Depends()` é permitido apenas para integrar o FastAPI ao Dependency Injector.

Nunca utilize `Depends()` em:

- Domain;
- Application;
- Infrastructure.

## 15.4 Regras obrigatórias

- Toda dependência deve ser injetada pelo construtor.
- Casos de uso devem depender apenas de abstrações (`Protocol`).
- Nunca instanciar implementações concretas dentro das classes.
- Nunca utilizar Service Locator.
- Nunca utilizar Singletons manuais.
- Nunca utilizar variáveis globais para compartilhar dependências.
- Todo objeto compartilhado deve ser registrado no container.
- O container deve ser inicializado apenas durante o bootstrap da aplicação.

# 16. Código assíncrono

Use `async` para operações de I/O:

* banco de dados;
* HTTP;
* armazenamento;
* e-mail;
* filas.

Não use `async` para funções puramente computacionais sem I/O.

Não chame funções bloqueantes dentro do event loop.

Quando uma biblioteca síncrona for inevitável:

* utilizar thread pool;
* encapsular a dependência;
* documentar o motivo;
* avaliar impacto.

Evite misturar sessões SQLAlchemy síncronas e assíncronas no mesmo fluxo.

---

# 17. Tratamento de erros

Defina hierarquia clara de erros.

```python
class ApplicationError(Exception):
    pass


class DomainError(ApplicationError):
    pass


class ResourceNotFound(ApplicationError):
    pass


class PermissionDenied(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass
```

A camada HTTP deve converter erros em respostas consistentes.

Exemplo:

```json
{
  "code": "registration_request_already_processed",
  "message": "A solicitação já foi processada.",
  "details": {}
}
```

Não exponha:

* stack traces;
* mensagens do banco;
* SQL;
* credenciais;
* nomes internos de tabelas;
* detalhes de infraestrutura.

---

# 18. Segurança

## 18.1 Dados sensíveis

Nunca registrar em logs:

* senhas;
* tokens;
* cookies;
* documentos completos;
* dados financeiros sensíveis;
* credenciais;
* segredos;
* payloads completos com informações pessoais.

## 18.2 Senhas

Senhas devem ser armazenadas com hash seguro.

Preferência:

```text
Argon2id
```

Nunca implementar algoritmo próprio de hash.

## 18.3 Segredos

Segredos devem vir de variáveis de ambiente ou secret manager.

Nunca versionar:

```text
.env
private keys
access tokens
database credentials
cloud credentials
```

## 18.4 Autorização

Toda operação protegida deve verificar:

* usuário autenticado;
* tenant;
* permissão;
* escopo do recurso;
* estado atual da entidade.

Não confiar apenas em verificações feitas no frontend.

---

# 19. Datas e horários

Utilize `datetime` com timezone.

Correto:

```python
from datetime import UTC, datetime

now = datetime.now(UTC)
```

Evitar:

```python
datetime.now()
```

Persistir timestamps em UTC.

Converter para o fuso do usuário apenas na apresentação.

Não utilizar `date.today()` diretamente em regras testáveis. Injete uma abstração de relógio:

```python
class Clock(Protocol):
    def now(self) -> datetime:
        ...
```

---

# 20. Valores monetários

Nunca utilize `float` para dinheiro.

Utilize:

* inteiro em centavos; ou
* `Decimal` com precisão definida.

Preferência no domínio:

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "BRL"
```

Ao utilizar `Decimal`, construa a partir de string:

```python
Decimal("10.50")
```

Não:

```python
Decimal(10.50)
```

O banco deve utilizar:

```text
BIGINT para centavos
```

ou:

```text
NUMERIC com escala definida
```

A estratégia deve ser consistente em todo o módulo financeiro.

---

# 21. Logging

Utilize logs estruturados.

Campos recomendados:

```text
timestamp
level
message
request_id
church_id
user_id
resource_id
operation
duration_ms
```

Exemplo:

```python
logger.info(
    "registration_request_approved",
    request_id=str(command.request_id.value),
    church_id=str(command.church_id.value),
    approved_by=str(command.approved_by.value),
)
```

Não utilizar `print` em código de produção.

Mensagens de log devem ser técnicas e estáveis.

Não usar informações sensíveis como parte da mensagem.

---

# 22. Testes

Toda alteração funcional deve possuir testes.

## 22.1 Pirâmide de testes

Priorize:

```text
Muitos testes unitários de domínio e casos de uso
Testes de integração para repositórios e banco
Poucos testes end-to-end para fluxos críticos
```

## 22.2 Testes unitários

Devem testar:

* invariantes;
* transições de estado;
* value objects;
* políticas;
* casos de uso;
* erros de negócio;
* autorização;
* eventos gerados.

Não acessar:

* banco real;
* rede;
* sistema de arquivos;
* provedores externos.

## 22.3 Testes de integração

Devem testar:

* repositórios SQLAlchemy;
* scripts SQL de schema;
* constraints;
* mappers;
* transações;
* isolamento multi-tenant;
* integração com PostgreSQL.

Preferir PostgreSQL real em container em vez de SQLite para testes de persistência.

SQLite possui semântica diferente em:

* tipos;
* transações;
* constraints;
* concorrência;
* JSON;
* índices;
* SQL específico.

## 22.4 Testes end-to-end

Devem cobrir fluxos críticos, como:

```text
criar solicitação pública
aprovar solicitação
criar membro
registrar contribuição
impedir acesso entre tenants
```

## 22.5 Estrutura de testes

Utilize Arrange, Act, Assert.

```python
async def test_approves_pending_registration_request() -> None:
    # Arrange
    request = registration_request_factory.pending()

    # Act
    request.approve(
        approved_by=user_id,
        occurred_at=clock.now(),
    )

    # Assert
    assert request.status is RegistrationStatus.APPROVED
```

## 22.6 Nomenclatura

Nomes devem descrever comportamento.

Preferir:

```python
def test_rejects_approval_when_request_is_already_processed() -> None:
```

Evitar:

```python
def test_approve_2() -> None:
```

---

# 23. Test doubles

Utilize:

* fakes para repositórios;
* stubs para retornos previsíveis;
* spies para verificar interações relevantes;
* mocks apenas quando necessário.

Evite excesso de mocks acoplados à implementação.

Exemplo de fake:

```python
class InMemoryMemberRepository:
    def __init__(self) -> None:
        self._members: dict[tuple[ChurchId, MemberId], Member] = {}

    async def save(self, member: Member) -> None:
        self._members[(member.church_id, member.id)] = member
```

O fake deve respeitar as mesmas regras importantes do repositório real, especialmente isolamento por tenant.

---

# 24. Qualidade de código

O código deve passar por:

```text
Ruff format
Ruff check
Pyright
Pytest
```

Não concluir uma tarefa com:

* erros de lint;
* erros de type checking;
* testes quebrados;
* imports não utilizados;
* código morto;
* comentários temporários;
* `TODO` sem justificativa.

## 24.1 Funções

Funções devem:

* possuir responsabilidade única;
* ter nomes descritivos;
* evitar muitos níveis de indentação;
* evitar parâmetros booleanos ambíguos;
* evitar efeitos colaterais ocultos.

Evitar:

```python
process_member(member, True, False)
```

Preferir:

```python
approve_member_registration(
    member=member,
    notify_member=True,
    create_user_account=False,
)
```

Ou separar os comportamentos.

## 24.2 Comentários

Comentários devem explicar o porquê, não repetir o código.

Incorreto:

```python
# Incrementa tentativas
attempts += 1
```

Correto:

```python
# O provedor pode responder com timeout depois de aceitar a mensagem.
# O idempotency key impede o envio duplicado na próxima tentativa.
attempts += 1
```

## 24.3 Docstrings

Utilize docstrings em:

* APIs públicas;
* abstrações;
* comportamentos não triviais;
* decisões com restrições importantes.

Não é necessário adicionar docstring redundante em métodos óbvios e privados.

---

# 25. Ferramentas

## 25.1 Gerenciamento de dependências

Utilize `uv`.

Comandos esperados:

```bash
uv sync
uv add <package>
uv add --dev <package>
uv run <command>
```

Não editar manualmente o lockfile.

## 25.2 Formatação e lint

```bash
uv run ruff format .
uv run ruff check .
```

Para corrigir automaticamente quando seguro:

```bash
uv run ruff check . --fix
```

Revise as correções antes de concluir.

## 25.3 Tipagem

```bash
uv run pyright
```

A configuração deve tratar código de produção com nível estrito.

## 25.4 Testes

```bash
uv run pytest
```

Com cobertura:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

## 25.5 Schema PostgreSQL

```bash
docker compose up -d postgres
docker compose exec -T postgres psql -U church_manage -d church_manage_test < scripts/init-db.sql
```

O `docker-compose.yml` deve montar o SQL canônico em
`/docker-entrypoint-initdb.d/` para inicialização automática de bancos novos.

---

# 26. Docker

A aplicação deve ser executável em container OCI padrão.

O container deve:

* utilizar imagem pequena;
* não executar como root;
* possuir dependências reproduzíveis;
* receber configuração por ambiente;
* não armazenar dados persistentes localmente;
* expor health check;
* encerrar corretamente ao receber `SIGTERM`.

Exemplo de execução:

```text
uvicorn app.main:app
```

Em produção, respeite a variável:

```text
PORT
```

A aplicação deve escutar em:

```text
0.0.0.0
```

Não assumir recursos específicos de uma plataforma.

---

# 27. Integrações externas

Toda integração externa deve ficar atrás de uma porta.

Exemplos:

```python
class EmailSender(Protocol):
    async def send(self, message: EmailMessage) -> EmailDelivery:
        ...


class ObjectStorage(Protocol):
    async def upload(self, file: UploadFileCommand) -> StoredObject:
        ...


class PasswordHasher(Protocol):
    def hash(self, plain_text: str) -> PasswordHash:
        ...

    def verify(self, plain_text: str, hashed: PasswordHash) -> bool:
        ...
```

Casos de uso não devem importar diretamente SDKs de:

* AWS;
* Cloudflare;
* Google Cloud;
* Resend;
* Brevo;
* Stripe;
* provedores de WhatsApp.

---

# 28. Idempotência

Operações sujeitas a repetição devem considerar idempotência.

Exemplos:

* callbacks;
* webhooks;
* criação de pagamentos;
* envio de comunicações;
* aprovação de solicitações;
* importações;
* processamento de jobs.

Quando aplicável, utilizar:

```text
idempotency_key
unique constraint
controle de estado
registro de processamento
```

Não confiar apenas em verificações na memória.

---

# 29. Jobs e processamento assíncrono

Durante o MVP, prefira jobs persistidos no PostgreSQL.

Não introduzir RabbitMQ, Kafka ou Redis sem necessidade comprovada e ADR correspondente.

Jobs devem possuir:

```text
id
type
payload
status
attempts
scheduled_at
locked_until
last_error
created_at
updated_at
```

Handlers devem ser idempotentes.

Falhas devem possuir:

* quantidade máxima de tentativas;
* backoff;
* registro de erro;
* possibilidade de reprocessamento.

Não executar tarefas críticas apenas com `BackgroundTasks` do FastAPI, pois elas podem ser perdidas em reinícios.

---

# 30. Paginação

Listagens potencialmente grandes devem ser paginadas.

Prefira paginação por cursor para:

* membros;
* lançamentos financeiros;
* auditoria;
* eventos;
* comunicações.

O cursor deve ser:

* opaco para o cliente;
* validado;
* estável;
* baseado em ordenação determinística.

Exemplo de ordenação:

```text
created_at DESC, id DESC
```

Não utilizar apenas `created_at`, pois pode haver empate.

---

# 31. APIs

## 31.1 Convenções

Utilize recursos no plural:

```text
/members
/events
/financial-entries
/registration-requests
```

Use verbos somente quando a operação representar uma ação que não seja CRUD natural:

```text
POST /registration-requests/{id}/approval
POST /financial-entries/{id}/reversal
POST /events/{id}/publication
```

## 31.2 Versionamento

Utilize:

```text
/api/v1
```

Mudanças incompatíveis exigem nova versão ou estratégia de compatibilidade.

## 31.3 Status HTTP

Utilize semanticamente:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
```

Não retornar `200` para erros de negócio.

---

# 32. Alterações de arquitetura

O agente não deve introduzir sem autorização explícita:

* microsserviços;
* event sourcing;
* CQRS completo;
* Kafka;
* RabbitMQ;
* Kubernetes;
* Redis como dependência obrigatória;
* banco diferente de PostgreSQL;
* framework diferente de FastAPI;
* ORM diferente de SQLAlchemy;
* nova linguagem de backend;
* autenticação proprietária fortemente acoplada;
* dependência exclusiva de um provedor de cloud.

Quando uma alteração arquitetural parecer necessária:

1. explicar o problema;
2. apresentar alternativas;
3. indicar trade-offs;
4. criar ou propor um ADR;
5. aguardar decisão antes de implementar.

---

# 33. Política para dependências

Antes de adicionar uma biblioteca, verificar:

* se o problema pode ser resolvido com a biblioteca padrão;
* manutenção ativa;
* compatibilidade com Python 3.12;
* tipos disponíveis;
* licença;
* tamanho e complexidade;
* vulnerabilidades conhecidas;
* impacto de portabilidade.

Evitar dependências para funcionalidades triviais.

Não adicionar bibliotecas sobrepostas com ferramentas já adotadas.

Exemplo:

```text
Não adicionar Black se Ruff já realiza formatação.
Não adicionar Flake8 se Ruff já realiza lint.
Não adicionar outro ORM se SQLAlchemy já é o padrão.
```

---

# 34. Modificação de arquivos

O agente deve preservar:

* estilo existente;
* encoding UTF-8;
* final de linha;
* estrutura de imports;
* convenções do módulo;
* APIs públicas existentes, salvo quando a tarefa exigir mudança.

Evitar reformatar arquivos inteiros quando a alteração for localizada.

Não modificar arquivos gerados automaticamente, salvo quando esse for o fluxo esperado.

Exemplos de arquivos normalmente gerados:

```text
lockfiles
artefatos de build
clientes OpenAPI
```

---

# 35. Critérios de conclusão

Uma tarefa só deve ser considerada concluída quando:

1. o comportamento solicitado estiver implementado;
2. a arquitetura tiver sido respeitada;
3. a tipagem estiver completa, sem `Unknown`, tipos parcialmente desconhecidos, `Any` injustificado ou argumentos genéricos ausentes;
4. os testes relevantes tiverem sido adicionados ou atualizados;
5. os testes estiverem passando;
6. o lint estiver passando;
7. o formatador tiver sido executado;
8. o Pyright não apresentar erros;
9. o SQL canônico tiver sido atualizado e validado quando o schema mudar;
10. a documentação afetada tiver sido atualizada;
11. riscos e limitações remanescentes tiverem sido informados.

Comandos mínimos:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Quando houver mudança de schema:

```bash
docker compose config --quiet
docker compose up -d postgres
```

---

# 36. Formato de resposta do agente

Ao concluir uma tarefa, o agente deve informar:

```text
Resumo:
- o que foi implementado;

Arquivos alterados:
- lista dos arquivos principais;

Validações:
- testes executados;
- lint;
- type checking;
- alterações no schema SQL;

Decisões:
- decisões relevantes tomadas;

Pendências:
- limitações ou riscos ainda existentes.
```

Não afirmar que testes ou comandos foram executados quando não foram.

Caso uma validação não possa ser executada, informar explicitamente:

* qual comando não foi executado;
* por que não foi executado;
* qual risco permanece.

---

# 37. Restrições finais

O agente nunca deve:

* ignorar erros de tipagem para concluir rapidamente;
* deixar tipos `Unknown`, parcialmente desconhecidos ou genericamente incompletos no código;
* silenciar diagnósticos `reportUnknown*` ou equivalentes do Pyright;
* utilizar `Any` indiscriminadamente;
* introduzir regras de negócio em controllers;
* acoplar domínio ao ORM;
* consultar dados sem `church_id`;
* confiar em validações apenas do frontend;
* armazenar segredos no repositório;
* usar `float` para valores monetários;
* gerar timestamps sem timezone;
* criar alterações destrutivas de schema sem destacar o impacto;
* alterar decisões arquiteturais silenciosamente;
* adicionar complexidade de infraestrutura sem necessidade;
* afirmar sucesso sem realizar as validações correspondentes.

O objetivo é produzir código:

```text
fortemente tipado;
orientado ao domínio;
independente de framework no núcleo;
seguro para multi-tenancy;
testável;
portável;
simples de operar;
econômico para o MVP;
e evolutivo para o crescimento do produto.
```
