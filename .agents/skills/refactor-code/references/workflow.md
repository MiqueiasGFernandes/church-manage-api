# Skill: Refatoração Arquitetural e Padronização de Código

## Objetivo

Refatorar código existente para adequá-lo aos padrões arquiteturais, de qualidade e de estilo definidos no arquivo `AGENTS.md` do projeto.

A refatoração deve preservar o comportamento funcional existente, corrigindo desvios relacionados a:

* Clean Architecture;
* separação de responsabilidades;
* inversão e injeção de dependências;
* tipagem forte em Python;
* princípios SOLID;
* Clean Code;
* DRY;
* testabilidade;
* TDD;
* organização de módulos;
* convenções de código definidas no projeto.

Esta skill deve ser utilizada quando o código já existe, mas não está completamente alinhado às regras atuais do projeto.

---

## Fonte de verdade

Antes de iniciar qualquer alteração, leia integralmente o arquivo:

```text
AGENTS.md
```

O `AGENTS.md` é a fonte de verdade para:

* arquitetura;
* estrutura de diretórios;
* dependências permitidas;
* padrões de nomenclatura;
* regras de tipagem;
* framework de injeção de dependências;
* estratégia de testes;
* convenções de código;
* ferramentas de lint e formatação;
* práticas obrigatórias e proibidas.

Quando existir divergência entre esta skill e o `AGENTS.md`, prevalece o `AGENTS.md`.

Não presuma que as regras conhecidas anteriormente continuam válidas. Sempre releia a versão atual do arquivo antes de refatorar.

### Persistência de novas preferências

Quando o usuário estabelecer uma nova preferência de arquitetura, organização,
qualidade ou fluxo de trabalho durante uma refatoração, registre-a no contexto
persistente de `.agents` antes de concluir a tarefa.

Utilize preferencialmente `.agents/AGENTS.md` para regras gerais do repositório.
Quando a preferência pertencer a um contexto mais específico, registre-a no
arquivo correspondente dentro de `.agents` e adicione uma referência no
`.agents/AGENTS.md` quando necessário para que ela seja descoberta em tarefas
futuras.

Não deixe uma nova preferência apenas na conversa ou apenas na implementação.
Antes de persistir, confirme que ela não contradiz requisitos funcionais, ADRs ou
outras regras de maior prioridade. Se houver contradição, reporte-a em vez de
alterar silenciosamente a fonte de verdade.

---

## Quando utilizar esta skill

Utilize esta skill quando houver solicitações como:

* refatorar uma feature existente;
* adaptar código legado à arquitetura atual;
* corrigir violações de Clean Architecture;
* remover dependências diretas entre camadas;
* adicionar tipagem forte;
* migrar construção manual de dependências para o container de injeção;
* separar responsabilidades de controllers, use cases e repositories;
* tornar código testável;
* eliminar duplicações;
* reorganizar módulos;
* adequar testes aos padrões atuais;
* alinhar código existente ao `AGENTS.md`;
* reduzir acoplamento;
* corrigir responsabilidades indevidas em entidades ou casos de uso.

---

## Princípios obrigatórios

### 1. Preservação de comportamento

A refatoração não deve alterar intencionalmente:

* regras de negócio;
* contratos públicos;
* respostas de API;
* códigos HTTP;
* eventos publicados;
* efeitos colaterais esperados;
* formatos persistidos;
* comportamento observado pelos consumidores.

Mudanças funcionais devem ser tratadas como uma feature ou correção separada.

Caso seja impossível adequar a arquitetura sem alterar um contrato público, documente explicitamente:

* o contrato afetado;
* o motivo da alteração;
* os consumidores impactados;
* a estratégia de compatibilidade ou migração.

---

### 2. Refatoração guiada por testes

Antes de alterar o código:

1. identifique os comportamentos atuais;
2. localize os testes existentes;
3. execute os testes relevantes;
4. crie testes de caracterização quando o comportamento não estiver protegido;
5. somente depois altere a implementação.

A sequência preferencial é:

```text
Caracterizar → Refatorar → Validar → Simplificar
```

Não reescreva um componente sem antes possuir proteção mínima contra regressões.

---

### 3. Alterações incrementais

Evite refatorações extensas e simultâneas sem validação intermediária.

Prefira ciclos pequenos:

1. identificar uma violação;
2. criar ou ajustar testes;
3. aplicar uma alteração;
4. executar testes;
5. executar análise estática;
6. revisar o diff;
7. avançar para a próxima alteração.

Cada etapa deve manter o projeto em estado executável.

---

## Processo obrigatório

## Etapa 1 — Ler o contexto do projeto

Antes de modificar qualquer arquivo:

1. leia o `AGENTS.md`;
2. identifique o módulo ou bounded context afetado;
3. analise a estrutura de diretórios existente;
4. identifique os pontos de entrada da funcionalidade;
5. identifique interfaces, implementações e dependências;
6. localize os testes existentes;
7. identifique o container de injeção de dependências;
8. localize configurações de lint, type checking e testes.

Verifique, quando existirem:

```text
pyproject.toml
pytest.ini
mypy.ini
ruff.toml
.coveragerc
docker-compose.yml
alembic.ini
```

Não introduza uma nova ferramenta quando o projeto já possuir uma ferramenta equivalente definida.

---

## Etapa 2 — Mapear o fluxo atual

Antes da refatoração, descreva internamente o fluxo atual:

```text
Entrada
  ↓
Controller / Handler
  ↓
Caso de uso
  ↓
Porta / Interface
  ↓
Adapter / Repository / Gateway
  ↓
Infraestrutura externa
```

Identifique:

* onde a requisição entra;
* onde ocorre validação de entrada;
* onde está a regra de negócio;
* onde ocorre persistência;
* onde serviços externos são chamados;
* onde transações são controladas;
* onde objetos de domínio são criados;
* onde DTOs são convertidos;
* onde exceções são traduzidas;
* como as dependências são construídas.

O mapeamento deve diferenciar comportamento essencial de detalhes acidentais da implementação atual.

---

## Etapa 3 — Identificar violações

Classifique cada problema encontrado em uma das categorias abaixo.

### Arquitetura

* domínio dependendo de framework;
* aplicação dependendo de infraestrutura;
* controller acessando repository diretamente;
* caso de uso importando implementação concreta;
* adapter contendo regra de negócio;
* entidade conhecendo banco de dados;
* DTO sendo usado como entidade;
* container de DI importado dentro da camada de domínio;
* dependência apontando da camada interna para a camada externa.

### Responsabilidade

* controller executando regra de negócio;
* use case realizando serialização HTTP;
* repository decidindo regra de negócio;
* entidade realizando acesso externo;
* classe com múltiplos motivos para mudar;
* função coordenando responsabilidades não relacionadas.

### Dependências

* instanciação direta de implementações concretas;
* uso de singleton global;
* service locator;
* imports circulares;
* dependências opcionais sem contrato claro;
* dependências ocultas em variáveis globais;
* uso incorreto do framework `dependency_injector`.

### Tipagem

* uso desnecessário de `Any`;
* ausência de tipos em APIs públicas;
* retorno implícito;
* dicionários sem estrutura conhecida;
* uso de `dict[str, object]` onde deveria existir DTO;
* casts usados para esconder erros arquiteturais;
* `# type: ignore` sem justificativa;
* tipos opcionais tratados sem validação;
* entidades com estado inválido representável.

### Qualidade de código

* duplicação;
* nomes vagos;
* funções extensas;
* condicionais profundamente aninhadas;
* comentários explicando código confuso;
* abstrações genéricas prematuras;
* classes utilitárias sem responsabilidade clara;
* parâmetros booleanos que alteram drasticamente o comportamento;
* efeitos colaterais escondidos;
* mutabilidade desnecessária.

### Testes

* testes acoplados à implementação;
* ausência de testes de unidade da aplicação e domínio;
* mocks excessivos;
* uso de infraestrutura real em testes unitários;
* testes não determinísticos;
* fixtures globais com estado mutável;
* ausência de cobertura de erros;
* teste que valida apenas status HTTP sem validar comportamento;
* teste que replica a implementação.

---

## Etapa 4 — Definir o plano de refatoração

Organize as alterações na seguinte ordem:

1. proteger comportamento com testes;
2. corrigir limites arquiteturais;
3. introduzir ou ajustar interfaces;
4. corrigir injeção de dependências;
5. mover regras para a camada correta;
6. fortalecer tipos;
7. reduzir duplicações;
8. simplificar funções e classes;
9. ajustar testes;
10. executar validações completas.

O plano deve priorizar alterações de menor risco.

Evite misturar na mesma mudança:

* refatoração arquitetural;
* alteração de regra de negócio;
* mudança de contrato;
* otimização de performance;
* atualização ampla de dependências;
* reformatação não relacionada.

---

## Regras de Clean Architecture

## Camada de domínio

A camada de domínio deve conter os conceitos centrais do negócio.

Pode conter:

* entidades;
* value objects;
* enums de domínio;
* regras invariantes;
* serviços de domínio;
* exceções de domínio;
* eventos de domínio.

Não deve depender de:

* FastAPI;
* SQLAlchemy;
* Pydantic;
* bibliotecas HTTP;
* brokers;
* bancos de dados;
* framework de injeção de dependências;
* detalhes de configuração;
* adapters externos.

Exemplo esperado:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChurchId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ChurchId cannot be empty.")
```

Entidades e value objects devem impedir, sempre que possível, a criação de estados inválidos.

---

## Camada de aplicação

A camada de aplicação deve:

* implementar casos de uso;
* orquestrar entidades e serviços;
* depender de abstrações;
* coordenar transações quando definido pela arquitetura;
* produzir resultados independentes de transporte;
* representar comandos e consultas por tipos explícitos.

Não deve:

* retornar respostas HTTP;
* importar routers ou controllers;
* acessar diretamente SQLAlchemy;
* construir implementações concretas;
* conhecer detalhes de infraestrutura.

Exemplo:

```python
from dataclasses import dataclass
from typing import Protocol


class ChurchRepository(Protocol):
    async def get_by_name(self, name: str) -> "Church | None":
        ...

    async def save(self, church: "Church") -> None:
        ...


@dataclass(frozen=True, slots=True)
class RegisterChurchCommand:
    name: str


@dataclass(frozen=True, slots=True)
class RegisterChurchResult:
    church_id: str


class RegisterChurchUseCase:
    def __init__(self, repository: ChurchRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        command: RegisterChurchCommand,
    ) -> RegisterChurchResult:
        existing_church = await self._repository.get_by_name(command.name)

        if existing_church is not None:
            raise ChurchAlreadyExistsError(command.name)

        church = Church.create(name=command.name)
        await self._repository.save(church)

        return RegisterChurchResult(church_id=church.id.value)
```

---

## Camada de infraestrutura

A infraestrutura deve implementar as portas definidas pelas camadas internas.

Pode conter:

* repositories SQLAlchemy;
* clientes HTTP;
* serviços de mensageria;
* adapters de cache;
* gateways externos;
* implementações de observabilidade;
* configurações de banco;
* migrations;
* integrações com provedores.

A infraestrutura não deve definir regras centrais do negócio.

Exemplo:

```python
class SqlAlchemyChurchRepository(ChurchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_name(self, name: str) -> Church | None:
        statement = select(ChurchModel).where(ChurchModel.name == name)
        model = await self._session.scalar(statement)

        if model is None:
            return None

        return ChurchMapper.to_domain(model)

    async def save(self, church: Church) -> None:
        model = ChurchMapper.to_model(church)
        self._session.add(model)
```

---

## Camada de apresentação

Controllers, handlers e routers devem ser finos.

Suas responsabilidades são:

* receber a entrada;
* validar o formato do transporte;
* converter DTO em comando;
* chamar o caso de uso;
* converter o resultado;
* traduzir erros para o protocolo utilizado.

Não devem:

* implementar regra de negócio;
* consultar banco diretamente;
* iniciar dependências concretas;
* controlar detalhes internos do domínio;
* realizar decisões de negócio.

Exemplo:

```python
@router.post("/churches", status_code=status.HTTP_201_CREATED)
@inject
async def register_church(
    request: RegisterChurchRequest,
    use_case: Provide[Container.register_church_use_case],
) -> RegisterChurchResponse:
    result = await use_case.execute(
        RegisterChurchCommand(name=request.name),
    )

    return RegisterChurchResponse(
        church_id=result.church_id,
    )
```

O padrão exato de integração com o framework web deve seguir o `AGENTS.md`.

---

## Regras de injeção de dependências

Utilize obrigatoriamente o framework definido no `AGENTS.md`.

Quando o projeto utilizar `dependency_injector`, siga as regras abaixo.

### Dependências devem ser declaradas no container

Exemplo:

```python
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.modules.church.presentation.api.routes",
        ],
    )

    database = providers.Singleton(
        Database,
        database_url=config.database.url,
    )

    church_repository = providers.Factory(
        SqlAlchemyChurchRepository,
        session=database.provided.session,
    )

    register_church_use_case = providers.Factory(
        RegisterChurchUseCase,
        repository=church_repository,
    )
```

### Não instanciar implementações concretas dentro de casos de uso

Incorreto:

```python
class RegisterChurchUseCase:
    def __init__(self) -> None:
        self._repository = SqlAlchemyChurchRepository()
```

Correto:

```python
class RegisterChurchUseCase:
    def __init__(self, repository: ChurchRepository) -> None:
        self._repository = repository
```

### Não utilizar o container como service locator

Incorreto:

```python
class RegisterChurchUseCase:
    async def execute(self, command: RegisterChurchCommand) -> None:
        repository = Container.church_repository()
```

O container deve compor o grafo de objetos fora das camadas de domínio e aplicação.

### Preferir constructor injection

Dependências obrigatórias devem ser recebidas pelo construtor.

```python
class RegisterChurchUseCase:
    def __init__(
        self,
        repository: ChurchRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher
```

Evite:

* setters;
* atributos públicos mutáveis;
* acesso global;
* resolução dinâmica desnecessária;
* dependências opcionais que alteram silenciosamente o comportamento.

### Escopo dos providers

Escolha o provider conforme o ciclo de vida:

* `Singleton`: recursos compartilhados e seguros para reutilização;
* `Factory`: objetos independentes por resolução;
* `Resource`: recursos com inicialização e finalização;
* `Dependency`: contratos fornecidos externamente;
* `Configuration`: valores de configuração.

Não utilize `Singleton` para objetos com estado mutável por requisição.

---

## Tipagem forte

Todo código refatorado deve possuir tipagem explícita compatível com as regras do projeto.

### APIs públicas

Funções e métodos públicos devem declarar:

* tipos dos parâmetros;
* tipo de retorno;
* nulabilidade;
* tipos genéricos;
* exceções relevantes por documentação quando necessário.

```python
async def find_church(
    church_id: ChurchId,
) -> Church | None:
    ...
```

### Evitar `Any`

Não utilize `Any` para acelerar a refatoração.

Quando um formato for conhecido, crie um tipo explícito:

* `dataclass`;
* `TypedDict`;
* `Protocol`;
* DTO;
* generic;
* value object;
* modelo Pydantic na borda.

### Protocols

Utilize `Protocol` para abstrações estruturais quando essa for a convenção do projeto.

```python
from typing import Protocol


class EventPublisher(Protocol):
    async def publish(self, event: DomainEvent) -> None:
        ...
```

Não crie interfaces sem necessidade de inversão de dependência, substituição, isolamento de infraestrutura ou testes.

### Tipos opcionais

Não propague `None` sem necessidade.

Incorreto:

```python
def get_name(church: Church | None) -> str | None:
    return church.name if church else None
```

Prefira validar a ausência no ponto correto e manter o restante do fluxo com tipos não opcionais.

### Type ignores

Não adicione:

```python
# type: ignore
```

sem justificar a causa e restringir o código ignorado ao menor escopo possível.

O type checker não deve ser silenciado para esconder:

* dependência incorreta;
* retorno inconsistente;
* abstração mal definida;
* uso inadequado de biblioteca;
* modelo de dados ambíguo.

---

## Aplicação de SOLID

### Single Responsibility Principle

Cada classe ou função deve possuir uma responsabilidade coerente.

Separe:

* validação de transporte;
* regra de negócio;
* persistência;
* serialização;
* publicação de eventos;
* integração externa.

Não separe código apenas para reduzir o número de linhas. A extração deve representar uma responsabilidade ou abstração real.

### Open/Closed Principle

Prefira extensão por abstrações e composição quando houver variações reais.

Não crie hierarquias complexas para cenários hipotéticos.

### Liskov Substitution Principle

Implementações devem preservar o contrato da abstração.

Uma implementação não deve:

* exigir pré-condições adicionais;
* retornar formatos incompatíveis;
* lançar erros inesperados sem contrato;
* ignorar parâmetros;
* alterar semântica do método.

### Interface Segregation Principle

Prefira portas específicas.

Incorreto:

```python
class ChurchRepository(Protocol):
    async def save(self, church: Church) -> None:
        ...

    async def delete(self, church_id: ChurchId) -> None:
        ...

    async def export_financial_report(self) -> bytes:
        ...
```

Separe contratos não relacionados.

### Dependency Inversion Principle

Casos de uso e domínio devem depender de abstrações internas.

Implementações externas devem implementar essas abstrações.

---

## Aplicação de DRY

Elimine duplicações que representem o mesmo conhecimento.

Exemplos de duplicações relevantes:

* mesma regra de negócio em dois casos de uso;
* mesma conversão entre domínio e persistência;
* mesma validação invariável;
* mesma tradução de erro;
* mesma construção de eventos.

Não remova duplicação apenas por semelhança sintática.

Dois trechos parecidos podem representar conceitos distintos e evoluir de forma independente.

Antes de extrair uma abstração, verifique:

* se os trechos mudam pelos mesmos motivos;
* se representam o mesmo conceito;
* se possuem o mesmo contrato;
* se a abstração terá um nome claro;
* se a extração reduz complexidade.

Prefira uma pequena duplicação explícita a uma abstração genérica e confusa.

---

## Regras de Clean Code

### Nomes

Use nomes que expressem intenção.

Evite:

```python
data
item
obj
manager
helper
utils
service
process
handle
execute_task
```

quando não houver contexto suficiente.

Prefira:

```python
registration_request
church_repository
contribution_calculator
membership_approval_policy
register_church
```

### Funções

Funções devem:

* possuir objetivo claro;
* trabalhar em um nível consistente de abstração;
* evitar efeitos colaterais escondidos;
* ter poucos parâmetros;
* retornar tipos previsíveis;
* falhar de maneira explícita.

### Condicionais

Utilize guard clauses para reduzir aninhamento.

Antes:

```python
if church is not None:
    if church.is_active:
        if user.can_manage(church):
            await update_church(church)
```

Depois:

```python
if church is None:
    raise ChurchNotFoundError()

if not church.is_active:
    raise InactiveChurchError()

if not user.can_manage(church):
    raise PermissionDeniedError()

await update_church(church)
```

### Comentários

Comentários devem explicar:

* decisões não óbvias;
* limitações externas;
* trade-offs;
* regras regulatórias;
* comportamento temporário;
* motivo de uma solução incomum.

Não use comentários para repetir o código.

### Exceções

Use exceções específicas.

Evite:

```python
raise Exception("Error")
```

Prefira:

```python
raise ChurchAlreadyExistsError(name=command.name)
```

Não capture exceções genéricas sem necessidade.

---

## Regras de refatoração de casos de uso

Um caso de uso deve representar uma intenção do sistema.

Exemplos:

```text
RegisterChurch
ApproveMemberRegistration
CreateCongregation
RecordContribution
ScheduleChurchEvent
AssignMemberToMinistry
```

Um caso de uso deve:

* receber um comando ou consulta tipada;
* depender de portas;
* orquestrar o domínio;
* retornar resultado tipado;
* não conhecer HTTP;
* não construir adapters;
* não manipular modelos de ORM diretamente.

Evite casos de uso genéricos como:

```text
ChurchService
MemberManager
DataProcessor
GenericCrudUseCase
```

Não force um CRUD genérico quando as operações representam intenções de negócio diferentes.

---

## Regras de refatoração de repositories

Repositories devem representar acesso a agregados ou conceitos de persistência relevantes.

As interfaces devem ser definidas na camada interna apropriada.

Evite expor:

* `Session`;
* queries;
* modelos ORM;
* filtros específicos de SQL;
* detalhes de paginação do banco;
* APIs da biblioteca de persistência.

Incorreto:

```python
async def find(
    self,
    filter_expression: BinaryExpression,
) -> ChurchModel | None:
    ...
```

Melhor:

```python
async def get_by_slug(
    self,
    slug: ChurchSlug,
) -> Church | None:
    ...
```

Não utilize repository para serviços externos que não representam persistência. Utilize nomes como:

* gateway;
* client;
* publisher;
* provider;
* notifier.

---

## Regras de mapeamento

Não misture indiscriminadamente:

* modelos ORM;
* entidades;
* DTOs;
* schemas de transporte.

Use mapeadores explícitos quando necessário.

```python
class ChurchMapper:
    @staticmethod
    def to_domain(model: ChurchModel) -> Church:
        ...

    @staticmethod
    def to_model(entity: Church) -> ChurchModel:
        ...
```

Não coloque métodos dependentes de ORM nas entidades de domínio.

Mapeadores devem ser testáveis e determinísticos.

---

## Regras de transação

O controle transacional deve seguir o padrão definido no `AGENTS.md`.

Quando for utilizado Unit of Work:

```python
class UnitOfWork(Protocol):
    churches: ChurchRepository

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
```

O caso de uso não deve depender de uma sessão concreta de banco.

Não distribua commits entre repositories distintos sem uma estratégia transacional explícita.

---

## Estratégia de testes

## Testes de caracterização

Crie testes de caracterização antes de modificar código sem cobertura.

Esses testes devem registrar o comportamento atual relevante, mesmo que a implementação interna esteja inadequada.

Após a refatoração, avalie se o teste ainda deve permanecer como teste de comportamento ou ser substituído por um teste mais semântico.

---

## Testes de unidade

Priorize testes unitários para:

* entidades;
* value objects;
* serviços de domínio;
* casos de uso;
* policies;
* mapeadores;
* validadores de regras.

Os testes devem usar fakes ou stubs baseados nos contratos internos.

Exemplo:

```python
class InMemoryChurchRepository:
    def __init__(self) -> None:
        self.churches: list[Church] = []

    async def get_by_name(self, name: str) -> Church | None:
        return next(
            (
                church
                for church in self.churches
                if church.name == name
            ),
            None,
        )

    async def save(self, church: Church) -> None:
        self.churches.append(church)
```

Prefira fakes simples a mocks altamente acoplados à sequência interna de chamadas.

---

## Testes de integração

Utilize testes de integração para validar:

* repository concreto;
* mapeamento ORM;
* migrations;
* container de DI;
* configuração;
* integração HTTP;
* transações;
* serialização;
* adapters externos simulados por servidor controlado.

Não replique em testes de integração toda a matriz já coberta por testes unitários.

---

## Testes do container de DI

Após alterar o container, valide:

* resolução dos providers;
* escopos;
* wiring;
* overrides;
* ciclo de vida de resources;
* ausência de dependências circulares;
* construção dos casos de uso.

Exemplo:

```python
def test_container_resolves_register_church_use_case() -> None:
    container = Container()

    use_case = container.register_church_use_case()

    assert isinstance(use_case, RegisterChurchUseCase)
```

Quando houver infraestrutura externa, use overrides:

```python
container.church_repository.override(
    providers.Object(fake_repository),
)
```

---

## Antipadrões proibidos

Não introduza ou mantenha deliberadamente:

* service locator;
* god classes;
* entidades anêmicas quando houver invariantes reais;
* domínio dependente de framework;
* repository genérico universal;
* classe `Utils` como destino de lógica sem responsável;
* `Any` indiscriminado;
* dicionários sem contrato;
* imports circulares;
* dependências globais mutáveis;
* singletons com estado de requisição;
* acesso direto ao container dentro de casos de uso;
* retorno de modelos ORM pela API;
* regras de negócio em routers;
* tratamento genérico de todas as exceções;
* mocks de detalhes internos;
* comentários para desabilitar lint sem justificativa;
* abstrações criadas apenas para aumentar quantidade de camadas.

---

## Critérios para mover código

Ao decidir para onde mover uma lógica, utilize estas perguntas.

### Deve estar no domínio?

Coloque no domínio quando:

* representa uma regra intrínseca do negócio;
* protege uma invariante;
* independe de infraestrutura;
* faz sentido no vocabulário do negócio.

### Deve estar em um caso de uso?

Coloque na aplicação quando:

* coordena entidades;
* executa uma intenção do usuário;
* depende de repositories ou gateways;
* controla o fluxo da operação;
* combina múltiplas regras e dependências.

### Deve estar em um adapter?

Coloque na infraestrutura quando:

* depende de banco;
* depende de HTTP;
* depende de broker;
* depende de filesystem;
* depende de framework;
* traduz um protocolo externo.

### Deve estar na apresentação?

Coloque na apresentação quando:

* interpreta uma requisição;
* converte protocolo em comando;
* converte resultado em resposta;
* traduz erro em status ou mensagem de transporte.

---

## Validações obrigatórias

Ao final da refatoração, execute os comandos definidos no projeto.

Exemplos possíveis:

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
ruff check .
```

```bash
ruff format --check .
```

```bash
mypy src
```

```bash
pyright
```

Utilize apenas os comandos e ferramentas configurados no projeto.

A refatoração somente deve ser considerada concluída quando:

* testes relevantes passarem;
* lint passar;
* formatação estiver correta;
* type checking passar;
* imports estiverem válidos;
* container resolver as dependências;
* não houver regressões conhecidas.

---

## Revisão final do diff

Antes de concluir, revise o diff procurando:

* mudanças funcionais acidentais;
* arquivos alterados sem necessidade;
* imports não utilizados;
* abstrações desnecessárias;
* nomes inconsistentes;
* comentários obsoletos;
* código morto;
* duplicação;
* alterações em contratos públicos;
* novos `Any`;
* novos `type: ignore`;
* instanciação direta de dependências;
* dependência de camada interna para externa;
* testes removidos ou enfraquecidos.

Não considere aumento de quantidade de arquivos como sinônimo de melhoria arquitetural.

A nova estrutura deve reduzir acoplamento e tornar as responsabilidades mais explícitas.

---

## Formato da resposta

Ao finalizar uma refatoração, apresente:

### 1. Diagnóstico

Liste objetivamente as principais violações encontradas.

Exemplo:

```text
- O controller acessava diretamente o repository SQLAlchemy.
- O caso de uso construía sua própria dependência.
- O modelo ORM era retornado pela camada de apresentação.
- A operação não possuía testes de comportamento.
```

### 2. Alterações realizadas

Descreva as mudanças arquiteturais e de código.

Exemplo:

```text
- Introduzida a porta ChurchRepository na camada de aplicação.
- Movida a implementação SQLAlchemy para infraestrutura.
- Registrado o repository e o use case no container de DI.
- Criados DTOs tipados para entrada e saída.
- Adicionados testes unitários e de integração.
```

### 3. Arquivos alterados

Informe os arquivos criados, modificados ou removidos.

### 4. Validações executadas

Informe os comandos executados e seus resultados.

Exemplo:

```text
- pytest: aprovado;
- ruff check: aprovado;
- mypy: aprovado.
```

### 5. Decisões e trade-offs

Explique somente decisões arquiteturais relevantes.

### 6. Pendências

Liste pendências reais que não puderam ser resolvidas.

Não declare que uma validação passou se ela não foi executada.

---

## Checklist de conclusão

Antes de concluir, confirme:

* [ ] O `AGENTS.md` atual foi lido.
* [ ] O comportamento existente foi identificado.
* [ ] Os testes relevantes foram executados antes da alteração.
* [ ] Código sem cobertura recebeu testes de caracterização.
* [ ] As dependências respeitam a direção da Clean Architecture.
* [ ] O domínio não depende de frameworks.
* [ ] Casos de uso dependem de abstrações.
* [ ] Controllers estão finos.
* [ ] Implementações concretas estão na infraestrutura.
* [ ] As dependências são construídas pelo container.
* [ ] O framework `dependency_injector` foi utilizado conforme o padrão do projeto.
* [ ] Não foi introduzido service locator.
* [ ] A tipagem está explícita.
* [ ] Não foram adicionados `Any` ou `type: ignore` injustificados.
* [ ] As responsabilidades estão bem separadas.
* [ ] Duplicações de conhecimento foram removidas.
* [ ] Não foram criadas abstrações prematuras.
* [ ] Testes unitários cobrem regras e casos de uso.
* [ ] Testes de integração cobrem adapters relevantes.
* [ ] O container de DI foi validado.
* [ ] Lint foi executado.
* [ ] Formatação foi validada.
* [ ] Type checking foi executado.
* [ ] A suíte de testes passou.
* [ ] O diff final foi revisado.
* [ ] Nenhuma alteração funcional acidental foi introduzida.

---

## Instrução operacional

Ao receber uma solicitação de refatoração:

1. leia o `AGENTS.md`;
2. inspecione o código afetado;
3. identifique o comportamento atual;
4. execute ou crie testes de proteção;
5. apresente internamente um plano incremental;
6. aplique as alterações em pequenos passos;
7. valide cada passo;
8. revise o grafo de dependências;
9. execute todas as verificações configuradas;
10. registre no contexto de `.agents` as novas preferências estabelecidas pelo usuário;
11. apresente diagnóstico, alterações, arquivos e validações.

Nunca substitua código funcional por uma reescrita completa sem necessidade comprovada.

Prefira refatorações seguras, incrementais, tipadas e protegidas por testes.
