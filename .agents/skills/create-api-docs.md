---

name: generate-openapi-docs
description: Gera, atualiza, valida e organiza documentação OpenAPI para APIs HTTP, mantendo o contrato sincronizado com os requisitos, casos de uso, modelos de domínio e implementação.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Generate OpenAPI Docs

## Objetivo

Gerar ou atualizar contratos OpenAPI completos, consistentes, fortemente tipados, reutilizáveis e preparados para:

* documentação interativa;
* geração de clientes;
* geração de SDKs;
* testes de contrato;
* validação de requisições e respostas;
* mocks de API;
* integração entre frontend e backend;
* revisão arquitetural;
* pipelines de CI/CD.

O documento OpenAPI deve ser tratado como parte do código-fonte da aplicação e como um contrato formal entre produtores e consumidores da API.

---

## Quando utilizar esta skill

Use esta skill quando a tarefa envolver:

* criar a documentação de uma nova API;
* documentar um novo endpoint;
* atualizar endpoints existentes;
* transformar requisitos funcionais em contrato HTTP;
* gerar um arquivo `openapi.yaml` ou `openapi.json`;
* revisar uma especificação OpenAPI existente;
* detectar divergências entre implementação e documentação;
* documentar schemas, autenticação, erros ou paginação;
* preparar uma API para Swagger UI, Redoc ou geração de SDK;
* gerar documentação a partir de casos de uso;
* aplicar design-first ou contract-first;
* validar compatibilidade retroativa da API.

Não utilize esta skill para documentar APIs que não sejam baseadas em HTTP, salvo quando houver uma representação HTTP compatível com OpenAPI.

---

## Princípios obrigatórios

### 1. Contract-first

Sempre que possível, o contrato OpenAPI deve ser criado ou atualizado antes da implementação do endpoint.

A ordem preferencial é:

1. analisar o requisito;
2. identificar o caso de uso;
3. definir os recursos HTTP;
4. definir os schemas;
5. definir os endpoints;
6. definir erros e regras de autorização;
7. validar a especificação;
8. implementar o código;
9. criar testes de contrato;
10. verificar sincronização entre código e contrato.

Quando o endpoint já estiver implementado, adote uma abordagem de sincronização:

1. inspecione rotas e controllers;
2. inspecione DTOs de entrada e saída;
3. inspecione regras de validação;
4. inspecione autenticação e autorização;
5. inspecione códigos HTTP retornados;
6. compare a implementação com o contrato;
7. corrija inconsistências;
8. reporte breaking changes.

---

### 2. Fonte única da verdade

Deve existir uma fonte canônica para a documentação OpenAPI.

Preferencialmente:

```text
docs/
└── openapi/
    ├── openapi.yaml
    ├── paths/
    ├── components/
    └── examples/
```

Para APIs pequenas, um único arquivo pode ser utilizado:

```text
docs/openapi/openapi.yaml
```

Para APIs médias ou grandes, utilize uma especificação modular.

Exemplo:

```text
docs/
└── openapi/
    ├── openapi.yaml
    ├── paths/
    │   ├── churches.yaml
    │   ├── members.yaml
    │   ├── congregations.yaml
    │   ├── ministries.yaml
    │   └── contributions.yaml
    ├── components/
    │   ├── schemas/
    │   │   ├── church.yaml
    │   │   ├── member.yaml
    │   │   ├── pagination.yaml
    │   │   └── problem-details.yaml
    │   ├── parameters/
    │   ├── responses/
    │   ├── request-bodies/
    │   └── security-schemes/
    └── examples/
```

Não duplique schemas equivalentes em arquivos ou endpoints diferentes.

---

### 3. Compatibilidade da versão

Utilize por padrão:

```yaml
openapi: 3.1.0
```

A versão poderá ser alterada quando:

* o projeto já possuir outra versão definida;
* alguma ferramenta obrigatória não suportar OpenAPI 3.1;
* houver requisito explícito de compatibilidade;
* o `AGENTS.md` determinar outra versão.

Nunca altere a versão OpenAPI de um projeto existente sem analisar o impacto sobre:

* Swagger UI;
* Redoc;
* linters;
* validadores;
* geradores de cliente;
* gateways;
* bibliotecas do backend;
* testes de contrato;
* pipelines existentes.

---

## Fontes que devem ser analisadas

Antes de gerar a documentação, procure nesta ordem:

1. `AGENTS.md`;
2. requisitos funcionais;
3. especificações de histórias;
4. documentação de domínio;
5. ADRs;
6. controllers ou handlers HTTP;
7. DTOs de entrada e saída;
8. entidades e Value Objects;
9. casos de uso;
10. políticas de autorização;
11. testes unitários;
12. testes de integração;
13. contratos OpenAPI existentes;
14. configurações de autenticação;
15. tratamento global de erros.

As instruções do `AGENTS.md` têm precedência sobre convenções genéricas desta skill.

Não invente comportamento quando a resposta puder ser obtida por inspeção do projeto.

Quando alguma informação indispensável estiver ausente, use uma suposição explícita e registre-a na seção de observações da entrega.

---

## Fluxo de execução

## Etapa 1 — Analisar o contexto

Identifique:

* recurso principal;
* atores envolvidos;
* casos de uso;
* comandos e consultas;
* regras de negócio;
* estados possíveis;
* permissões;
* entradas;
* saídas;
* erros;
* operações idempotentes;
* paginação;
* filtros;
* ordenação;
* concorrência;
* eventos relacionados;
* requisitos de segurança;
* requisitos de auditoria.

Monte internamente uma tabela semelhante a:

| Caso de uso      | Método | Caminho                | Entrada               | Saída            | Autorização        |
| ---------------- | ------ | ---------------------- | --------------------- | ---------------- | ------------------ |
| Cadastrar igreja | POST   | `/churches`            | `CreateChurchRequest` | `ChurchResponse` | administrador      |
| Consultar igreja | GET    | `/churches/{churchId}` | path parameter        | `ChurchResponse` | usuário autorizado |

Não inclua endpoints sem caso de uso ou necessidade identificável.

---

## Etapa 2 — Mapear casos de uso para HTTP

Utilize semântica HTTP corretamente.

### Métodos

* `GET`: consulta sem alteração de estado;
* `POST`: criação, comando não idempotente ou operação complexa;
* `PUT`: substituição integral idempotente;
* `PATCH`: alteração parcial;
* `DELETE`: remoção ou desativação de recurso;
* `HEAD`: consulta somente de metadados;
* `OPTIONS`: capacidades e políticas de comunicação.

Não use `POST` para todas as operações por conveniência.

Endpoints de ação devem ser usados somente quando a operação não puder ser representada adequadamente como manipulação de recurso.

Exemplo aceitável:

```text
POST /member-registration-requests/{registrationRequestId}/approval
```

Alternativa orientada a estado:

```text
PATCH /member-registration-requests/{registrationRequestId}
```

```json
{
  "status": "approved"
}
```

Escolha uma abordagem consistente com o modelo de domínio e com os padrões do projeto.

---

## Etapa 3 — Definir caminhos

Utilize:

* substantivos;
* nomes no plural;
* `kebab-case` para caminhos compostos;
* identificadores em parâmetros de caminho;
* hierarquia apenas quando houver relação de escopo real.

Exemplos:

```text
/churches
/churches/{churchId}
/churches/{churchId}/members
/member-registration-requests
/member-registration-requests/{registrationRequestId}
```

Evite:

```text
/createChurch
/getMembers
/delete-congregation
/api/doApproval
```

Não crie hierarquias excessivamente profundas.

Evite:

```text
/churches/{churchId}/congregations/{congregationId}/ministries/{ministryId}/members/{memberId}
```

Prefira recursos diretamente endereçáveis quando o contexto puder ser validado pela aplicação:

```text
/ministry-memberships/{membershipId}
```

---

## Etapa 4 — Definir `operationId`

Toda operação deve possuir um `operationId`:

* único;
* estável;
* descritivo;
* adequado para geração de clientes;
* independente do nome interno do controller.

Use preferencialmente `camelCase`.

Exemplos:

```yaml
operationId: createChurch
operationId: getChurchById
operationId: listChurchMembers
operationId: approveMemberRegistration
```

Não utilize nomes genéricos:

```yaml
operationId: execute
operationId: process
operationId: handler
operationId: endpoint1
```

---

## Etapa 5 — Organizar tags

Agrupe endpoints pelo recurso ou bounded context.

Exemplo:

```yaml
tags:
  - name: Churches
    description: Gerenciamento das igrejas e suas informações institucionais.

  - name: Members
    description: Gerenciamento de membros e solicitações de cadastro.

  - name: Congregations
    description: Gerenciamento de congregações vinculadas às igrejas.
```

Não use uma única tag genérica como `API`.

Não organize as tags conforme camadas técnicas, como:

* Controllers;
* Services;
* Repositories;
* Database.

As tags devem representar capacidades de negócio.

---

## Etapa 6 — Modelar schemas

Todo corpo de requisição e resposta deve possuir schema explícito.

Prefira schemas reutilizáveis em:

```yaml
components:
  schemas:
```

Exemplo:

```yaml
components:
  schemas:
    ChurchResponse:
      type: object
      additionalProperties: false
      required:
        - id
        - name
        - status
        - createdAt
        - updatedAt
      properties:
        id:
          type: string
          format: uuid
          description: Identificador único da igreja.
          example: 7a3aa748-53fd-47a9-b54e-429ba5e5405d

        name:
          type: string
          minLength: 2
          maxLength: 150
          description: Nome público da igreja.
          example: Igreja Presbiteriana Central

        status:
          $ref: '#/components/schemas/ChurchStatus'

        createdAt:
          type: string
          format: date-time
          description: Data e hora de criação no formato RFC 3339.

        updatedAt:
          type: string
          format: date-time
          description: Data e hora da última atualização no formato RFC 3339.
```

---

## Tipagem forte obrigatória

Não utilize schemas indefinidos ou parcialmente indefinidos.

É proibido usar estruturas equivalentes a tipos desconhecidos sem uma justificativa formal.

Evite:

```yaml
type: object
```

sem definição de propriedades.

Evite:

```yaml
additionalProperties: true
```

Evite:

```yaml
data: {}
```

Evite schemas genéricos como:

```yaml
AnyValue:
  description: Qualquer valor.
```

Evite respostas com objetos sem contrato:

```yaml
properties:
  metadata:
    type: object
```

Todo objeto deve declarar:

* `type`;
* `properties`;
* campos obrigatórios;
* restrições relevantes;
* comportamento de propriedades adicionais.

Utilize por padrão:

```yaml
additionalProperties: false
```

Quando um mapa dinâmico for realmente necessário, seu valor também deve ser tipado.

Exemplo:

```yaml
Metadata:
  type: object
  additionalProperties:
    type: string
```

Não use `additionalProperties: true`.

---

## Campos obrigatórios e nulabilidade

Diferencie corretamente:

* campo obrigatório;
* campo opcional;
* campo anulável;
* campo ausente;
* campo vazio.

Exemplo de campo obrigatório e não anulável:

```yaml
required:
  - name
properties:
  name:
    type: string
```

Exemplo de campo opcional e não anulável:

```yaml
properties:
  description:
    type: string
```

Exemplo de campo obrigatório e anulável em OpenAPI 3.1:

```yaml
required:
  - deletedAt
properties:
  deletedAt:
    type:
      - string
      - 'null'
    format: date-time
```

Não torne campos anuláveis apenas para simplificar a implementação.

---

## Restrições de validação

Represente no contrato as mesmas restrições aplicadas pela aplicação.

Utilize, conforme aplicável:

* `minLength`;
* `maxLength`;
* `minimum`;
* `maximum`;
* `exclusiveMinimum`;
* `exclusiveMaximum`;
* `multipleOf`;
* `minItems`;
* `maxItems`;
* `uniqueItems`;
* `pattern`;
* `format`;
* `enum`;
* `const`;
* `oneOf`;
* `anyOf`;
* `allOf`.

Exemplo:

```yaml
CreateChurchRequest:
  type: object
  additionalProperties: false
  required:
    - name
  properties:
    name:
      type: string
      minLength: 2
      maxLength: 150
      example: Igreja Presbiteriana Central

    email:
      type: string
      format: email
      maxLength: 254
      example: contato@igreja.example
```

Não documente uma restrição que não seja validada pela aplicação sem informar que a implementação deverá ser ajustada.

---

## Enums

Enums devem possuir nomes de domínio claros.

Exemplo:

```yaml
ChurchStatus:
  type: string
  description: Estado atual da igreja no sistema.
  enum:
    - pending_activation
    - active
    - suspended
    - deactivated
  example: active
```

Não use valores ambíguos:

```yaml
enum:
  - A
  - I
  - X
```

Quando o código possuir enums com valores legados pouco claros, preserve os valores reais do contrato e documente o significado de cada um.

---

## Identificadores

Identificadores UUID devem ser representados como:

```yaml
type: string
format: uuid
```

Não documente UUIDs como números.

Identificadores numéricos devem definir formato e limites quando aplicável:

```yaml
type: integer
format: int64
minimum: 1
```

Nunca exponha IDs internos de banco de dados quando houver identificador público definido pelo domínio.

---

## Datas e horários

Use:

```yaml
type: string
format: date
```

para datas sem horário.

Use:

```yaml
type: string
format: date-time
```

para instantes temporais.

As APIs devem preferir datas e horários em formato ISO 8601/RFC 3339.

Exemplos:

```yaml
birthDate:
  type: string
  format: date
  example: '1995-08-17'

createdAt:
  type: string
  format: date-time
  example: '2026-07-25T23:30:00-03:00'
```

Não utilize datas formatadas para exibição:

```text
25/07/2026
```

como representação canônica da API.

---

## Valores monetários

Não represente valores monetários com números de ponto flutuante.

Evite:

```yaml
amount:
  type: number
  format: float
```

Utilize uma das abordagens definidas pelo projeto.

### Valor em unidade mínima

```yaml
amountInCents:
  type: integer
  format: int64
  minimum: 0
  description: Valor monetário em centavos.
  example: 15990
```

### Valor decimal como string

```yaml
amount:
  type: string
  pattern: '^-?\d+\.\d{2}$'
  description: Valor monetário decimal com duas casas.
  example: '159.90'
```

Quando houver múltiplas moedas, utilize um objeto:

```yaml
Money:
  type: object
  additionalProperties: false
  required:
    - amount
    - currency
  properties:
    amount:
      type: string
      pattern: '^-?\d+\.\d{2}$'
      example: '159.90'

    currency:
      type: string
      pattern: '^[A-Z]{3}$'
      example: BRL
```

---

## Value Objects

Value Objects do domínio devem possuir representação explícita.

Exemplo:

```yaml
Cpf:
  type: string
  pattern: '^\d{11}$'
  description: CPF contendo somente dígitos.
  example: '12345678909'
```

```yaml
EmailAddress:
  type: string
  format: email
  maxLength: 254
  example: membro@example.com
```

Não exponha diretamente a estrutura interna de um Value Object quando ela for apenas um detalhe de implementação.

---

## Polimorfismo

Use `oneOf` quando o valor puder possuir exatamente uma entre várias estruturas.

Exemplo:

```yaml
ContactDestination:
  oneOf:
    - $ref: '#/components/schemas/EmailDestination'
    - $ref: '#/components/schemas/PhoneDestination'
  discriminator:
    propertyName: type
    mapping:
      email: '#/components/schemas/EmailDestination'
      phone: '#/components/schemas/PhoneDestination'
```

Cada alternativa deve ser inequivocamente identificável.

Não use polimorfismo para ocultar ausência de modelagem.

---

## Etapa 7 — Separar schemas de entrada e saída

Não reutilize automaticamente o mesmo schema para:

* criação;
* atualização;
* persistência;
* resposta;
* evento;
* representação interna.

Exemplo:

```text
CreateChurchRequest
UpdateChurchRequest
ChurchResponse
ChurchSummaryResponse
ChurchCreatedEvent
```

Essa separação evita expor:

* campos internos;
* IDs indevidos;
* atributos de auditoria;
* flags administrativas;
* campos somente de leitura;
* propriedades calculadas;
* dados sensíveis.

Use `readOnly` e `writeOnly` somente quando a reutilização for realmente vantajosa.

---

## Etapa 8 — Documentar parâmetros

Todo parâmetro deve declarar:

* nome;
* localização;
* obrigatoriedade;
* descrição;
* schema;
* exemplo quando útil.

Exemplo:

```yaml
ChurchId:
  name: churchId
  in: path
  required: true
  description: Identificador único da igreja.
  schema:
    type: string
    format: uuid
```

Parâmetros de caminho são sempre obrigatórios.

Não use corpos de requisição em operações `GET` sem uma justificativa explícita e compatibilidade confirmada.

---

## Paginação

Adote o padrão existente no projeto.

Quando não houver padrão definido, prefira paginação por cursor para conjuntos grandes ou mutáveis.

### Paginação por cursor

Parâmetros:

```yaml
CursorParameter:
  name: cursor
  in: query
  required: false
  description: Cursor opaco retornado pela página anterior.
  schema:
    type: string
    minLength: 1

PageSizeParameter:
  name: limit
  in: query
  required: false
  description: Quantidade máxima de registros retornados.
  schema:
    type: integer
    minimum: 1
    maximum: 100
    default: 20
```

Resposta:

```yaml
CursorPagination:
  type: object
  additionalProperties: false
  required:
    - hasNextPage
  properties:
    nextCursor:
      type:
        - string
        - 'null'
      description: Cursor da próxima página ou null quando não houver próxima página.

    hasNextPage:
      type: boolean
      example: true
```

O cursor deve ser documentado como opaco. Consumidores não devem depender de seu conteúdo interno.

### Paginação por página

Quando o projeto utilizar página e tamanho:

```yaml
page:
  type: integer
  minimum: 1
  default: 1

pageSize:
  type: integer
  minimum: 1
  maximum: 100
  default: 20
```

Documente claramente se a primeira página é `0` ou `1`.

---

## Filtros e ordenação

Filtros devem possuir tipo e semântica explícitos.

Exemplo:

```yaml
- name: status
  in: query
  required: false
  schema:
    $ref: '#/components/schemas/MemberStatus'

- name: createdFrom
  in: query
  required: false
  schema:
    type: string
    format: date-time
```

Para ordenação, restrinja os campos aceitos:

```yaml
- name: sortBy
  in: query
  required: false
  schema:
    type: string
    enum:
      - name
      - createdAt
      - updatedAt
    default: createdAt

- name: sortDirection
  in: query
  required: false
  schema:
    type: string
    enum:
      - asc
      - desc
    default: desc
```

Não aceite campos arbitrários em `sortBy`.

---

## Etapa 9 — Definir corpos de requisição

Todo corpo deve declarar:

* `required`;
* tipo de mídia;
* schema;
* exemplo representativo quando útil.

Exemplo:

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreateChurchRequest'
      examples:
        default:
          summary: Cadastro de uma igreja
          value:
            name: Igreja Presbiteriana Central
            email: contato@igreja.example
```

Não inclua campos gerados pelo servidor em requisições de criação.

Exemplos de campos que normalmente não pertencem a uma requisição:

* `id`;
* `createdAt`;
* `updatedAt`;
* `createdBy`;
* `version`.

---

## Etapa 10 — Definir respostas

Documente todas as respostas relevantes e realmente produzidas.

Exemplo para criação:

```yaml
responses:
  '201':
    description: Igreja cadastrada com sucesso.
    headers:
      Location:
        description: URI do recurso criado.
        schema:
          type: string
          format: uri
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ChurchResponse'

  '400':
    $ref: '#/components/responses/BadRequest'

  '401':
    $ref: '#/components/responses/Unauthorized'

  '403':
    $ref: '#/components/responses/Forbidden'

  '409':
    $ref: '#/components/responses/Conflict'

  '422':
    $ref: '#/components/responses/UnprocessableEntity'

  '500':
    $ref: '#/components/responses/InternalServerError'
```

Não adicione códigos de resposta que a aplicação nunca retorna.

Não omita respostas de erro conhecidas.

---

## Semântica recomendada de status HTTP

Utilize conforme o comportamento real:

* `200 OK`: consulta ou atualização com conteúdo;
* `201 Created`: recurso criado;
* `202 Accepted`: processamento assíncrono aceito;
* `204 No Content`: sucesso sem corpo;
* `400 Bad Request`: requisição sintaticamente inválida;
* `401 Unauthorized`: autenticação ausente ou inválida;
* `403 Forbidden`: usuário autenticado sem permissão;
* `404 Not Found`: recurso não encontrado;
* `409 Conflict`: conflito com o estado atual;
* `412 Precondition Failed`: precondição de concorrência falhou;
* `415 Unsupported Media Type`: mídia não suportada;
* `422 Unprocessable Content`: entrada sintaticamente válida, mas semanticamente inválida;
* `429 Too Many Requests`: limite de requisições excedido;
* `500 Internal Server Error`: erro inesperado;
* `503 Service Unavailable`: serviço temporariamente indisponível.

Não use `200` para todos os resultados.

---

## Erros padronizados

Prefira um schema inspirado em Problem Details.

Exemplo:

```yaml
ProblemDetails:
  type: object
  additionalProperties: false
  required:
    - type
    - title
    - status
    - detail
    - instance
    - code
  properties:
    type:
      type: string
      format: uri
      description: URI que identifica a categoria do problema.
      example: https://api.example.com/problems/church-name-already-exists

    title:
      type: string
      description: Resumo legível da categoria do problema.
      example: Nome de igreja já cadastrado

    status:
      type: integer
      minimum: 400
      maximum: 599
      example: 409

    detail:
      type: string
      description: Explicação específica desta ocorrência.
      example: Já existe uma igreja cadastrada com o nome informado.

    instance:
      type: string
      description: Identificador ou URI desta ocorrência.
      example: /churches

    code:
      type: string
      pattern: '^[A-Z][A-Z0-9_]*$'
      description: Código estável e processável pelo consumidor.
      example: CHURCH_NAME_ALREADY_EXISTS

    traceId:
      type:
        - string
        - 'null'
      description: Identificador utilizado para rastreamento da requisição.
      example: 01J3SC6NKM5A7QEKDWQBVQP05M

    errors:
      type: array
      description: Erros específicos associados aos campos da requisição.
      items:
        $ref: '#/components/schemas/FieldError'
```

```yaml
FieldError:
  type: object
  additionalProperties: false
  required:
    - field
    - code
    - message
  properties:
    field:
      type: string
      example: name

    code:
      type: string
      example: STRING_TOO_SHORT

    message:
      type: string
      example: O nome deve possuir pelo menos 2 caracteres.
```

Os códigos de erro devem ser estáveis e próprios para processamento por aplicações clientes.

Não exponha:

* stack traces;
* nomes de tabelas;
* consultas SQL;
* nomes internos de classes;
* caminhos internos do servidor;
* tokens;
* segredos;
* detalhes de infraestrutura.

---

## Etapa 11 — Documentar segurança

Declare os mecanismos em:

```yaml
components:
  securitySchemes:
```

Exemplo com Bearer JWT:

```yaml
BearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
  description: Token de acesso JWT enviado no cabeçalho Authorization.
```

Aplicação global:

```yaml
security:
  - BearerAuth: []
```

Endpoint público:

```yaml
security: []
```

Não documente apenas a autenticação. Registre também, na descrição da operação:

* perfil necessário;
* escopo;
* permissão;
* regra de ownership;
* restrição por igreja;
* restrição por congregação;
* condição de acesso.

Exemplo:

```yaml
description: |
  Retorna os dados da igreja.

  Requer que o usuário autenticado pertença à igreja solicitada ou possua
  permissão administrativa global.
```

Não exponha detalhes de implementação de claims internos que não façam parte do contrato público.

---

## Multi-tenancy

Quando a API for multi-tenant, documente explicitamente como o tenant é determinado:

* token;
* subdomínio;
* cabeçalho;
* caminho;
* configuração da sessão.

Prefira obter a organização ou igreja a partir da identidade autenticada quando isso fizer parte da política arquitetural.

Não aceite um `tenantId` arbitrário no corpo da requisição quando ele puder ser derivado com segurança do usuário autenticado.

Se o identificador da igreja fizer parte do caminho:

```text
/churches/{churchId}/members
```

documente que o backend deve validar a associação entre usuário e igreja.

Nunca trate a presença do identificador no caminho como autorização suficiente.

---

## Idempotência

Operações que possam sofrer repetição por timeout, retry ou falha de rede devem documentar idempotência quando aplicável.

Exemplo:

```yaml
IdempotencyKey:
  name: Idempotency-Key
  in: header
  required: true
  description: |
    Chave única gerada pelo cliente. Requisições repetidas com a mesma chave
    e o mesmo conteúdo devem produzir o mesmo resultado lógico.
  schema:
    type: string
    minLength: 16
    maxLength: 128
```

Utilize especialmente em operações como:

* contribuições;
* pagamentos;
* geração de cobranças;
* criação de registros críticos;
* comandos disparados por integrações externas.

Documente:

* período de retenção da chave, quando conhecido;
* comportamento em payload divergente;
* resposta de repetição;
* códigos de conflito.

---

## Concorrência otimista

Quando atualizações concorrentes forem relevantes, documente o mecanismo adotado.

Exemplo com `ETag`:

```yaml
headers:
  ETag:
    description: Versão atual da representação.
    schema:
      type: string
```

Na atualização:

```yaml
- name: If-Match
  in: header
  required: true
  description: ETag recebido na consulta anterior.
  schema:
    type: string
```

Documente `412 Precondition Failed` quando a versão não corresponder.

Não utilize concorrência otimista no contrato sem suporte correspondente na implementação.

---

## Processamento assíncrono

Quando uma operação for assíncrona, utilize `202 Accepted`.

Exemplo:

```yaml
responses:
  '202':
    description: Solicitação aceita para processamento.
    headers:
      Location:
        description: URI utilizada para consultar o processamento.
        schema:
          type: string
          format: uri
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AsyncOperationResponse'
```

```yaml
AsyncOperationResponse:
  type: object
  additionalProperties: false
  required:
    - operationId
    - status
  properties:
    operationId:
      type: string
      format: uuid

    status:
      type: string
      enum:
        - pending
        - processing
        - completed
        - failed
```

Não retorne `201 Created` antes de o recurso realmente existir, salvo quando o recurso criado for a própria operação assíncrona.

---

## Webhooks e callbacks

Quando a API enviar notificações HTTP para consumidores, documente:

* evento;
* payload;
* autenticação;
* assinatura;
* retentativas;
* timeout;
* idempotência;
* respostas esperadas;
* política de falha.

Não documente webhooks apenas com uma descrição textual quando a estrutura puder ser formalizada.

---

## Etapa 12 — Criar exemplos

Adicione exemplos que:

* sejam válidos conforme o schema;
* representem casos reais;
* não contenham dados pessoais reais;
* não exponham segredos;
* utilizem identificadores fictícios;
* respeitem formatos;
* permaneçam sincronizados com o contrato.

Exemplo:

```yaml
examples:
  activeChurch:
    summary: Igreja ativa
    value:
      id: 7a3aa748-53fd-47a9-b54e-429ba5e5405d
      name: Igreja Presbiteriana Central
      status: active
      createdAt: '2026-07-25T23:30:00-03:00'
      updatedAt: '2026-07-25T23:30:00-03:00'
```

Não use exemplos incompatíveis com:

* `required`;
* `enum`;
* `pattern`;
* `format`;
* limites numéricos;
* nulabilidade.

---

## Etapa 13 — Adicionar descrições úteis

Descrições devem explicar comportamento e semântica, não apenas repetir o nome.

Ruim:

```yaml
name:
  type: string
  description: Nome.
```

Melhor:

```yaml
name:
  type: string
  description: Nome público da igreja exibido aos membros e administradores.
```

Para cada operação, documente quando relevante:

* objetivo;
* precondições;
* regras de autorização;
* efeitos colaterais;
* idempotência;
* comportamento transacional;
* consequências de repetição;
* regras de validação;
* consistência eventual;
* processamento assíncrono;
* eventos publicados;
* campos imutáveis.

Não transforme a especificação em um documento de implementação interna.

---

## Etapa 14 — Modularizar a especificação

Para arquivos externos, utilize referências:

```yaml
paths:
  /churches:
    $ref: './paths/churches.yaml'

components:
  schemas:
    ChurchResponse:
      $ref: './components/schemas/church.yaml#/ChurchResponse'
```

Evite referências circulares.

Garanta que:

* todos os caminhos relativos estejam corretos;
* arquivos referenciados existam;
* os fragmentos JSON Pointer sejam válidos;
* o bundling da especificação seja possível;
* a visualização local funcione.

Quando a ferramenta utilizada não suportar múltiplos arquivos, gere também uma versão consolidada:

```text
docs/openapi/dist/openapi.bundle.yaml
```

O arquivo modular deve permanecer como fonte principal.

---

## Estrutura mínima do documento principal

```yaml
openapi: 3.1.0

info:
  title: SaaS Igrejas API
  version: 1.0.0
  description: |
    API responsável pelas funcionalidades do SaaS de gestão de igrejas.

servers:
  - url: https://api.example.com
    description: Produção

  - url: https://api.staging.example.com
    description: Homologação

tags:
  - name: Churches
    description: Gerenciamento de igrejas.

paths: {}

components:
  schemas: {}
  parameters: {}
  responses: {}
  securitySchemes: {}
```

Não inclua URLs fictícias como se fossem ambientes reais. Quando a URL não for conhecida, utilize um placeholder claramente identificável ou omita `servers`.

---

## Versionamento da API

Diferencie:

* versão do documento OpenAPI;
* versão da API;
* versão da aplicação;
* versão do schema de eventos.

Exemplo:

```yaml
openapi: 3.1.0
info:
  version: 1.4.0
```

A propriedade `openapi` identifica a versão da especificação.

A propriedade `info.version` identifica a versão do contrato da API.

Quando o projeto utilizar versionamento por caminho:

```text
/v1/churches
```

mantenha consistência em todos os endpoints.

Não adicione versionamento por caminho sem verificar o padrão arquitetural existente.

---

## Compatibilidade retroativa

Antes de atualizar um contrato existente, analise se a alteração é breaking.

Considere breaking change:

* remover endpoint;
* remover método;
* remover campo de resposta;
* tornar campo opcional obrigatório;
* alterar tipo;
* alterar formato;
* restringir enum;
* reduzir limite permitido;
* alterar semântica de campo;
* alterar status de sucesso;
* alterar estrutura de erro;
* alterar autenticação;
* adicionar autorização mais restritiva;
* renomear `operationId`;
* modificar comportamento de nulabilidade;
* alterar campo de leitura para escrita ou vice-versa.

Normalmente não é breaking:

* adicionar endpoint;
* adicionar campo opcional de requisição;
* adicionar campo de resposta quando clientes toleram propriedades extras;
* adicionar novo status de erro já previsto pelo protocolo;
* ampliar enum apenas quando consumidores forem preparados para valores desconhecidos;
* melhorar descrições;
* adicionar exemplos.

A classificação deve considerar o comportamento dos consumidores reais.

Nunca afirme que uma mudança é retrocompatível apenas porque o YAML continua válido.

---

## Validação obrigatória

Após gerar ou alterar a especificação:

1. valide a sintaxe YAML ou JSON;
2. valide a estrutura OpenAPI;
3. resolva todas as referências;
4. execute o linter configurado pelo projeto;
5. valide os exemplos contra os schemas;
6. verifique `operationId` duplicado;
7. verifique schemas não utilizados;
8. verifique respostas sem descrição;
9. verifique parâmetros de caminho;
10. verifique autenticação;
11. verifique breaking changes;
12. gere uma versão consolidada quando aplicável;
13. renderize a documentação para inspeção;
14. execute testes de contrato existentes.

Utilize primeiro as ferramentas já configuradas no projeto.

Possíveis ferramentas, quando já adotadas ou aprovadas:

* Redocly CLI;
* Spectral;
* Swagger CLI;
* openapi-generator;
* Schemathesis;
* Prism;
* Swagger UI;
* Redoc.

Não introduza uma nova dependência sem verificar as decisões técnicas do projeto.

---

## Regras para lint

Quando o projeto ainda não possuir regras próprias, verifique pelo menos:

* presença de `info`;
* presença de `operationId`;
* unicidade de `operationId`;
* descrições das operações;
* tags válidas;
* respostas de sucesso;
* respostas de erro;
* exemplos válidos;
* schemas fechados;
* ausência de tipos desconhecidos;
* segurança documentada;
* convenção dos caminhos;
* convenção dos nomes;
* formatos válidos;
* referências resolvíveis.

Trate erros de lint como falhas da entrega.

Warnings somente podem permanecer quando:

* houver justificativa;
* não representarem contrato ambíguo;
* forem registrados na entrega.

---

## Integração com CI

Quando solicitado, adicione ou atualize uma etapa de CI para:

1. instalar o validador;
2. validar a especificação;
3. executar lint;
4. gerar bundle;
5. detectar breaking changes;
6. publicar artefatos;
7. impedir merge em caso de contrato inválido.

Exemplo conceitual:

```yaml
- name: Validate OpenAPI
  run: make openapi-validate

- name: Lint OpenAPI
  run: make openapi-lint

- name: Check breaking changes
  run: make openapi-breaking-check
```

Prefira comandos encapsulados em scripts, `Makefile`, `Taskfile` ou ferramenta equivalente, evitando lógica extensa diretamente no workflow.

---

## Testes de contrato

Quando a tarefa incluir implementação, gere ou atualize testes que verifiquem:

* método;
* caminho;
* parâmetros;
* autenticação;
* corpo da requisição;
* códigos HTTP;
* headers;
* corpo da resposta;
* schema de erro;
* nulabilidade;
* enums;
* limites;
* formatos;
* propriedades adicionais;
* exemplos.

O contrato deve ser executável sempre que possível.

Evite testes que apenas comparem snapshots extensos do arquivo OpenAPI.

Prefira verificações semânticas.

---

## Sincronização com o código

Quando a documentação for derivada de decorators, annotations ou modelos do framework:

* verifique o documento gerado;
* não presuma que geração automática produz um contrato correto;
* adicione descrições e exemplos;
* remova schemas genéricos;
* corrija tipos opcionais e anuláveis;
* defina códigos de erro;
* verifique segurança;
* verifique aliases e nomes externos;
* garanta estabilidade do `operationId`.

Quando o projeto utilizar um arquivo OpenAPI manual como fonte principal:

* não altere decorators de documentação sem necessidade;
* mantenha o arquivo manual sincronizado com os DTOs;
* utilize testes para detectar divergências.

---

## Regras específicas para Python

Quando a API for implementada em Python:

* preserve tipagem forte;
* não utilize `Any` nos contratos internos usados para gerar OpenAPI;
* não utilize `dict` sem tipos;
* não utilize `dict[str, Any]`;
* não utilize modelos com propriedades desconhecidas;
* não ignore erros do analisador de tipos;
* diferencie DTOs de entrada, saída e domínio;
* não exponha entidades diretamente;
* mantenha os schemas compatíveis com os tipos reais da aplicação.

Evite:

```python
def create_church(payload: dict) -> dict:
    ...
```

Prefira:

```python
def create_church(payload: CreateChurchRequest) -> ChurchResponse:
    ...
```

Quando utilizar Pydantic:

* defina modelos explícitos;
* proíba campos extras quando essa for a regra do contrato;
* declare restrições;
* declare aliases conscientemente;
* não use `Any`;
* verifique o schema OpenAPI gerado;
* não acople o domínio ao framework de validação.

Exemplo conceitual:

```python
from pydantic import BaseModel, ConfigDict, Field


class CreateChurchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=150)
    email: str | None = Field(default=None, max_length=254)
```

Os modelos HTTP pertencem à camada de interface ou adapters, não à camada de domínio.

---

## Clean Architecture

A documentação deve refletir o contrato externo da aplicação, não a estrutura interna.

Não exponha no OpenAPI:

* entidades de persistência;
* modelos ORM;
* nomes de repositórios;
* objetos de sessão;
* estruturas específicas do banco;
* classes internas;
* detalhes de mensageria;
* detalhes de injeção de dependência.

O fluxo esperado é:

```text
HTTP Request
    ↓
Request DTO
    ↓
Controller / Handler
    ↓
Input Port / Use Case
    ↓
Domain
    ↓
Output DTO
    ↓
HTTP Response
```

O contrato OpenAPI deve documentar principalmente:

```text
HTTP Request DTO ↔ HTTP Response DTO
```

Não documente diretamente entidades de domínio como contratos HTTP quando isso criar acoplamento indevido.

---

## Segurança de dados

Antes de documentar um campo, analise se ele pode ser exposto.

Nunca inclua em respostas públicas:

* senha;
* hash de senha;
* token;
* segredo;
* chave privada;
* segredo de webhook;
* credencial;
* dados internos de autenticação;
* observação administrativa sigilosa;
* informações sensíveis sem autorização adequada.

Campos sensíveis aceitos em requisições devem usar:

```yaml
writeOnly: true
```

Exemplo:

```yaml
password:
  type: string
  format: password
  minLength: 12
  writeOnly: true
```

Campos gerados somente pelo servidor podem usar:

```yaml
readOnly: true
```

---

## LGPD e privacidade

Quando houver dados pessoais:

* documente somente os campos necessários;
* não use exemplos com dados reais;
* diferencie endpoints administrativos e pessoais;
* documente regras de acesso;
* evite retornar dados completos em listagens;
* utilize schemas resumidos;
* não exponha dados sensíveis por conveniência;
* considere consentimentos;
* considere finalidade de uso;
* considere exclusão ou anonimização.

Exemplo:

```text
MemberSummaryResponse
MemberDetailsResponse
MemberAdministrativeResponse
```

Não reutilize `MemberResponse` indiscriminadamente em todos os contextos.

---

## Checklist de qualidade

Antes de concluir, confirme:

### Estrutura

* [ ] O documento possui versão OpenAPI válida.
* [ ] `info.title` está definido.
* [ ] `info.version` está definido.
* [ ] Os servidores são reais ou claramente marcados.
* [ ] As tags representam capacidades de negócio.
* [ ] A especificação pode ser carregada integralmente.

### Endpoints

* [ ] Os caminhos usam substantivos.
* [ ] Os métodos HTTP possuem semântica correta.
* [ ] Cada operação possui `operationId`.
* [ ] Cada operação possui `summary`.
* [ ] Operações complexas possuem `description`.
* [ ] Parâmetros estão corretamente tipados.
* [ ] Parâmetros de caminho são obrigatórios.
* [ ] Paginação está documentada.
* [ ] Filtros e ordenação estão restritos.

### Schemas

* [ ] Não existem tipos desconhecidos.
* [ ] Não existem objetos parcialmente desconhecidos.
* [ ] Não existe `additionalProperties: true`.
* [ ] Objetos fechados usam `additionalProperties: false`.
* [ ] Campos obrigatórios estão em `required`.
* [ ] Nulabilidade está correta.
* [ ] Enums são explícitos.
* [ ] Datas possuem formato.
* [ ] UUIDs usam `format: uuid`.
* [ ] Valores monetários não usam ponto flutuante.
* [ ] Restrições refletem a implementação.
* [ ] Entradas e saídas estão separadas quando necessário.

### Respostas

* [ ] Todos os status relevantes estão documentados.
* [ ] A resposta de sucesso corresponde ao comportamento real.
* [ ] Erros utilizam schema padronizado.
* [ ] Erros possuem códigos estáveis.
* [ ] Headers relevantes estão documentados.
* [ ] Não existem respostas com corpo indefinido.

### Segurança

* [ ] O mecanismo de autenticação está declarado.
* [ ] Endpoints públicos usam `security: []`.
* [ ] Regras de autorização estão descritas.
* [ ] Dados sensíveis não são expostos.
* [ ] Multi-tenancy está documentado.
* [ ] Exemplos não contêm dados reais.

### Validação

* [ ] O YAML ou JSON é válido.
* [ ] A estrutura OpenAPI é válida.
* [ ] Todas as referências foram resolvidas.
* [ ] O linter foi executado.
* [ ] Exemplos são compatíveis com os schemas.
* [ ] Não existem `operationId` duplicados.
* [ ] Breaking changes foram analisadas.
* [ ] Testes de contrato foram executados quando disponíveis.

---

## Formato da entrega

Ao concluir uma tarefa, apresente:

### 1. Arquivos criados ou alterados

Exemplo:

```text
docs/openapi/openapi.yaml
docs/openapi/paths/churches.yaml
docs/openapi/components/schemas/church.yaml
```

### 2. Endpoints documentados

Exemplo:

```text
POST   /churches
GET    /churches/{churchId}
GET    /churches
PATCH  /churches/{churchId}
```

### 3. Decisões adotadas

Informe objetivamente:

* padrão de paginação;
* estratégia de autenticação;
* estrutura de erros;
* convenções de nomes;
* organização dos schemas;
* representação monetária;
* abordagem de idempotência;
* comportamento assíncrono.

### 4. Validações realizadas

Informe os comandos realmente executados e seus resultados.

Exemplo:

```text
OpenAPI validation: passed
Lint: passed
Reference resolution: passed
Breaking change check: passed
```

Não declare uma validação como executada quando ela não tiver sido realizada.

### 5. Pendências ou suposições

Liste apenas informações relevantes ainda não confirmadas.

Exemplo:

```text
- A URL de produção ainda não está definida.
- O tempo de retenção da chave de idempotência não foi especificado.
- A permissão necessária para suspender uma igreja precisa ser confirmada.
```

---

## Restrições finais

Nunca:

* gere documentação com tipos desconhecidos;
* use objetos parcialmente tipados;
* invente endpoints sem requisito;
* invente regras de negócio;
* documente campos inexistentes sem sinalizar a mudança;
* esconda divergências entre código e contrato;
* exponha modelos internos;
* exponha dados sensíveis;
* ignore autenticação;
* ignore respostas de erro;
* use exemplos inválidos;
* declare testes não executados;
* introduza breaking changes silenciosamente;
* altere convenções existentes sem justificativa;
* trate documentação gerada automaticamente como necessariamente correta.

Sempre:

* siga o `AGENTS.md`;
* preserve tipagem forte;
* utilize schemas explícitos;
* reutilize componentes;
* mantenha separação entre domínio e HTTP;
* valide o documento;
* analise compatibilidade;
* registre suposições;
* mantenha o contrato legível para humanos e máquinas.
