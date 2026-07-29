---
name: add-feature
description: Implementa uma nova feature de ponta a ponta utilizando Clean Architecture, Clean Code, DRY, SOLID, tipagem forte e TDD.
-------------------------------------------------------------------------------------------------------------------------------------

# Add Feature

## Objetivo

Adicionar uma nova feature ao sistema de forma incremental, testável e alinhada à arquitetura existente.

Esta skill deve ser utilizada sempre que for necessário:

* criar um novo caso de uso;
* adicionar uma nova funcionalidade de negócio;
* criar ou alterar entidades e objetos de valor;
* expor um novo endpoint;
* integrar uma nova operação ao banco de dados;
* adicionar uma regra de negócio;
* implementar uma história de usuário.

A implementação deve seguir obrigatoriamente:

* Clean Architecture;
* Clean Code;
* DRY;
* SOLID;
* TDD;
* tipagem forte em Python;
* baixo acoplamento;
* alta coesão;
* dependências apontando para dentro;
* separação entre domínio, aplicação, interfaces e infraestrutura.

---

# Princípios fundamentais

## Regra de dependência

As dependências devem sempre apontar para as camadas mais internas.

Fluxo permitido:

```text
Infrastructure → Interface Adapters → Application → Domain
```

Fluxos proibidos:

```text
Domain → Application
Domain → Infrastructure
Application → Infrastructure
Application → Framework Web
```

O domínio não deve conhecer:

* FastAPI;
* SQLAlchemy;
* Pydantic;
* PostgreSQL;
* HTTP;
* JSON;
* filas;
* serviços externos;
* detalhes de persistência.

A camada de aplicação pode depender apenas de abstrações definidas em camadas internas.

---

# Estrutura arquitetural esperada

Utilize como referência:

```text
src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── enums/
│   ├── exceptions/
│   ├── services/
│   └── repositories/
│
├── application/
│   ├── use_cases/
│   ├── commands/
│   ├── queries/
│   ├── dto/
│   ├── ports/
│   └── exceptions/
│
├── adapters/
│   ├── inbound/
│   │   └── http/
│   │       ├── controllers/
│   │       ├── requests/
│   │       ├── responses/
│   │       └── presenters/
│   │
│   └── outbound/
│       ├── persistence/
│       ├── messaging/
│       └── external_services/
│
└── infrastructure/
    ├── database/
    ├── web/
    ├── configuration/
    └── dependency_injection/

scripts/
└── init-db.sql

tests/
├── unit/
│   ├── domain/
│   └── application/
├── integration/
│   ├── persistence/
│   └── http/
└── acceptance/
```

Adapte a localização dos arquivos à estrutura real do projeto. Não crie uma estrutura paralela caso o projeto já possua uma convenção equivalente.

---

# Fluxo obrigatório de implementação

A implementação deve seguir estas etapas, na ordem apresentada.

## 1. Compreender a feature

Antes de escrever código, identifique:

* objetivo de negócio;
* ator responsável;
* pré-condições;
* entradas;
* regras de negócio;
* permissões;
* resultados esperados;
* efeitos colaterais;
* erros esperados;
* critérios de aceitação;
* entidades envolvidas;
* agregados envolvidos;
* invariantes que precisam ser protegidas.

Não inicie pelo controller, endpoint ou banco de dados.

Comece pelo comportamento de negócio.

Caso alguma informação não esteja especificada, faça a suposição mais conservadora possível e registre-a claramente na implementação ou na descrição da mudança.

---

## 2. Inspecionar o código existente

Antes de criar novos componentes:

1. procure entidades relacionadas;
2. procure casos de uso semelhantes;
3. procure abstrações de repositório existentes;
4. procure objetos de valor reutilizáveis;
5. procure convenções de nomenclatura;
6. procure fábricas e fixtures de teste;
7. procure padrões de tratamento de erros;
8. procure o mecanismo de injeção de dependências;
9. procure os padrões de persistência;
10. procure endpoints equivalentes.

Não duplique uma abstração existente.

Não reutilize código apenas porque ele possui estrutura parecida. Reutilize somente quando houver o mesmo significado de negócio.

DRY significa evitar repetição de conhecimento, e não apenas eliminar linhas visualmente semelhantes.

---

## 3. Definir o comportamento por testes

Utilize o ciclo TDD:

```text
Red → Green → Refactor
```

### Red

Escreva primeiro um teste que represente um comportamento esperado e que falhe pelo motivo correto.

### Green

Implemente apenas o mínimo necessário para fazer o teste passar.

### Refactor

Melhore a estrutura do código mantendo todos os testes passando.

Não implemente vários comportamentos antes de executar o ciclo.

Execute o ciclo individualmente para cada regra relevante.

---

# Estratégia de testes

## Pirâmide de testes

Priorize:

1. testes unitários de domínio;
2. testes unitários de casos de uso;
3. testes de integração dos adapters;
4. poucos testes de aceitação ou ponta a ponta.

Regras de negócio não devem depender de testes HTTP para serem validadas.

---

## Testes de domínio

Os testes de domínio devem validar:

* criação válida de entidades;
* rejeição de estados inválidos;
* invariantes;
* transições de estado;
* comportamento dos objetos de valor;
* eventos de domínio, quando aplicável;
* regras que independem de infraestrutura.

Exemplos de comportamentos:

```text
Dado um membro pendente
Quando sua inscrição for aprovada
Então seu status deve passar para ativo
```

```text
Dado um membro já aprovado
Quando uma nova aprovação for solicitada
Então a operação deve ser rejeitada
```

Evite testar detalhes internos, atributos privados ou sequência de chamadas internas.

Teste comportamento observável.

---

## Testes de casos de uso

Os testes da camada de aplicação devem validar:

* orquestração correta;
* chamadas às dependências;
* persistência;
* autorização;
* ausência de efeitos colaterais em falhas;
* conversão entre entradas e saídas;
* propagação ou tradução de erros;
* idempotência, quando necessária.

Use doubles somente nas fronteiras da aplicação:

* fake;
* stub;
* spy;
* mock.

Prefira fakes simples para repositórios quando eles deixarem o teste mais legível.

Evite mocks excessivamente acoplados à implementação.

---

## Testes de integração

Os testes de integração devem validar contratos reais, como:

* implementação do repositório;
* mapeamento ORM;
* constraints do banco;
* serialização e desserialização;
* transações;
* endpoint HTTP;
* autenticação;
* injeção de dependências.

Não repita toda a lógica dos testes unitários nos testes de integração.

---

## Estrutura dos testes

Utilize o padrão:

```text
Arrange
Act
Assert
```

ou:

```text
Given
When
Then
```

Os nomes devem descrever o comportamento:

```python
def test_should_approve_pending_member() -> None:
    ...
```

```python
def test_should_reject_approval_when_member_is_already_active() -> None:
    ...
```

Evite nomes genéricos:

```python
def test_member() -> None:
    ...
```

---

# Implementação por camada

## 1. Camada de domínio

Implemente primeiro os conceitos de negócio necessários.

A camada de domínio pode conter:

* entidades;
* agregados;
* objetos de valor;
* enums de negócio;
* exceções de domínio;
* serviços de domínio;
* eventos de domínio;
* interfaces de repositório, conforme a convenção do projeto.

### Entidades

Uma entidade deve:

* possuir identidade;
* proteger suas invariantes;
* expor comportamentos de negócio;
* evitar setters genéricos;
* impedir estados inválidos;
* manter sua consistência internamente.

Prefira:

```python
member.approve(approved_by=approver_id)
```

Evite:

```python
member.status = MemberStatus.ACTIVE
member.approved_by = approver_id
member.approved_at = now
```

As alterações de estado devem acontecer por métodos que expressem intenção de negócio.

---

## Objetos de valor

Crie um objeto de valor quando um conceito:

* possuir regras próprias de validação;
* for identificado pelos seus valores;
* for imutável;
* aparecer repetidamente no domínio;
* reduzir o uso de tipos primitivos ambíguos.

Exemplos:

* `Email`;
* `DocumentNumber`;
* `PhoneNumber`;
* `Money`;
* `ChurchId`;
* `MemberId`;
* `CongregationId`.

Prefira:

```python
@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()

        if not normalized:
            raise InvalidEmailError("Email não pode ser vazio.")

        object.__setattr__(self, "value", normalized)
```

Evite espalhar validações de e-mail por controllers, DTOs, casos de uso e repositórios.

---

## Exceções de domínio

Exceções devem representar violações de regras de negócio.

Exemplos:

```python
class MemberAlreadyApprovedError(DomainError):
    pass
```

```python
class ChurchMemberLimitExceededError(DomainError):
    pass
```

Evite exceções genéricas para situações de negócio:

```python
raise Exception("Erro")
```

A exceção deve revelar o motivo da falha.

---

## Serviços de domínio

Crie um serviço de domínio somente quando uma regra:

* pertence ao domínio;
* envolve múltiplas entidades ou agregados;
* não pertence naturalmente a uma única entidade;
* não depende de infraestrutura.

Não use serviços de domínio como depósito genérico de lógica.

---

## 2. Camada de aplicação

A camada de aplicação deve implementar os casos de uso do sistema.

Ela é responsável por:

* coordenar o fluxo;
* carregar agregados;
* verificar permissões;
* chamar comportamentos de domínio;
* persistir mudanças;
* controlar transações por abstração;
* publicar eventos por abstração;
* produzir uma saída estruturada.

Ela não deve conter detalhes de:

* HTTP;
* ORM;
* banco de dados;
* framework web;
* formato JSON;
* códigos de status HTTP.

---

## Casos de uso

Cada caso de uso deve representar uma intenção clara.

Exemplos:

```text
RegisterChurch
ApproveMemberRegistration
CreateCell
AssignMemberToMinistry
RecordContribution
ScheduleChurchEvent
```

Evite serviços genéricos como:

```text
MemberService
ChurchService
FinanceService
```

Um caso de uso deve ter uma responsabilidade principal.

Exemplo:

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ApproveMemberInput:
    church_id: ChurchId
    member_id: MemberId
    approver_id: UserId


@dataclass(frozen=True, slots=True)
class ApproveMemberOutput:
    member_id: MemberId
    status: MemberStatus


class ApproveMember:
    def __init__(
        self,
        member_repository: MemberRepository,
        authorization_service: AuthorizationService,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._member_repository = member_repository
        self._authorization_service = authorization_service
        self._unit_of_work = unit_of_work

    def execute(self, data: ApproveMemberInput) -> ApproveMemberOutput:
        self._authorization_service.ensure_can_approve_member(
            church_id=data.church_id,
            user_id=data.approver_id,
        )

        member = self._member_repository.get_by_id(
            church_id=data.church_id,
            member_id=data.member_id,
        )

        if member is None:
            raise MemberNotFoundError(data.member_id)

        member.approve(approved_by=data.approver_id)

        self._member_repository.save(member)
        self._unit_of_work.commit()

        return ApproveMemberOutput(
            member_id=member.id,
            status=member.status,
        )
```

Adapte chamadas síncronas ou assíncronas ao padrão existente no projeto.

---

## DTOs de aplicação

DTOs devem:

* possuir tipagem explícita;
* ser imutáveis quando possível;
* representar entrada ou saída de um caso de uso;
* não depender de classes HTTP;
* evitar dicionários sem contrato.

Prefira:

```python
@dataclass(frozen=True, slots=True)
class CreateChurchInput:
    name: str
    document_number: str | None
    owner_user_id: UserId
```

Evite:

```python
def execute(self, data: dict) -> dict:
    ...
```

Não use `Any` sem necessidade técnica justificada.

---

## Ports

Dependências externas devem ser representadas por interfaces ou protocolos.

Exemplo:

```python
from typing import Protocol


class MemberRepository(Protocol):
    def get_by_id(
        self,
        church_id: ChurchId,
        member_id: MemberId,
    ) -> Member | None:
        ...

    def save(self, member: Member) -> None:
        ...
```

A aplicação depende da abstração.

A infraestrutura implementa a abstração explicitamente por herança. Não dependa
somente da conformidade estrutural implícita de `Protocol`:

```python
class SqlAlchemyMemberRepository(IMemberRepository):
    ...
```

Essa regra se aplica a toda porta e adapter, incluindo repositories, Unit of
Work, gateways, publishers, rate limiters, clientes externos, hashing, relógio,
storage e e-mail. Implementações concretas devem aparecer somente na
infraestrutura, no Composition Root e em testes diretos do adapter.

---

## 3. Adapters de entrada

Controllers devem ser finos.

Responsabilidades permitidas:

* receber a requisição;
* validar formato básico;
* converter request em input do caso de uso;
* executar o caso de uso;
* converter a saída em response;
* traduzir erros conhecidos para o protocolo de entrada.

Responsabilidades proibidas:

* implementar regra de negócio;
* acessar ORM diretamente;
* executar queries diretamente;
* decidir invariantes;
* alterar entidades sem passar pelo caso de uso.

Exemplo conceitual:

```python
@router.post(
    "/churches/{church_id}/members/{member_id}/approval",
    response_model=ApproveMemberResponse,
)
def approve_member(
    church_id: UUID,
    member_id: UUID,
    current_user: CurrentUser,
    use_case: ApproveMemberDependency,
) -> ApproveMemberResponse:
    output = use_case.execute(
        ApproveMemberInput(
            church_id=ChurchId(church_id),
            member_id=MemberId(member_id),
            approver_id=UserId(current_user.id),
        )
    )

    return ApproveMemberResponse.from_output(output)
```

---

## Requests e responses

Os schemas HTTP devem ficar na borda da aplicação.

Eles podem utilizar Pydantic ou outra biblioteca do framework, mas não devem ser reutilizados como entidades ou DTOs de domínio.

Fluxo esperado:

```text
HTTP Request
    ↓
Request Schema
    ↓
Application Input
    ↓
Use Case
    ↓
Application Output
    ↓
Response Schema
    ↓
HTTP Response
```

---

## 4. Adapters de saída

Adapters de saída implementam as abstrações esperadas pelas camadas internas.

Exemplos:

* repositório SQLAlchemy;
* publicador de eventos;
* cliente de e-mail;
* armazenamento de arquivos;
* gateway de pagamento;
* serviço de notificações.

Eles devem converter modelos de infraestrutura para modelos de domínio e vice-versa.

Não exponha modelos ORM para o domínio ou para os casos de uso.

---

## Repositórios

O repositório deve trabalhar com entidades ou agregados de domínio.

Prefira:

```python
class SqlAlchemyMemberRepository(MemberRepository):
    def get_by_id(
        self,
        church_id: ChurchId,
        member_id: MemberId,
    ) -> Member | None:
        model = (
            self._session.query(MemberModel)
            .filter(
                MemberModel.id == member_id.value,
                MemberModel.church_id == church_id.value,
            )
            .one_or_none()
        )

        if model is None:
            return None

        return self._mapper.to_domain(model)
```

Evite retornar diretamente:

```python
MemberModel
```

Não implemente regras de negócio dentro do repositório.

---

## Mappers

Use mappers explícitos quando houver separação entre:

* entidade de domínio;
* modelo ORM;
* request;
* response;
* evento externo.

Evite mapeamentos implícitos ou espalhados por vários arquivos.

Um mapper deve apenas converter representações. Ele não deve implementar regra de negócio.

---

## 5. Infraestrutura

A infraestrutura deve conectar os adapters aos frameworks e recursos externos.

Implemente, quando necessário:

* modelo ORM;
* atualização de `scripts/init-db.sql`;
* configuração;
* container de dependências;
* transação;
* rota;
* observabilidade;
* implementação de gateways.

Não deixe o framework controlar a arquitetura.

O framework deve ser um detalhe externo.

---

# TDD detalhado

Para cada comportamento, execute o seguinte processo.

## Etapa 1 — Escrever o cenário

Exemplo:

```text
Cenário: aprovar um membro pendente

Dado que existe um membro pendente
E o usuário possui permissão para aprovar membros
Quando o caso de uso de aprovação for executado
Então o membro deve ficar ativo
E o responsável pela aprovação deve ser registrado
E a alteração deve ser persistida
```

---

## Etapa 2 — Criar o teste que falha

Exemplo:

```python
def test_should_approve_pending_member() -> None:
    member = MemberFactory.pending()
    repository = InMemoryMemberRepository([member])
    authorization = AllowAllAuthorizationService()
    unit_of_work = SpyUnitOfWork()

    use_case = ApproveMember(
        member_repository=repository,
        authorization_service=authorization,
        unit_of_work=unit_of_work,
    )

    output = use_case.execute(
        ApproveMemberInput(
            church_id=member.church_id,
            member_id=member.id,
            approver_id=UserId.generate(),
        )
    )

    saved_member = repository.get_by_id(
        church_id=member.church_id,
        member_id=member.id,
    )

    assert output.status is MemberStatus.ACTIVE
    assert saved_member is not None
    assert saved_member.status is MemberStatus.ACTIVE
    assert unit_of_work.committed is True
```

O teste deve falhar inicialmente pela ausência do comportamento esperado.

---

## Etapa 3 — Implementar o mínimo

Implemente somente o código necessário para passar o teste atual.

Não antecipe:

* abstrações sem uso;
* cenários hipotéticos;
* configurações futuras;
* padrões ainda não necessários;
* otimizações prematuras.

---

## Etapa 4 — Adicionar cenários negativos

Exemplos:

* entidade não encontrada;
* usuário sem permissão;
* estado atual incompatível;
* dados inválidos;
* operação duplicada;
* conflito de unicidade;
* falha de infraestrutura;
* violação de isolamento entre igrejas.

No contexto multi-tenant, sempre teste que uma igreja não consegue acessar ou alterar recursos de outra igreja.

Exemplo:

```python
def test_should_not_approve_member_from_another_church() -> None:
    ...
```

---

## Etapa 5 — Refatorar

Após os testes passarem:

* remova duplicações reais;
* melhore nomes;
* reduza responsabilidades;
* extraia objetos de valor;
* simplifique condicionais;
* elimine acoplamento desnecessário;
* verifique a direção das dependências;
* mantenha os testes passando.

Não refatore código não relacionado à feature sem justificativa.

---

# Aplicação dos princípios SOLID

## Single Responsibility Principle

Cada classe ou módulo deve possuir uma razão principal para mudar.

Exemplos:

* entidade protege regras de negócio;
* caso de uso coordena uma ação;
* repositório persiste agregados;
* controller adapta HTTP;
* mapper converte representações.

Não concentre todas essas responsabilidades em um único serviço.

---

## Open/Closed Principle

Prefira extensão por novas implementações de ports em vez de condicionais acopladas a provedores.

Prefira:

```python
class NotificationGateway(Protocol):
    def send(self, notification: Notification) -> None:
        ...
```

Com implementações como:

```text
EmailNotificationGateway
WhatsAppNotificationGateway
InMemoryNotificationGateway
```

Evite:

```python
if provider == "email":
    ...
elif provider == "whatsapp":
    ...
```

Não aplique abstrações prematuramente quando há apenas um comportamento estável e sem variação prevista.

---

## Liskov Substitution Principle

Toda implementação de uma abstração deve respeitar o mesmo contrato.

Uma implementação de repositório não deve:

* alterar semanticamente os resultados;
* lançar erros incompatíveis sem documentação;
* ignorar o tenant;
* retornar entidades parcialmente inválidas;
* realizar commits escondidos quando o contrato não prevê isso.

---

## Interface Segregation Principle

Crie interfaces pequenas e orientadas às necessidades dos consumidores.

Evite:

```python
class Repository(Protocol):
    def save(self, entity: object) -> None: ...
    def delete(self, entity: object) -> None: ...
    def search(self, query: str) -> list[object]: ...
    def export(self) -> bytes: ...
    def import_data(self, data: bytes) -> None: ...
```

Prefira contratos específicos por agregado ou capacidade.

---

## Dependency Inversion Principle

Casos de uso devem depender de abstrações.

Prefira:

```python
class RegisterMember:
    def __init__(self, repository: MemberRepository) -> None:
        self._repository = repository
```

Evite:

```python
class RegisterMember:
    def __init__(self) -> None:
        self._repository = SqlAlchemyMemberRepository(...)
```

A composição das implementações deve ocorrer na infraestrutura.

---

# Aplicação de Clean Code

## Nomes

Use nomes que expressem intenção.

Prefira:

```python
pending_member
approval_requested_at
ensure_member_can_be_approved()
```

Evite:

```python
obj
data2
process()
handle()
do_work()
```

Termos genéricos como `manager`, `helper`, `utils`, `processor` e `service` devem ser evitados quando não descrevem claramente a responsabilidade.

---

## Funções

Funções devem:

* executar uma tarefa conceitual;
* ser pequenas o suficiente para serem compreendidas;
* possuir parâmetros explícitos;
* evitar flags booleanas que alterem completamente o comportamento;
* evitar efeitos colaterais escondidos;
* operar em um único nível de abstração.

Evite:

```python
def register_member(data: dict, send_email: bool, approve: bool) -> dict:
    ...
```

Prefira casos de uso separados ou dependências explícitas.

---

## Comentários

Comentários devem explicar decisões, restrições ou motivos não evidentes.

Não use comentários para repetir o código.

Evite:

```python
# Verifica se o membro está ativo
if member.is_active:
    ...
```

Use docstrings apenas quando adicionarem informação útil ao contrato.

---

## Tratamento de erros

* não capture exceções genericamente sem tratamento;
* não silencie erros;
* não use exceções para fluxo normal;
* traduza erros somente nas fronteiras apropriadas;
* preserve a causa original quando encapsular uma exceção técnica;
* não exponha detalhes internos em respostas HTTP.

Evite:

```python
try:
    ...
except Exception:
    return None
```

---

# Aplicação de DRY

Antes de extrair uma abstração, confirme que existe repetição de conhecimento.

Não extraia funções apenas porque dois blocos possuem linhas parecidas.

Considere:

* mesmo significado de negócio;
* mesma razão para mudar;
* mesmo conjunto de invariantes;
* mesmo ciclo de vida;
* mesma linguagem do domínio.

Repetições aceitáveis podem ser preferíveis a uma abstração incorreta.

Regra prática:

```text
Duplication is cheaper than the wrong abstraction.
```

Ao identificar duplicação:

1. confirme que o conceito é realmente o mesmo;
2. identifique o melhor proprietário da regra;
3. mova a regra para esse proprietário;
4. atualize os consumidores;
5. mantenha os testes passando.

---

# Tipagem forte em Python

Utilize tipagem explícita em:

* parâmetros;
* retornos;
* atributos;
* protocolos;
* coleções;
* DTOs;
* funções assíncronas;
* callbacks.

Prefira:

```python
def find_members(
    church_id: ChurchId,
    status: MemberStatus | None,
) -> Sequence[Member]:
    ...
```

Evite:

```python
def find_members(church_id, status=None):
    ...
```

Evite `Any`. Quando inevitável, documente o motivo.

Utilize, quando apropriado:

* `Protocol`;
* `TypeAlias`;
* `NewType`;
* generics;
* `Literal`;
* `TypedDict` apenas nas bordas;
* dataclasses;
* enums;
* tipos de identificador específicos.

Prefira identificadores semanticamente distintos:

```python
@dataclass(frozen=True, slots=True)
class ChurchId:
    value: UUID


@dataclass(frozen=True, slots=True)
class MemberId:
    value: UUID
```

Isso reduz o risco de trocar acidentalmente identificadores do mesmo tipo primitivo.

---

# Segurança multi-tenant

Toda feature que manipula dados de uma igreja deve considerar isolamento por tenant.

Nunca busque ou altere um recurso apenas pelo identificador global quando ele pertencer a uma igreja.

Prefira:

```python
repository.get_by_id(
    church_id=church_id,
    member_id=member_id,
)
```

Evite:

```python
repository.get_by_id(member_id)
```

Verifique:

* isolamento entre igrejas;
* permissões por igreja;
* vínculos do usuário;
* escopo de congregação, quando aplicável;
* queries filtradas pelo tenant;
* constraints de unicidade por tenant;
* logs sem vazamento de dados;
* eventos com identificação correta da igreja.

Inclua testes específicos para acesso cruzado entre tenants.

---

# Transações

Quando uma feature altera múltiplos dados que precisam permanecer consistentes, utilize uma abstração de unidade de trabalho.

Exemplo:

```python
class UnitOfWork(Protocol):
    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

O caso de uso define o limite transacional.

O repositório não deve realizar commits escondidos, salvo se essa for uma convenção arquitetural explicitamente estabelecida no projeto.

Em caso de erro:

* nenhuma alteração parcial deve permanecer;
* eventos externos não devem ser publicados antes da confirmação necessária;
* utilize outbox quando consistência entre banco e mensageria for necessária.

---

# Idempotência

Considere idempotência quando a operação:

* puder ser reenviada;
* receber callbacks;
* processar mensagens;
* registrar pagamentos;
* registrar contribuições;
* criar recursos a partir de solicitações externas;
* puder sofrer retry automático.

A estratégia pode utilizar:

* chave de idempotência;
* constraint única;
* registro de operação processada;
* estado da entidade;
* deduplicação de mensagem.

A idempotência deve ser testada.

Exemplo:

```text
Quando a mesma contribuição for registrada duas vezes com a mesma chave
Então apenas um lançamento financeiro deve existir
```

---

# Observabilidade

Ao implementar uma nova feature, considere:

* logs estruturados;
* correlation ID;
* tenant ID;
* actor ID;
* nome do caso de uso;
* resultado da operação;
* duração;
* métricas relevantes;
* rastreamento de falhas.

Não registre:

* senhas;
* tokens;
* documentos completos;
* dados financeiros sensíveis;
* informações pessoais desnecessárias.

Logs não devem substituir regras ou auditoria de domínio.

Quando a operação exigir histórico formal, implemente um registro de auditoria explícito.

---

# Banco de dados e schema SQL

Quando a feature exigir alteração de banco:

1. atualize o schema canônico em `scripts/init-db.sql`;
2. mantenha compatibilidade com o estado esperado do banco;
3. defina nulabilidade conscientemente;
4. defina índices com base nos acessos reais;
5. defina constraints que reforcem invariantes possíveis;
6. considere escopo multi-tenant;
7. evite alteração destrutiva sem estratégia explícita;
8. teste a criação em PostgreSQL real pelo Docker Compose;
9. teste a reexecução do script quando ele for declarado idempotente;
10. não dependa apenas da validação da aplicação.

Para mudanças incompatíveis, prefira expandir e contrair:

```text
Expand → Migrate → Switch → Contract
```

---

# Compatibilidade e evolução

Evite quebrar contratos existentes sem necessidade.

Ao alterar APIs:

* preserve campos existentes quando possível;
* adicione novos campos de forma compatível;
* não mude significado silenciosamente;
* trate versionamento quando necessário;
* atualize documentação;
* atualize consumidores conhecidos;
* adicione testes de regressão.

---

# Ordem recomendada dos arquivos

Para uma nova feature, implemente aproximadamente nesta ordem:

```text
1. Teste do comportamento de domínio
2. Entidade, value object ou regra de domínio
3. Teste do caso de uso
4. Input e output do caso de uso
5. Port necessário
6. Caso de uso
7. Fake de teste
8. Teste de integração do repositório
9. Modelo ORM e mapper
10. Implementação do repositório
11. Atualização de `scripts/init-db.sql`
12. Teste HTTP
13. Request e response
14. Controller ou rota
15. Injeção de dependências
16. Documentação
```

A ordem pode variar quando não houver alteração em alguma camada.

---

# Checklist de implementação

## Domínio

* [ ] A regra está no domínio correto.
* [ ] As invariantes estão protegidas.
* [ ] Não existem dependências de framework.
* [ ] Os métodos expressam intenção de negócio.
* [ ] Objetos de valor foram considerados.
* [ ] Estados inválidos são impossíveis ou rejeitados.
* [ ] As exceções possuem significado de negócio.
* [ ] Os testes unitários cobrem os comportamentos.

## Aplicação

* [ ] Existe um caso de uso com responsabilidade clara.
* [ ] Entradas e saídas possuem tipos explícitos.
* [ ] Dependências externas são abstraídas.
* [ ] O caso de uso não conhece HTTP ou ORM.
* [ ] Autorização foi considerada.
* [ ] Isolamento multi-tenant foi considerado.
* [ ] Transação foi considerada.
* [ ] Idempotência foi considerada.
* [ ] Casos de erro estão testados.

## Adapters

* [ ] O controller é fino.
* [ ] Requests não são usados como entidades.
* [ ] Responses não expõem modelos ORM.
* [ ] Repositórios convertem entre domínio e persistência.
* [ ] Erros são traduzidos na fronteira correta.
* [ ] Os adapters respeitam os ports internos.
* [ ] Cada adapter implementa explicitamente seu port por herança.

## Infraestrutura

* [ ] Dependências estão configuradas no composition root.
* [ ] O schema canônico em `scripts/init-db.sql` foi atualizado.
* [ ] Índices e constraints foram considerados.
* [ ] Logs não expõem informações sensíveis.
* [ ] Configurações não estão hardcoded.
* [ ] Integrações possuem timeout quando aplicável.
* [ ] Retries são seguros e limitados.

## Qualidade

* [ ] O ciclo Red-Green-Refactor foi seguido.
* [ ] Todos os testes passam.
* [ ] O type checker passa.
* [ ] O linter passa.
* [ ] O formatter passa.
* [ ] Não há imports circulares.
* [ ] Não há código morto.
* [ ] Não há abstrações prematuras.
* [ ] Não há duplicação de conhecimento.
* [ ] Nomes representam o domínio.
* [ ] A documentação foi atualizada.

---

# Comandos de validação

Utilize os comandos definidos pelo projeto.

Quando não houver uma convenção estabelecida, considere:

```bash
pytest
```

```bash
pytest tests/unit
```

```bash
pytest tests/integration
```

```bash
mypy src tests
```

```bash
ruff check src tests
```

```bash
ruff format --check src tests
```

Quando houver configuração no `pyproject.toml`, utilize-a como fonte de verdade.

Não altere configurações de qualidade apenas para fazer código inválido passar.

---

# Restrições

Não faça:

* regras de negócio em controllers;
* acesso direto ao banco em casos de uso;
* modelos ORM como entidades de domínio;
* dependência do domínio em frameworks;
* classes genéricas com muitas responsabilidades;
* repositories genéricos sem semântica;
* captura indiscriminada de `Exception`;
* uso desnecessário de `Any`;
* funções com argumentos booleanos que mudam sua natureza;
* commits escondidos em componentes inesperados;
* duplicação de validações;
* criação de abstrações sem necessidade atual;
* refatorações amplas não relacionadas;
* mocks de detalhes internos;
* testes dependentes da ordem de execução;
* testes que acessam serviços externos reais;
* alteração de contratos sem testes de regressão;
* consulta de recurso multi-tenant sem escopo da igreja;
* bypass de permissões por confiar apenas na interface;
* implementação sem testes automatizados.

---

# Critérios para considerar a feature concluída

Uma feature somente pode ser considerada concluída quando:

1. os critérios de aceitação foram implementados;
2. os testes de domínio estão passando;
3. os testes do caso de uso estão passando;
4. os testes de integração necessários estão passando;
5. os cenários de erro foram cobertos;
6. o isolamento multi-tenant foi validado;
7. a tipagem está correta;
8. o linter está passando;
9. o formatter está passando;
10. o SQL canônico está atualizado e validado, quando necessário;
11. a composição de dependências foi atualizada;
12. a documentação relevante foi atualizada;
13. não existem violações conhecidas da arquitetura;
14. não existem TODOs essenciais para o funcionamento;
15. o comportamento pode ser explicado em termos de negócio.

---

# Formato da resposta do agente

Ao finalizar a implementação, apresente:

## Resumo

Descreva objetivamente o comportamento adicionado.

## Decisões de domínio

Liste:

* entidades alteradas;
* objetos de valor criados;
* invariantes adicionadas;
* decisões relevantes.

## Arquitetura

Liste os componentes criados ou modificados por camada:

```text
Domain
Application
Adapters
Infrastructure
```

## Testes

Informe:

* testes adicionados;
* cenários positivos;
* cenários negativos;
* testes de isolamento multi-tenant;
* testes de integração;
* resultado da execução.

## Banco de dados

Informe:

* alterações em `scripts/init-db.sql`;
* tabelas ou colunas alteradas;
* índices;
* constraints.

## Validações executadas

Informe os comandos executados e seus resultados:

```text
pytest: aprovado
mypy: aprovado
ruff check: aprovado
ruff format --check: aprovado
```

Não afirme que um comando foi executado quando ele não tiver sido realmente executado.

## Pendências e riscos

Informe somente riscos reais, limitações ou decisões que exijam acompanhamento.

Não invente pendências genéricas.

---

# Regra final

Implemente a menor solução completa que satisfaça os requisitos atuais, preserve as invariantes do domínio e mantenha a arquitetura evolutiva.

A prioridade é:

```text
Corretude de negócio
→ Testabilidade
→ Clareza
→ Isolamento arquitetural
→ Simplicidade
→ Performance
```

Não sacrifique corretude e clareza por abstrações sofisticadas ou otimizações prematuras.
