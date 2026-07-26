# Especificação — Cadastro de Igreja

## 1. Identificação

**Código:** `CHURCH-001`
**Título:** Cadastrar uma igreja
**Módulo:** Administração da organização
**Prioridade:** Crítica
**Versão:** MVP
**Status:** A especificar / Pronta para refinamento

---

## 2. Objetivo

Permitir que uma nova igreja seja registrada na plataforma, criando a estrutura organizacional inicial necessária para que seus usuários possam acessar e configurar o SaaS.

O cadastro da igreja deverá:

* criar a organização principal;
* criar a congregação sede;
* criar ou associar o primeiro usuário administrador;
* garantir o isolamento dos dados da igreja;
* disponibilizar a igreja para configurações posteriores;
* impedir cadastros inválidos ou duplicados.

---

## 3. História de usuário

**Como** responsável por uma igreja,
**quero** cadastrar minha igreja na plataforma,
**para que** eu possa utilizar o sistema para administrar membros, congregações, células, ministérios, eventos, comunicação e finanças.

---

## 4. Valor de negócio

O cadastro da igreja é a operação inicial do SaaS. Sem ele, não existe contexto organizacional para os demais módulos.

A igreja cadastrada será a raiz lógica dos dados e deverá delimitar:

* usuários;
* membros;
* congregações;
* células;
* ministérios;
* eventos;
* comunicações;
* contribuições;
* movimentações financeiras;
* configurações;
* permissões.

---

## 5. Escopo do MVP

O cadastro inicial deverá permitir informar:

### 5.1 Dados da igreja

| Campo                | Obrigatório | Descrição                                |
| -------------------- | ----------: | ---------------------------------------- |
| Nome oficial         |         Sim | Nome completo da igreja                  |
| Nome público         |         Sim | Nome utilizado nas telas e comunicações  |
| Documento            |         Não | CNPJ da igreja                           |
| E-mail institucional |         Sim | E-mail principal da igreja               |
| Telefone             |         Sim | Telefone ou WhatsApp institucional       |
| Site                 |         Não | Site oficial da igreja                   |
| Slug                 |         Sim | Identificador utilizado em URLs públicas |
| Fuso horário         |         Sim | Fuso horário padrão da igreja            |
| Status               |  Automático | Situação operacional da igreja           |

### 5.2 Endereço da sede

| Campo       | Obrigatório | Descrição                             |
| ----------- | ----------: | ------------------------------------- |
| CEP         |         Sim | CEP do endereço                       |
| Logradouro  |         Sim | Rua, avenida ou equivalente           |
| Número      |         Sim | Número do imóvel                      |
| Complemento |         Não | Sala, bloco, ponto de referência etc. |
| Bairro      |         Sim | Bairro                                |
| Cidade      |         Sim | Município                             |
| Estado      |         Sim | Unidade federativa                    |
| País        |         Sim | País da igreja                        |

### 5.3 Dados do administrador inicial

| Campo                | Obrigatório | Descrição                                   |
| -------------------- | ----------: | ------------------------------------------- |
| Nome completo        |         Sim | Nome da pessoa responsável                  |
| E-mail               |         Sim | E-mail utilizado para autenticação          |
| Telefone             |         Sim | Telefone pessoal ou profissional            |
| Senha                |         Sim | Senha inicial de acesso                     |
| Confirmação de senha |         Sim | Validação da senha informada                |
| Aceite dos termos    |         Sim | Confirmação dos termos de uso e privacidade |

---

## 6. Atores

### 6.1 Responsável pela igreja

Pessoa que realiza o cadastro inicial da igreja.

No MVP, esse usuário receberá automaticamente o papel:

```text
ADMINISTRADOR_DA_IGREJA
```

### 6.2 Sistema

Responsável por:

* validar os dados;
* verificar duplicidades;
* criar a igreja;
* criar a congregação sede;
* criar o usuário administrador;
* vincular o usuário à igreja;
* atribuir permissões;
* registrar auditoria;
* iniciar o processo de confirmação do e-mail.

---

## 7. Pré-condições

* O responsável ainda não deve possuir uma igreja ativa vinculada à mesma conta, salvo se futuramente o sistema permitir múltiplas organizações.
* O e-mail do administrador deve ser válido.
* O slug escolhido deve estar disponível.
* O usuário deve aceitar os termos de uso e a política de privacidade.
* A plataforma deve estar disponível para novos cadastros.

---

## 8. Pós-condições

Após a conclusão bem-sucedida:

1. uma igreja deverá existir no sistema;
2. uma congregação sede deverá ser criada;
3. um usuário administrador deverá existir;
4. o administrador deverá estar vinculado à igreja;
5. o administrador deverá possuir as permissões iniciais;
6. a igreja deverá possuir configurações padrão;
7. os dados deverão estar isolados dos dados de outras igrejas;
8. um registro de auditoria deverá ser criado;
9. o e-mail de confirmação ou boas-vindas deverá ser solicitado;
10. o usuário deverá poder iniciar a configuração da igreja.

---

## 9. Fluxo principal

### 9.1 Cadastro

1. O responsável acessa a página de cadastro.
2. O sistema apresenta o formulário.
3. O responsável informa os dados da igreja.
4. O responsável informa o endereço da sede.
5. O responsável informa seus dados de administrador.
6. O responsável aceita os termos de uso e a política de privacidade.
7. O responsável solicita a criação da conta.
8. O sistema valida os campos obrigatórios.
9. O sistema normaliza os dados informados.
10. O sistema verifica a disponibilidade do slug.
11. O sistema verifica duplicidade de e-mail.
12. O sistema verifica duplicidade de CNPJ, quando informado.
13. O sistema cria a igreja.
14. O sistema cria a congregação sede.
15. O sistema cria o usuário administrador.
16. O sistema vincula o administrador à igreja.
17. O sistema atribui o papel de administrador.
18. O sistema cria as configurações padrão.
19. O sistema informa que o cadastro foi realizado e que a verificação de e-mail está pendente.

---

## 10. Fluxos alternativos

### 10.1 E-mail já cadastrado

1. O sistema identifica que o e-mail já pertence a um usuário.
2. O sistema não cria um novo usuário.
3. O sistema informa que o e-mail já está cadastrado.
4. O sistema orienta o usuário a entrar na conta ou recuperar a senha.

No MVP, um usuário já cadastrado não deverá ser automaticamente associado a uma nova igreja.

---

### 10.2 Slug indisponível

1. O sistema identifica que o slug já está sendo utilizado.
2. O sistema rejeita o cadastro.
3. O sistema apresenta sugestões alternativas.

Exemplo:

```text
Slug solicitado: igreja-batista-central

Sugestões:
- igreja-batista-central-jundiai
- ib-central-jundiai
- igreja-batista-central-2
```

---

### 10.3 CNPJ já cadastrado

1. O sistema identifica que o CNPJ pertence a outra igreja.
2. O sistema rejeita o cadastro.
3. O sistema informa que já existe uma organização cadastrada com o documento.
4. O sistema poderá futuramente disponibilizar um fluxo de solicitação de acesso.

---

### 10.4 Falha ao enviar e-mail

1. A igreja e o usuário são criados normalmente.
2. A falha de comunicação é registrada.
3. O envio deverá ser tentado novamente de forma assíncrona.
4. O cadastro não deverá ser desfeito exclusivamente pela falha no envio do e-mail.

---

### 10.5 Falha durante a criação

Caso uma operação obrigatória falhe antes da conclusão:

* igreja;
* congregação sede;
* usuário;
* vínculo;
* permissões;

o sistema deverá cancelar a operação completa, evitando registros parcialmente configurados.

---

## 11. Regras de negócio

### RN-001 — Igreja como tenant

Cada igreja representa um tenant independente.

Todos os dados pertencentes à organização deverão possuir referência direta ou indireta ao identificador da igreja:

```text
church_id
```

Nenhuma consulta deverá retornar dados pertencentes a outra igreja.

---

### RN-002 — Identificador interno

A igreja deverá possuir um identificador interno imutável.

Formato recomendado:

```text
UUID
```

O identificador interno não deverá ser substituído pelo slug ou pelo CNPJ.

---

### RN-003 — Nome oficial

O nome oficial:

* deve possuir entre 3 e 150 caracteres;
* deve ser normalizado antes da persistência;
* pode se repetir entre igrejas diferentes;
* não deverá ser utilizado como chave de unicidade.

---

### RN-004 — Nome público

O nome público:

* deve possuir entre 2 e 100 caracteres;
* será exibido na interface;
* poderá ser alterado posteriormente;
* não precisa ser único.

Exemplo:

```text
Nome oficial: Igreja Batista Central de Jundiaí
Nome público: Igreja Batista Central
```

---

### RN-005 — CNPJ

O CNPJ será opcional no MVP.

Quando informado:

* deverá possuir formato válido;
* os dígitos verificadores deverão ser validados;
* deverá ser armazenado sem máscara;
* deverá ser único entre igrejas não excluídas;
* não deverá ser validado apenas pela quantidade de caracteres.

Exemplo persistido:

```text
12345678000190
```

Exemplo apresentado:

```text
12.345.678/0001-90
```

---

### RN-006 — Slug

O slug:

* deverá ser obrigatório;
* deverá ser único;
* deverá possuir entre 3 e 60 caracteres;
* deverá utilizar letras minúsculas, números e hífens;
* não poderá começar ou terminar com hífen;
* não poderá conter dois hífens consecutivos;
* deverá ser normalizado antes da validação;
* não deverá aceitar palavras reservadas.

Expressão de referência:

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

Exemplos válidos:

```text
igreja-central
ib-central-jundiai
comunidade-da-graca
```

Exemplos inválidos:

```text
Igreja Central
-igreja-central
igreja--central
igreja_central
```

Palavras reservadas iniciais:

```text
admin
api
app
auth
login
logout
cadastro
configuracoes
suporte
sistema
publico
```

---

### RN-007 — E-mail institucional

O e-mail institucional:

* deverá ser válido;
* deverá ser armazenado normalizado;
* deverá ser convertido para letras minúsculas;
* poderá ser igual ao e-mail do administrador;
* não será obrigatoriamente único entre igrejas.

---

### RN-008 — Telefone institucional

O telefone:

* deverá possuir código do país;
* deverá ser normalizado;
* deverá ser armazenado preferencialmente no padrão E.164.

Exemplo:

```text
+5511999999999
```

---

### RN-009 — Endereço da sede

Toda igreja deverá possuir uma congregação sede.

O endereço informado no cadastro da igreja será inicialmente utilizado como endereço da congregação sede.

A igreja e a congregação poderão futuramente ter endereços diferentes.

---

### RN-010 — Criação da congregação sede

Ao criar a igreja, o sistema deverá criar automaticamente uma congregação com:

```text
nome: Sede
tipo: SEDE
status: ATIVA
```

Uma igreja deverá possuir exatamente uma congregação marcada como sede principal.

---

### RN-011 — Administrador inicial

O responsável pelo cadastro será o primeiro administrador da igreja.

Esse usuário deverá receber o papel:

```text
CHURCH_ADMIN
```

O administrador inicial deverá possuir acesso administrativo aos módulos liberados para o plano da igreja.

---

### RN-012 — Senha

A senha deverá:

* possuir no mínimo 8 caracteres;
* possuir ao menos uma letra;
* possuir ao menos um número;
* não ser armazenada em texto puro;
* ser processada por algoritmo seguro de hash;
* não ser incluída em logs, eventos ou respostas da API.

Algoritmo recomendado:

```text
Argon2id
```

---

### RN-013 — Status inicial

A igreja deverá ser criada inicialmente com o status:

```text
PENDING_EMAIL_VERIFICATION
```

Após a confirmação do e-mail:

```text
ACTIVE
```

Outros estados previstos:

```text
SUSPENDED
CANCELED
ARCHIVED
```

---

### RN-014 — Configurações padrão

Na criação da igreja, o sistema deverá definir:

```text
idioma: pt-BR
moeda: BRL
fuso_horario: America/Sao_Paulo
formato_data: DD/MM/YYYY
pais: BR
```

O fuso horário poderá ser alterado pelo responsável durante ou após o cadastro.

---

### RN-015 — Atomicidade

A criação dos registros essenciais deverá ocorrer atomicamente.

São registros essenciais:

* igreja;
* congregação sede;
* usuário administrador;
* vínculo usuário-igreja;
* papel do usuário;
* configurações iniciais.

Caso qualquer etapa essencial falhe, nenhuma delas deverá permanecer efetivada.

---

### RN-016 — Auditoria

O sistema deverá registrar:

* identificador da igreja criada;
* identificador do usuário responsável;
* data e hora;
* origem da solicitação;
* endereço IP, quando disponível;
* user agent, quando disponível;
* operação executada;
* resultado da operação.

Senhas e tokens não deverão ser auditados.

---

### RN-017 — Exclusão lógica

O cadastro da igreja não deverá ser fisicamente excluído durante operações comuns.

Deverá ser utilizado um mecanismo de exclusão lógica ou arquivamento, preservando:

* histórico;
* auditoria;
* integridade referencial;
* obrigações legais e financeiras.

---

## 12. Critérios de aceitação

### Cenário 1 — Cadastro realizado com sucesso

```gherkin
Dado que o responsável acessou a página de cadastro
E informou todos os dados obrigatórios válidos
E informou um slug disponível
E informou um e-mail ainda não cadastrado
E aceitou os termos de uso e a política de privacidade
Quando solicitar a criação da igreja
Então o sistema deverá criar a igreja
E deverá criar uma congregação sede
E deverá criar o usuário administrador
E deverá vincular o administrador à igreja
E deverá atribuir o papel de administrador
E deverá criar as configurações padrão
E deverá solicitar o envio do e-mail de confirmação
E deverá informar que o cadastro foi realizado
```

### Cenário 2 — Campo obrigatório ausente

```gherkin
Dado que o responsável não informou um campo obrigatório
Quando solicitar a criação da igreja
Então o sistema não deverá criar a igreja
E deverá indicar o campo que precisa ser preenchido
```

### Cenário 3 — E-mail inválido

```gherkin
Dado que o responsável informou um e-mail com formato inválido
Quando solicitar a criação da igreja
Então o sistema não deverá criar a igreja
E deverá informar que o e-mail é inválido
```

### Cenário 4 — E-mail já cadastrado

```gherkin
Dado que já existe um usuário com o e-mail informado
Quando o responsável solicitar a criação da igreja
Então o sistema não deverá criar um novo usuário
E deverá informar que o e-mail já está cadastrado
```

### Cenário 5 — Slug indisponível

```gherkin
Dado que já existe uma igreja utilizando o slug informado
Quando o responsável solicitar a criação da igreja
Então o sistema não deverá concluir o cadastro
E deverá informar que o slug está indisponível
E deverá apresentar sugestões alternativas
```

### Cenário 6 — CNPJ inválido

```gherkin
Dado que o responsável informou um CNPJ
E o CNPJ possui dígitos verificadores inválidos
Quando solicitar a criação da igreja
Então o sistema não deverá criar a igreja
E deverá informar que o CNPJ é inválido
```

### Cenário 7 — CNPJ duplicado

```gherkin
Dado que já existe uma igreja com o CNPJ informado
Quando o responsável solicitar a criação da igreja
Então o sistema não deverá criar a igreja
E deverá informar que o documento já está cadastrado
```

### Cenário 8 — Senhas diferentes

```gherkin
Dado que a senha e a confirmação da senha são diferentes
Quando o responsável solicitar a criação da igreja
Então o sistema não deverá criar a igreja
E deverá informar que as senhas não coincidem
```

### Cenário 9 — Termos não aceitos

```gherkin
Dado que o responsável não aceitou os termos obrigatórios
Quando solicitar a criação da igreja
Então o sistema não deverá criar a igreja
E deverá informar que o aceite é necessário
```

### Cenário 10 — Falha em uma operação essencial

```gherkin
Dado que os dados informados são válidos
E ocorre uma falha durante a criação da congregação sede
Quando o sistema processar o cadastro
Então a igreja não deverá permanecer criada
E o usuário não deverá permanecer criado
E nenhum vínculo parcial deverá existir
E a falha deverá ser registrada
```

### Cenário 11 — Isolamento de tenant

```gherkin
Dado que existem duas igrejas cadastradas
E cada igreja possui seus próprios administradores
Quando um administrador consultar os dados de sua igreja
Então somente os dados da igreja à qual ele pertence deverão ser retornados
```

---

## 13. Modelo de domínio proposto

### 13.1 Agregado principal

```text
Church
```

A igreja será a raiz do agregado responsável por sua identidade e configurações institucionais.

Possíveis atributos:

```python
class Church:
    id: ChurchId
    official_name: ChurchName
    display_name: ChurchDisplayName
    document: CNPJ | None
    institutional_email: EmailAddress
    institutional_phone: PhoneNumber
    slug: ChurchSlug
    timezone: TimeZone
    status: ChurchStatus
    created_at: datetime
    updated_at: datetime
```

---

### 13.2 Entidades relacionadas

```text
Church
├── ChurchSettings
├── Congregation
├── ChurchMembership
└── Address
```

O usuário não deve necessariamente pertencer ao agregado de igreja, pois poderá futuramente possuir vínculo com mais de uma organização.

O relacionamento deverá ser representado por uma entidade associativa:

```text
ChurchMembership
```

Exemplo:

```python
class ChurchMembership:
    id: ChurchMembershipId
    church_id: ChurchId
    user_id: UserId
    role: ChurchRole
    status: MembershipStatus
    joined_at: datetime
```

---

## 14. Value Objects propostos

### `ChurchId`

Representa a identidade interna da igreja.

```python
ChurchId(UUID)
```

### `ChurchName`

Responsável pelas regras do nome oficial.

### `ChurchDisplayName`

Responsável pelas regras do nome público.

### `ChurchSlug`

Responsável por:

* normalização;
* validação de formato;
* palavras reservadas.

A verificação de unicidade deverá ocorrer no caso de uso ou por meio de um serviço de domínio, pois depende de consulta ao repositório.

### `CNPJ`

Responsável por:

* remover máscara;
* validar quantidade de dígitos;
* validar dígitos verificadores;
* produzir representação formatada.

### `EmailAddress`

Responsável por:

* normalização;
* validação de formato;
* comparação consistente.

### `PhoneNumber`

Responsável por:

* normalização;
* código do país;
* formato de persistência.

### `Address`

Representa o endereço completo.

### `TimeZone`

Representa um identificador válido de fuso horário.

Exemplo:

```text
America/Sao_Paulo
```

---

## 15. Enumerações propostas

### Status da igreja

```python
from enum import StrEnum


class ChurchStatus(StrEnum):
    PENDING_EMAIL_VERIFICATION = "pending_email_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELED = "canceled"
    ARCHIVED = "archived"
```

### Papel dentro da igreja

```python
class ChurchRole(StrEnum):
    CHURCH_ADMIN = "church_admin"
    PASTOR = "pastor"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    LEADER = "leader"
    MEMBER = "member"
```

No cadastro inicial, apenas `CHURCH_ADMIN` será atribuído automaticamente.

### Tipo de congregação

```python
class CongregationType(StrEnum):
    HEADQUARTERS = "headquarters"
    BRANCH = "branch"
```

---

## 16. Caso de uso

Nome sugerido:

```text
RegisterChurch
```

### Entrada

```python
@dataclass(frozen=True, slots=True)
class RegisterChurchInput:
    official_name: str
    display_name: str
    document: str | None
    institutional_email: str
    institutional_phone: str
    website: str | None
    slug: str
    timezone: str
    address: RegisterAddressInput
    administrator: RegisterAdministratorInput
    terms_accepted: bool
```

### Saída

```python
@dataclass(frozen=True, slots=True)
class RegisterChurchOutput:
    church_id: UUID
    congregation_id: UUID
    administrator_id: UUID
    church_status: str
    email_verification_required: bool
```

### Dependências

```python
class RegisterChurch:
    church_repository: ChurchRepository
    congregation_repository: CongregationRepository
    user_repository: UserRepository
    church_membership_repository: ChurchMembershipRepository
    password_hasher: PasswordHasher
    unit_of_work: UnitOfWork
    clock: Clock
    id_generator: IdGenerator
```

---

## 17. Pseudocódigo do caso de uso

```python
async def execute(
    self,
    input_data: RegisterChurchInput,
) -> RegisterChurchOutput:
    self._validate_terms(input_data.terms_accepted)

    email = EmailAddress(input_data.administrator.email)
    slug = ChurchSlug(input_data.slug)

    if await self._user_repository.exists_by_email(email):
        raise UserEmailAlreadyExistsError(email)

    if await self._church_repository.exists_by_slug(slug):
        raise ChurchSlugAlreadyExistsError(slug)

    document = (
        CNPJ(input_data.document)
        if input_data.document
        else None
    )

    if (
        document is not None
        and await self._church_repository.exists_by_document(document)
    ):
        raise ChurchDocumentAlreadyExistsError(document)

    church = Church.register(
        church_id=self._id_generator.generate(),
        official_name=ChurchName(input_data.official_name),
        display_name=ChurchDisplayName(input_data.display_name),
        document=document,
        institutional_email=EmailAddress(
            input_data.institutional_email
        ),
        institutional_phone=PhoneNumber(
            input_data.institutional_phone
        ),
        slug=slug,
        timezone=TimeZone(input_data.timezone),
        now=self._clock.now(),
    )

    administrator = User.register(
        user_id=self._id_generator.generate(),
        name=PersonName(input_data.administrator.name),
        email=email,
        phone=PhoneNumber(input_data.administrator.phone),
        password_hash=self._password_hasher.hash(
            input_data.administrator.password
        ),
        now=self._clock.now(),
    )

    headquarters = Congregation.create_headquarters(
        congregation_id=self._id_generator.generate(),
        church_id=church.id,
        name=CongregationName("Sede"),
        address=Address.create(input_data.address),
        now=self._clock.now(),
    )

    membership = ChurchMembership.create_administrator(
        membership_id=self._id_generator.generate(),
        church_id=church.id,
        user_id=administrator.id,
        now=self._clock.now(),
    )

    async with self._unit_of_work:
        await self._church_repository.add(church)
        await self._user_repository.add(administrator)
        await self._congregation_repository.add(headquarters)
        await self._church_membership_repository.add(membership)
        await self._unit_of_work.commit()

    return RegisterChurchOutput(
        church_id=church.id.value,
        congregation_id=headquarters.id.value,
        administrator_id=administrator.id.value,
        church_status=church.status.value,
        email_verification_required=True,
    )
```

---

## 18. Integrações assíncronas adiadas

A publicação de eventos de domínio e seus consumidores não fazem parte da implementação atual
do cadastro. O caso de uso deve concluir somente a criação transacional da estrutura inicial e
informar que a verificação de e-mail está pendente. Quando integrações assíncronas forem
introduzidas, seu contrato e sua garantia de entrega deverão ser especificados separadamente.

---

## 19. API proposta

### Endpoint

```http
POST /api/v1/churches
```

### Requisição

```json
{
  "official_name": "Igreja Batista Central de Jundiaí",
  "display_name": "Igreja Batista Central",
  "document": "12.345.678/0001-90",
  "institutional_email": "contato@igrejacentral.com.br",
  "institutional_phone": "+5511999999999",
  "website": "https://igrejacentral.com.br",
  "slug": "igreja-batista-central-jundiai",
  "timezone": "America/Sao_Paulo",
  "address": {
    "postal_code": "13200-000",
    "street": "Rua das Igrejas",
    "number": "100",
    "complement": null,
    "district": "Centro",
    "city": "Jundiaí",
    "state": "SP",
    "country": "BR"
  },
  "administrator": {
    "name": "João da Silva",
    "email": "joao@igrejacentral.com.br",
    "phone": "+5511999999999",
    "password": "SenhaSegura123",
    "password_confirmation": "SenhaSegura123"
  },
  "terms_accepted": true
}
```

### Resposta de sucesso

```http
HTTP/1.1 201 Created
```

```json
{
  "data": {
    "church_id": "0a35a4f6-e0bf-4d82-a524-6144cd45dcfd",
    "congregation_id": "bcd10414-3218-4f13-b56f-e455466569e7",
    "administrator_id": "7a6c51a2-46ce-44af-9900-67d46e46a290",
    "status": "pending_email_verification",
    "email_verification_required": true
  }
}
```

---

## 20. Erros da API

### Erro de validação

```http
HTTP/1.1 422 Unprocessable Entity
```

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Os dados informados são inválidos.",
    "fields": {
      "administrator.email": [
        "Informe um e-mail válido."
      ],
      "slug": [
        "O slug informado possui formato inválido."
      ]
    }
  }
}
```

### E-mail duplicado

```http
HTTP/1.1 409 Conflict
```

```json
{
  "error": {
    "code": "USER_EMAIL_ALREADY_EXISTS",
    "message": "Já existe uma conta cadastrada com este e-mail."
  }
}
```

### Slug duplicado

```http
HTTP/1.1 409 Conflict
```

```json
{
  "error": {
    "code": "CHURCH_SLUG_ALREADY_EXISTS",
    "message": "O endereço público escolhido já está em uso.",
    "details": {
      "suggestions": [
        "igreja-batista-central-jundiai",
        "ib-central-jundiai"
      ]
    }
  }
}
```

### CNPJ duplicado

```http
HTTP/1.1 409 Conflict
```

```json
{
  "error": {
    "code": "CHURCH_DOCUMENT_ALREADY_EXISTS",
    "message": "Já existe uma igreja cadastrada com este CNPJ."
  }
}
```

---

## 21. Persistência proposta

### Tabela `churches`

```text
id
official_name
display_name
document
institutional_email
institutional_phone
website
slug
timezone
status
created_at
updated_at
archived_at
```

Restrições:

```text
PRIMARY KEY (id)
UNIQUE (slug)
UNIQUE (document), quando document não for nulo
```

### Tabela `church_settings`

```text
church_id
locale
currency
timezone
date_format
created_at
updated_at
```

### Tabela `congregations`

```text
id
church_id
name
type
status
address_id
created_at
updated_at
archived_at
```

### Tabela `users`

```text
id
name
email
phone
password_hash
email_verified_at
status
created_at
updated_at
```

### Tabela `church_memberships`

```text
id
church_id
user_id
role
status
joined_at
created_at
updated_at
```

Restrições:

```text
UNIQUE (church_id, user_id)
```

---

## 22. Segurança

O fluxo deverá observar:

* hash seguro de senha;
* proteção contra criação automatizada de contas;
* rate limiting;
* validação de entrada no limite da aplicação;
* mensagens de erro sem exposição de dados internos;
* prevenção contra mass assignment;
* proteção contra SQL injection;
* proteção contra enumeração excessiva de usuários;
* registro de tentativas suspeitas;
* expiração dos tokens de confirmação;
* uso obrigatório de HTTPS em produção.

Uma possível política inicial de rate limiting:

```text
5 tentativas por minuto por IP
20 tentativas por hora por IP
```

A política deverá ser configurável.

---

## 23. Observabilidade

O caso de uso deverá produzir métricas como:

```text
church_registration_started_total
church_registration_completed_total
church_registration_failed_total
church_registration_duration_seconds
```

Os logs deverão possuir correlação por:

```text
request_id
correlation_id
church_id
user_id
```

A senha, confirmação de senha e tokens não deverão aparecer nos logs.

---

## 24. Testes necessários

### Testes unitários

* cria igreja com dados válidos;
* normaliza o nome;
* normaliza e-mail;
* normaliza telefone;
* valida CNPJ;
* valida slug;
* rejeita slug reservado;
* rejeita senha inválida;
* rejeita termos não aceitos;
* cria congregação sede;
* cria administrador inicial;
* atribui papel correto;

### Testes do caso de uso

* registra igreja com sucesso;
* rejeita e-mail existente;
* rejeita slug existente;
* rejeita CNPJ existente;
* garante rollback em caso de falha;
* retorna os identificadores criados.

### Testes de integração

* persiste todos os registros;
* aplica restrição única de slug;
* aplica restrição única de CNPJ;
* garante o vínculo entre usuário e igreja;
* garante isolamento entre tenants;
* confirma atomicidade da transação.

### Testes de API

* retorna `201` para cadastro válido;
* retorna `422` para dados inválidos;
* retorna `409` para duplicidades;
* não retorna hash de senha;
* não aceita campos desconhecidos sensíveis;
* respeita o rate limit.

---

## 25. Fora do escopo do MVP

Não fazem parte desta história:

* cadastro de múltiplas congregações;
* cadastro completo dos líderes;
* configuração de plano ou assinatura;
* pagamento;
* personalização visual avançada;
* domínio personalizado;
* importação de membros;
* aprovação manual da igreja pela plataforma;
* integração com Receita Federal;
* associação de um usuário existente a uma nova igreja;
* transferência de propriedade;
* recuperação de uma igreja já cadastrada;
* exclusão definitiva;
* configuração detalhada de permissões;
* cadastro de dados bancários.

Esses comportamentos deverão ser tratados em histórias separadas.

---

## 26. Definition of Done

A história será considerada concluída quando:

* as regras de negócio estiverem implementadas;
* os dados essenciais forem criados atomicamente;
* a congregação sede for criada automaticamente;
* o administrador inicial for criado e vinculado;
* o isolamento de tenant estiver garantido;
* os testes unitários estiverem implementados;
* os testes de integração estiverem implementados;
* o contrato da API estiver documentado;
* os erros de domínio estiverem mapeados para respostas HTTP;
* logs e métricas essenciais estiverem disponíveis;
* a senha não aparecer em logs ou respostas;
* o fluxo de confirmação de e-mail for disparado;
* a documentação técnica estiver atualizada.
