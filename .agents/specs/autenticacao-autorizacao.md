# Especificação — Autenticação e Autorização de Usuários

**Projeto:** SaaS de Gestão de Igrejas
**Módulo:** Identidade e Acesso
**Status:** Especificação inicial para o MVP
**Versão:** 1.0

---

## 1. Objetivo

Implementar um módulo centralizado de autenticação e autorização responsável por:

* identificar usuários de forma segura;
* controlar o acesso às funcionalidades do sistema;
* garantir isolamento entre diferentes igrejas;
* permitir que um mesmo usuário participe de uma ou mais igrejas;
* aplicar permissões de acordo com o papel exercido pelo usuário em cada igreja;
* permitir bloqueio, revogação e auditoria de acessos;
* fornecer uma base extensível para autenticação multifator, login social e permissões personalizadas no futuro.

O módulo deverá ser utilizado por todas as funcionalidades protegidas do SaaS, como membros, congregações, células, ministérios, eventos, comunicação, financeiro e contribuições.

---

## 2. Contexto do domínio

O sistema será uma aplicação multi-tenant, em que cada igreja representa uma organização isolada.

Um usuário representa uma identidade autenticável no sistema. A associação entre o usuário e uma igreja determina:

* a qual igreja ele possui acesso;
* seu papel dentro daquela igreja;
* seu status de acesso;
* suas permissões;
* suas congregações, ministérios ou demais contextos organizacionais.

A identidade do usuário deve ser global. Isso significa que uma mesma pessoa poderá utilizar a mesma conta para participar de mais de uma igreja.

Exemplo:

```text
Usuário: joao@email.com

Igreja A:
- Papel: Administrador

Igreja B:
- Papel: Membro
```

As permissões deverão ser avaliadas considerando simultaneamente:

```text
usuário + igreja selecionada + vínculo com a igreja + papel + permissão solicitada
```

---

## 3. Escopo do MVP

O MVP deverá contemplar:

1. cadastro inicial do usuário;
2. autenticação por e-mail e senha;
3. verificação do endereço de e-mail;
4. recuperação e redefinição de senha;
5. encerramento de sessão;
6. renovação segura da sessão;
7. criação do primeiro administrador da igreja;
8. convite de usuários;
9. associação de usuários a uma igreja;
10. seleção da igreja ativa;
11. controle de acesso baseado em papéis;
12. isolamento de dados por igreja;
13. bloqueio e desbloqueio de acessos;
14. revogação de sessões;
15. registro de eventos relevantes de segurança;
16. proteção contra tentativas excessivas de autenticação;
17. exclusão lógica ou desativação de usuários;
18. autorização baseada em permissões explícitas.

---

## 4. Fora do escopo inicial

Os seguintes recursos não fazem parte do MVP, mas a arquitetura não deve impedir sua implementação futura:

* autenticação multifator;
* autenticação por Google, Apple ou Microsoft;
* autenticação biométrica;
* Single Sign-On;
* integração com provedores corporativos via OAuth 2.0, OpenID Connect ou SAML;
* login sem senha;
* autenticação por número de telefone;
* papéis completamente personalizados por igreja;
* permissões temporárias;
* aprovação em múltiplos níveis;
* delegação temporária de acesso;
* autenticação por certificado digital;
* gerenciamento avançado de dispositivos confiáveis.

---

## 5. Atores do sistema

### 5.1 Visitante

Pessoa que ainda não está autenticada.

Pode:

* acessar páginas públicas;
* iniciar um cadastro;
* confirmar seu e-mail;
* realizar login;
* solicitar recuperação de senha;
* preencher um formulário público de autocadastro como membro.

Não pode acessar recursos internos da igreja.

### 5.2 Usuário autenticado

Pessoa que possui uma conta válida e uma sessão autenticada.

Seu acesso às funcionalidades dependerá dos vínculos que possui com igrejas e das permissões associadas a esses vínculos.

### 5.3 Proprietário da igreja

Usuário responsável pela conta principal da igreja no SaaS.

Possui o maior nível administrativo dentro da organização.

Pode, entre outras ações:

* gerenciar administradores;
* alterar configurações críticas;
* transferir a propriedade da igreja;
* visualizar e gerenciar assinaturas;
* solicitar exclusão da organização.

Deve existir apenas um proprietário ativo por igreja.

### 5.4 Administrador

Usuário com acesso amplo à administração da igreja.

Pode:

* gerenciar usuários;
* atribuir papéis permitidos;
* aprovar solicitações de cadastro;
* bloquear acessos;
* configurar módulos;
* visualizar registros administrativos.

Não pode transferir a propriedade da igreja, salvo se existir uma permissão específica futura.

### 5.5 Pastor

Usuário com acesso administrativo e ministerial.

Pode:

* consultar e gerenciar membros;
* acompanhar congregações, células e ministérios;
* aprovar cadastros;
* consultar informações financeiras quando possuir a permissão correspondente;
* gerenciar eventos e comunicações.

### 5.6 Secretário

Usuário responsável por atividades administrativas e cadastrais.

Pode:

* cadastrar e editar membros;
* aprovar solicitações de cadastro;
* gerenciar eventos e comunicações;
* consultar informações permitidas da igreja.

Não deve possuir acesso financeiro automaticamente.

### 5.7 Tesoureiro

Usuário responsável pelas funcionalidades financeiras.

Pode:

* registrar receitas e despesas;
* consultar relatórios financeiros;
* gerenciar contribuições;
* acessar informações financeiras de membros quando permitido.

Não deve possuir acesso irrestrito às demais configurações administrativas.

### 5.8 Líder

Usuário responsável por uma célula, ministério ou grupo específico.

Pode acessar somente recursos relacionados aos contextos sob sua responsabilidade.

Exemplos:

* membros de sua célula;
* participantes de seu ministério;
* eventos do grupo que lidera;
* relatórios permitidos de sua área.

### 5.9 Membro

Usuário comum vinculado a uma igreja.

Pode:

* visualizar e atualizar seus próprios dados permitidos;
* consultar eventos;
* receber comunicações;
* acompanhar suas próprias contribuições, quando essa funcionalidade estiver habilitada;
* participar de células e ministérios.

---

## 6. Conceitos principais

### 6.1 Usuário

Representa a identidade global utilizada para autenticação.

A entidade `User` não deve conter diretamente o papel do usuário em uma igreja, pois o mesmo usuário poderá exercer papéis diferentes em organizações distintas.

Atributos conceituais:

```text
User
- id
- email
- normalized_email
- password_hash
- status
- email_verified_at
- last_login_at
- password_changed_at
- created_at
- updated_at
- deactivated_at
```

### 6.2 Igreja

Representa o tenant principal do sistema.

```text
Church
- id
- name
- status
- owner_membership_id
- created_at
- updated_at
```

### 6.3 Vínculo do usuário com a igreja

A entidade `ChurchMembership` representa a associação entre um usuário e uma igreja.

Ela não representa necessariamente o cadastro ministerial completo de um membro. Seu propósito principal é controlar o acesso à organização.

```text
ChurchMembership
- id
- church_id
- user_id
- role_id
- status
- invited_by_user_id
- invited_at
- accepted_at
- approved_by_user_id
- approved_at
- blocked_by_user_id
- blocked_at
- block_reason
- created_at
- updated_at
```

### 6.4 Papel

Representa um conjunto nomeado de permissões.

```text
Role
- id
- code
- name
- description
- scope
- is_system_role
```

Exemplos de códigos:

```text
church_owner
church_admin
pastor
secretary
treasurer
leader
member
```

### 6.5 Permissão

Representa uma ação específica que pode ser executada sobre um recurso.

O padrão recomendado é:

```text
recurso:ação
```

Exemplos:

```text
members:read
members:create
members:update
members:delete
members:approve
users:invite
users:block
roles:assign
finance:read
finance:create
finance:update
finance:delete
events:manage
communications:send
church:configure
church:transfer_ownership
```

### 6.6 Sessão

Representa uma autenticação ativa do usuário.

```text
Session
- id
- user_id
- refresh_token_hash
- device_identifier
- user_agent
- ip_address
- created_at
- last_used_at
- expires_at
- revoked_at
- revocation_reason
```

---

## 7. Modelo de autenticação

### 7.1 Credencial inicial

O MVP utilizará:

```text
e-mail + senha
```

O e-mail deverá:

* ser obrigatório;
* ser único globalmente;
* ser comparado de forma normalizada;
* ser convertido para uma representação canônica antes da persistência;
* ser verificado antes que o usuário obtenha acesso completo ao sistema.

A senha nunca poderá ser armazenada em texto puro ou de forma reversível.

### 7.2 Tokens

A aplicação deverá utilizar:

* access token de curta duração;
* refresh token rotativo;
* revogação de sessões;
* armazenamento seguro do refresh token.

Recomendação inicial:

```text
Access token:
- JWT assinado
- duração aproximada: 10 a 15 minutos

Refresh token:
- valor aleatório criptograficamente seguro
- duração aproximada: 7 a 30 dias
- armazenado no servidor apenas como hash
- rotacionado a cada renovação
```

O tempo exato deverá ser configurável por ambiente.

### 7.3 Conteúdo mínimo do access token

O access token poderá conter:

```json
{
  "sub": "user-id",
  "sid": "session-id",
  "iat": 0,
  "exp": 0,
  "jti": "token-id",
  "iss": "saas-igrejas",
  "aud": "saas-igrejas-api"
}
```

O token não deverá ser utilizado como fonte definitiva das permissões do usuário.

A igreja ativa e as permissões poderão ser recuperadas do servidor ou representadas em um contexto de autorização com tempo de validade curto.

Informações sensíveis não devem ser incluídas no JWT.

### 7.4 Armazenamento no cliente

Para aplicações web, o refresh token deverá preferencialmente ser armazenado em cookie:

```text
HttpOnly
Secure
SameSite=Lax ou Strict
Path restrito ao endpoint de autenticação, quando aplicável
```

O access token poderá ser mantido apenas em memória pelo cliente.

Não é recomendado persistir tokens de acesso em `localStorage`.

---

## 8. Regras de senha

A senha deverá:

* possuir no mínimo 10 caracteres;
* aceitar frases-senha;
* permitir letras, números, símbolos e espaços;
* não exigir regras excessivamente rígidas de composição;
* ser comparada contra senhas comuns ou comprometidas, quando possível;
* não ser igual ao e-mail do usuário;
* não ser registrada em logs;
* não ser retornada por nenhuma API;
* não ser enviada novamente ao usuário por e-mail.

O sistema poderá exigir alteração de senha quando:

* houver suspeita de comprometimento;
* um administrador criar uma credencial temporária;
* uma sessão for identificada como suspeita;
* ocorrer uma redefinição administrativa.

### 8.1 Hash de senha

Deverá ser utilizado um algoritmo apropriado para senhas.

Preferência:

```text
Argon2id
```

Alternativa aceitável:

```text
bcrypt
```

Parâmetros de custo deverão ser configuráveis e revisados periodicamente.

---

## 9. Estados do usuário

O usuário poderá possuir os seguintes estados:

```text
PENDING_EMAIL_VERIFICATION
ACTIVE
BLOCKED
DEACTIVATED
```

### 9.1 PENDING_EMAIL_VERIFICATION

O usuário concluiu o cadastro, mas ainda não confirmou o endereço de e-mail.

Pode:

* realizar nova solicitação de confirmação;
* alterar o endereço de e-mail, mediante validação;
* acessar apenas funcionalidades limitadas.

### 9.2 ACTIVE

O usuário confirmou o e-mail e pode utilizar o sistema conforme seus vínculos e permissões.

### 9.3 BLOCKED

O usuário foi bloqueado globalmente por uma ação administrativa da plataforma ou por razões de segurança.

Nenhuma nova sessão poderá ser criada.

As sessões existentes deverão ser revogadas.

### 9.4 DEACTIVATED

A conta foi desativada pelo usuário ou pela plataforma.

A identidade deverá permanecer preservada conforme as políticas de auditoria, segurança e proteção de dados.

---

## 10. Estados do vínculo com a igreja

Um vínculo entre usuário e igreja poderá possuir os seguintes estados:

```text
INVITED
PENDING_APPROVAL
ACTIVE
BLOCKED
REJECTED
REVOKED
```

### 10.1 INVITED

O usuário foi convidado para a igreja, mas ainda não aceitou o convite.

### 10.2 PENDING_APPROVAL

O usuário solicitou ingresso ou realizou autocadastro e aguarda aprovação.

### 10.3 ACTIVE

O usuário possui acesso ativo à igreja.

### 10.4 BLOCKED

O acesso à igreja foi temporariamente bloqueado.

O usuário pode continuar acessando outras igrejas em que possua vínculo ativo.

### 10.5 REJECTED

A solicitação de vínculo foi recusada.

### 10.6 REVOKED

O acesso à igreja foi removido.

Esse estado deve ser utilizado quando o usuário deixou de possuir vínculo com a organização.

---

## 11. Fluxos funcionais

## 11.1 Cadastro da primeira igreja

### Pré-condição

O endereço de e-mail não deve estar associado a uma conta ativa incompatível com o fluxo.

### Fluxo principal

1. O visitante informa:

   * nome;
   * e-mail;
   * senha;
   * nome da igreja;
   * aceite dos termos aplicáveis.
2. O sistema valida os dados.
3. O sistema cria o usuário com estado `PENDING_EMAIL_VERIFICATION`.
4. O sistema cria a igreja.
5. O sistema cria o vínculo com papel `church_owner`.
6. O sistema envia um e-mail de confirmação.
7. O usuário confirma o e-mail.
8. O usuário passa para o estado `ACTIVE`.
9. O vínculo com a igreja passa para `ACTIVE`.
10. O sistema cria a primeira sessão autenticada ou direciona o usuário ao login.

### Regra de consistência

A criação do usuário, da igreja e do vínculo proprietário deverá ser atômica.

Caso qualquer uma das operações falhe, nenhuma das entidades deverá permanecer parcialmente criada.

---

## 11.2 Cadastro de usuário sem igreja

O sistema poderá permitir que um usuário crie sua identidade antes de possuir um vínculo com uma igreja.

Após confirmar o e-mail, o usuário poderá:

* aceitar um convite;
* solicitar ingresso em uma igreja;
* utilizar um link público de autocadastro;
* criar uma nova igreja, caso permitido pelo modelo de negócio.

---

## 11.3 Login

### Entrada

```text
e-mail
senha
```

### Fluxo principal

1. O usuário informa as credenciais.
2. O sistema normaliza o e-mail.
3. O sistema localiza o usuário.
4. O sistema verifica seu status.
5. O sistema valida a senha.
6. O sistema registra a tentativa bem-sucedida.
7. O sistema cria uma sessão.
8. O sistema emite access token e refresh token.
9. O sistema retorna as igrejas disponíveis ao usuário.
10. Caso exista apenas uma igreja ativa, ela poderá ser selecionada automaticamente.

### Resposta de erro

A mensagem de erro não deverá revelar se o e-mail existe.

Mensagem recomendada:

```text
E-mail ou senha inválidos.
```

---

## 11.4 Verificação de e-mail

1. O sistema gera um token aleatório de uso único.
2. O token é armazenado somente como hash.
3. O usuário recebe um link por e-mail.
4. O usuário acessa o link.
5. O sistema valida:

   * existência;
   * expiração;
   * finalidade;
   * utilização anterior.
6. O sistema marca o e-mail como verificado.
7. O token é invalidado.

O token deverá:

* possuir prazo de expiração;
* ser utilizado apenas uma vez;
* ser invalidado após alteração do e-mail;
* não conter informações sensíveis.

---

## 11.5 Reenvio de confirmação de e-mail

O usuário poderá solicitar um novo e-mail de confirmação.

O endpoint deverá possuir:

* rate limiting;
* resposta neutra;
* invalidação ou controle dos tokens anteriores;
* proteção contra enumeração de usuários.

---

## 11.6 Recuperação de senha

1. O usuário informa o e-mail.
2. O sistema retorna uma resposta neutra.
3. Caso o usuário exista e esteja apto, o sistema gera um token de redefinição.
4. O token é enviado por e-mail.
5. O usuário informa uma nova senha.
6. O sistema valida o token.
7. O sistema atualiza a senha.
8. O sistema invalida o token.
9. O sistema revoga as sessões existentes, salvo decisão explícita em contrário.
10. O sistema registra o evento de segurança.

Resposta recomendada:

```text
Caso exista uma conta associada ao e-mail informado, as instruções de recuperação serão enviadas.
```

---

## 11.7 Renovação de sessão

1. O cliente envia o refresh token.
2. O sistema calcula seu hash.
3. O sistema localiza a sessão.
4. O sistema valida:

   * expiração;
   * revogação;
   * usuário ativo;
   * integridade da cadeia de rotação.
5. O sistema invalida o refresh token anterior.
6. O sistema gera um novo access token.
7. O sistema gera um novo refresh token.
8. O sistema atualiza a sessão.

Caso um refresh token já utilizado seja apresentado novamente, o sistema deverá considerar possível reutilização indevida.

Nesse cenário, deverá:

* revogar a sessão;
* opcionalmente revogar toda a família de tokens;
* registrar o evento de segurança;
* exigir nova autenticação.

---

## 11.8 Logout

O logout deverá:

* revogar a sessão correspondente;
* invalidar o refresh token;
* remover o cookie de autenticação;
* registrar o encerramento da sessão.

O access token poderá continuar tecnicamente válido até sua expiração, razão pela qual sua duração deve ser curta.

---

## 11.9 Logout de todos os dispositivos

O usuário poderá revogar todas as suas sessões ativas.

Após a operação:

* todos os refresh tokens deverão ser invalidados;
* novos access tokens somente poderão ser obtidos por novo login;
* a sessão atual também poderá ser encerrada.

---

## 11.10 Convite de usuário

Um usuário com permissão `users:invite` poderá convidar outro usuário.

### Dados do convite

```text
e-mail
papel inicial
igreja
data de expiração
usuário responsável pelo convite
```

### Fluxo para usuário inexistente

1. O administrador informa o e-mail e o papel.
2. O sistema cria o convite.
3. O sistema envia um link.
4. O convidado cria sua conta.
5. O convidado verifica seu e-mail.
6. O convidado aceita o convite.
7. O vínculo passa para `ACTIVE`.

### Fluxo para usuário existente

1. O sistema identifica que o usuário já possui conta.
2. O sistema cria o convite sem criar outro usuário.
3. O usuário autentica-se.
4. O usuário aceita o convite.
5. O vínculo passa para `ACTIVE`.

### Regras

* não poderá existir mais de um vínculo ativo do mesmo usuário com a mesma igreja;
* um convite deverá expirar;
* um convite deverá ser de uso único;
* a aceitação deverá ocorrer com o mesmo e-mail convidado;
* um administrador não poderá atribuir um papel superior ao seu nível de delegação;
* convites antigos poderão ser revogados.

---

## 11.11 Autocadastro público de membro

A igreja poderá disponibilizar um link público para autocadastro.

### Fluxo principal

1. O visitante acessa o link da igreja.
2. O visitante informa seus dados pessoais e credenciais.
3. O sistema cria ou associa a identidade do usuário.
4. O sistema cria o cadastro de membro.
5. O sistema cria o vínculo com estado `PENDING_APPROVAL`.
6. O sistema envia a verificação de e-mail.
7. Um responsável analisa a solicitação.
8. O responsável aprova ou rejeita.
9. Caso aprovado, o vínculo passa para `ACTIVE`.
10. O papel inicial será `member`.

### Atores autorizados a aprovar

Por padrão:

* proprietário;
* administrador;
* pastor;
* secretário.

A autorização real deverá depender da permissão:

```text
members:approve
```

---

## 11.12 Seleção da igreja ativa

Após autenticar-se, o usuário poderá selecionar uma igreja entre seus vínculos ativos.

O contexto da igreja ativa deverá ser informado explicitamente nas requisições protegidas.

Alternativas possíveis:

```text
Header:
X-Church-Id: <uuid>
```

ou:

```text
URL:
POST /churches/{church_id}/members
```

A utilização do identificador da igreja na URL é recomendada para recursos pertencentes diretamente a uma igreja.

O backend nunca deverá confiar apenas no identificador informado pelo cliente.

Para cada requisição, deverá validar:

1. se o usuário está autenticado;
2. se a igreja existe;
3. se o usuário possui vínculo com a igreja;
4. se o vínculo está ativo;
5. se o usuário possui a permissão exigida;
6. se eventuais restrições de escopo são satisfeitas.

---

## 11.13 Troca de igreja ativa

O usuário poderá alternar entre igrejas sem precisar realizar novo login.

A troca de igreja não poderá conceder permissões herdadas de outra organização.

Exemplo:

```text
Na Igreja A:
- usuário é administrador.

Na Igreja B:
- usuário é membro.

Ao selecionar a Igreja B:
- o usuário deverá possuir apenas permissões de membro.
```

---

## 11.14 Bloqueio do usuário em uma igreja

Um usuário autorizado poderá bloquear o vínculo de outro usuário.

O bloqueio deverá:

* alterar o vínculo para `BLOCKED`;
* impedir novas operações naquela igreja;
* revogar ou invalidar contextos ativos relacionados à igreja;
* preservar o acesso a outras igrejas;
* registrar quem realizou o bloqueio;
* registrar data, hora e motivo.

O usuário não deverá poder bloquear:

* o proprietário da igreja;
* a si próprio, quando isso deixaria a igreja sem administrador;
* usuários com nível superior sem possuir permissão específica.

---

## 11.15 Desbloqueio

O desbloqueio deverá:

* restaurar o vínculo para `ACTIVE`;
* registrar o responsável;
* registrar a data;
* não restaurar automaticamente sessões anteriormente revogadas.

O usuário deverá realizar novo login ou obter um novo contexto de autorização.

---

## 11.16 Remoção de acesso

Ao remover um usuário de uma igreja:

* o vínculo deverá passar para `REVOKED`;
* sessões ou contextos associados deverão ser revogados;
* dados históricos não deverão ser excluídos automaticamente;
* registros criados pelo usuário deverão manter autoria;
* o usuário poderá continuar acessando outras igrejas.

---

## 11.17 Transferência de propriedade

Somente o proprietário atual poderá transferir a propriedade da igreja.

O novo proprietário deverá:

* possuir conta ativa;
* possuir vínculo ativo com a igreja;
* confirmar a operação;
* possuir e-mail verificado.

A transferência deverá ser transacional:

1. o vínculo do novo proprietário recebe o papel `church_owner`;
2. o proprietário anterior recebe o papel administrativo definido;
3. a referência de propriedade da igreja é atualizada;
4. o evento é registrado em auditoria.

Deverá ser impossível existir:

* nenhuma pessoa proprietária;
* mais de uma pessoa proprietária ativa.

---

## 12. Modelo de autorização

O sistema adotará inicialmente uma combinação de:

```text
RBAC + escopo por tenant + regras contextuais
```

### 12.1 RBAC

O RBAC, controle de acesso baseado em papéis, será utilizado para associar papéis a permissões.

Exemplo:

```text
Papel: secretary

Permissões:
- members:read
- members:create
- members:update
- members:approve
- events:read
- events:create
- events:update
- communications:send
```

### 12.2 Escopo por tenant

Toda permissão administrativa deverá ser avaliada dentro de uma igreja.

Possuir `members:update` na Igreja A não concede a mesma permissão na Igreja B.

### 12.3 Regras contextuais

Algumas autorizações dependerão de dados adicionais.

Exemplos:

* um membro pode alterar somente o próprio perfil;
* um líder pode visualizar apenas membros de sua célula;
* um tesoureiro pode consultar contribuições, mas não informações pastorais;
* um administrador não pode remover o proprietário;
* um usuário não pode aprovar seu próprio cadastro;
* um líder não pode gerenciar uma célula que não lidera.

Essas regras não deverão ser representadas apenas por papéis. Deverão existir políticas de autorização específicas.

---

## 13. Matriz inicial de permissões

A matriz abaixo representa o comportamento padrão do MVP.

| Recurso/Ação                         | Proprietário | Administrador |       Pastor | Secretário | Tesoureiro |          Líder |         Membro |
| ------------------------------------ | -----------: | ------------: | -----------: | ---------: | ---------: | -------------: | -------------: |
| Visualizar igreja                    |          Sim |           Sim |          Sim |        Sim |        Sim |            Sim |            Sim |
| Configurar igreja                    |          Sim |           Sim |          Não |        Não |        Não |            Não |            Não |
| Transferir propriedade               |          Sim |           Não |          Não |        Não |        Não |            Não |            Não |
| Convidar usuários                    |          Sim |           Sim |          Sim |        Sim |        Não |            Não |            Não |
| Bloquear usuários                    |          Sim |           Sim |          Sim |        Não |        Não |            Não |            Não |
| Atribuir papéis                      |          Sim |           Sim |     Limitado |        Não |        Não |            Não |            Não |
| Visualizar membros                   |          Sim |           Sim |          Sim |        Sim |   Limitado | Escopo próprio |            Não |
| Cadastrar membros                    |          Sim |           Sim |          Sim |        Sim |        Não | Escopo próprio |            Não |
| Editar membros                       |          Sim |           Sim |          Sim |        Sim |        Não | Escopo próprio | Próprio perfil |
| Aprovar membros                      |          Sim |           Sim |          Sim |        Sim |        Não |            Não |            Não |
| Excluir ou inativar membros          |          Sim |           Sim |          Sim |   Limitado |        Não |            Não |            Não |
| Gerenciar células                    |          Sim |           Sim |          Sim |        Sim |        Não | Escopo próprio |            Não |
| Gerenciar ministérios                |          Sim |           Sim |          Sim |        Sim |        Não | Escopo próprio |            Não |
| Gerenciar eventos                    |          Sim |           Sim |          Sim |        Sim |        Não | Escopo próprio |            Não |
| Enviar comunicações                  |          Sim |           Sim |          Sim |        Sim |        Não | Escopo próprio |            Não |
| Visualizar financeiro                |          Sim |  Configurável | Configurável |        Não |        Sim |            Não |        Próprio |
| Registrar receitas e despesas        |          Sim |  Configurável |          Não |        Não |        Sim |            Não |            Não |
| Visualizar contribuições individuais |          Sim |  Configurável | Configurável |        Não |        Sim |            Não |       Próprias |
| Gerenciar assinatura do SaaS         |          Sim |           Não |          Não |        Não |        Não |            Não |            Não |

A matriz deverá ser convertida em permissões explícitas no código, evitando verificações espalhadas por nomes de papéis.

Exemplo inadequado:

```python
if user.role == "admin":
    ...
```

Exemplo recomendado:

```python
authorization_service.require_permission(
    actor=actor,
    church_id=church_id,
    permission=Permission.MEMBERS_UPDATE,
)
```

---

## 14. Hierarquia de papéis

A existência de uma hierarquia não deve significar herança irrestrita de permissões.

A hierarquia poderá ser utilizada para controlar atribuição e administração de papéis.

Ordem administrativa inicial:

```text
church_owner
church_admin
pastor
secretary
treasurer
leader
member
```

Regras:

* proprietário pode atribuir qualquer papel, exceto criar outro proprietário sem transferência;
* administrador pode atribuir papéis abaixo do nível de administrador;
* pastor pode atribuir apenas papéis operacionais autorizados;
* secretário, tesoureiro, líder e membro não podem atribuir papéis por padrão;
* nenhuma operação deverá depender exclusivamente da posição numérica do papel;
* permissões específicas continuam sendo a fonte da decisão.

---

## 15. Políticas de autorização

A autorização deverá ser implementada por políticas centralizadas.

Exemplos:

```text
CanInviteUserPolicy
CanAssignRolePolicy
CanBlockMembershipPolicy
CanApproveMemberPolicy
CanViewFinancialRecordPolicy
CanManageCellPolicy
CanUpdateMemberPolicy
CanTransferChurchOwnershipPolicy
```

Cada política deverá considerar:

```text
ator
tenant
permissão
recurso
estado do recurso
relação entre ator e recurso
restrições de domínio
```

Exemplo conceitual:

```python
class CanUpdateMemberPolicy:
    def check(
        self,
        actor: Actor,
        church_id: ChurchId,
        member: Member,
    ) -> AuthorizationDecision:
        ...
```

A decisão deverá ser fortemente tipada.

```python
@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    allowed: bool
    reason: AuthorizationDenialReason | None
```

---

## 16. Isolamento multi-tenant

O isolamento de tenant é um requisito crítico.

Toda entidade pertencente a uma igreja deverá possuir `church_id` ou estar relacionada de forma inequívoca a uma entidade que o possua.

Exemplos:

```text
Member.church_id
Congregation.church_id
Cell.church_id
Ministry.church_id
Event.church_id
FinancialTransaction.church_id
Contribution.church_id
```

Toda consulta deverá incluir o escopo da igreja.

Exemplo inadequado:

```sql
SELECT * FROM members WHERE id = :member_id;
```

Exemplo recomendado:

```sql
SELECT *
FROM members
WHERE id = :member_id
  AND church_id = :church_id;
```

A autorização não deve acontecer somente após carregar um recurso de outro tenant.

Preferencialmente, o repositório deverá exigir o `church_id` em sua interface.

```python
class MemberRepository(Protocol):
    async def find_by_id(
        self,
        *,
        church_id: ChurchId,
        member_id: MemberId,
    ) -> Member | None:
        ...
```

O sistema não deverá aceitar repositórios com operações ambíguas como:

```python
find_by_id(member_id)
```

para entidades pertencentes a uma igreja.

---

## 17. Requisitos funcionais

### RF-AUTH-001 — Cadastro de usuário

O sistema deverá permitir o cadastro de um usuário com e-mail e senha.

### RF-AUTH-002 — E-mail único

O sistema deverá impedir a criação de múltiplos usuários com o mesmo e-mail normalizado.

### RF-AUTH-003 — Verificação de e-mail

O sistema deverá exigir a verificação do e-mail para liberar o acesso completo.

### RF-AUTH-004 — Login

O sistema deverá autenticar usuários por e-mail e senha.

### RF-AUTH-005 — Logout

O sistema deverá permitir o encerramento da sessão atual.

### RF-AUTH-006 — Logout global

O sistema deverá permitir o encerramento de todas as sessões.

### RF-AUTH-007 — Renovação

O sistema deverá permitir a renovação segura da sessão por refresh token.

### RF-AUTH-008 — Recuperação de senha

O sistema deverá permitir a redefinição de senha por token enviado ao e-mail.

### RF-AUTH-009 — Alteração de senha

O usuário autenticado deverá poder alterar sua senha após informar a senha atual.

### RF-AUTH-010 — Listagem de sessões

O usuário deverá poder visualizar suas sessões ativas.

### RF-AUTH-011 — Revogação de sessão

O usuário deverá poder revogar uma sessão específica.

### RF-AUTH-012 — Vínculo com igrejas

O sistema deverá permitir que um usuário possua vínculos com múltiplas igrejas.

### RF-AUTH-013 — Igreja ativa

O sistema deverá permitir a seleção de uma igreja ativa.

### RF-AUTH-014 — Convite

Usuários autorizados deverão poder convidar pessoas para uma igreja.

### RF-AUTH-015 — Aceitação de convite

O convidado deverá poder aceitar um convite válido.

### RF-AUTH-016 — Recusa de convite

O convidado deverá poder recusar um convite.

### RF-AUTH-017 — Aprovação

Usuários autorizados deverão poder aprovar solicitações pendentes.

### RF-AUTH-018 — Rejeição

Usuários autorizados deverão poder rejeitar solicitações pendentes.

### RF-AUTH-019 — Atribuição de papel

Usuários autorizados deverão poder atribuir papéis permitidos.

### RF-AUTH-020 — Bloqueio por igreja

Usuários autorizados deverão poder bloquear o acesso de um usuário a uma igreja específica.

### RF-AUTH-021 — Desbloqueio

Usuários autorizados deverão poder desbloquear um vínculo.

### RF-AUTH-022 — Revogação de acesso

Usuários autorizados deverão poder remover o acesso de um usuário a uma igreja.

### RF-AUTH-023 — Verificação de permissão

Toda operação protegida deverá validar a permissão correspondente.

### RF-AUTH-024 — Escopo de tenant

Toda operação protegida deverá validar o vínculo do usuário com a igreja informada.

### RF-AUTH-025 — Auditoria

O sistema deverá registrar eventos relevantes de autenticação e autorização.

---

## 18. Requisitos não funcionais

### RNF-AUTH-001 — Segurança de senha

Senhas deverão ser armazenadas utilizando algoritmo resistente a ataques de força bruta.

### RNF-AUTH-002 — Segurança de tokens

Tokens deverão possuir entropia suficiente e não poderão ser registrados em logs.

### RNF-AUTH-003 — Criptografia em trânsito

Toda comunicação deverá ocorrer por HTTPS em produção.

### RNF-AUTH-004 — Tipagem forte

Toda implementação deverá utilizar tipagem forte e completa em Python.

Não serão permitidos:

* `Any` sem justificativa;
* tipos desconhecidos;
* tipos parcialmente desconhecidos;
* dicionários genéricos em contratos de domínio;
* retornos sem tipo;
* modelos de entrada ou saída indefinidos.

### RNF-AUTH-005 — Clean Architecture

O módulo deverá seguir separação entre:

```text
domain
application
infrastructure
presentation
```

### RNF-AUTH-006 — Injeção de dependências

Os casos de uso deverão receber suas dependências explicitamente por injeção de dependências.

Nenhum caso de uso deverá instanciar diretamente:

* repositórios;
* serviços de hashing;
* geradores de tokens;
* clientes de e-mail;
* relógios;
* identificadores;
* unidades de trabalho.

### RNF-AUTH-007 — Auditabilidade

Eventos de segurança deverão ser rastreáveis e possuir data, ator e contexto.

### RNF-AUTH-008 — Desempenho

A verificação de autorização deverá adicionar baixa latência às requisições.

Permissões poderão utilizar cache de curta duração, desde que:

* o cache seja segregado por tenant;
* alterações críticas invalidem o cache;
* o cache não seja a única fonte de segurança;
* bloqueios tenham efeito rapidamente.

### RNF-AUTH-009 — Disponibilidade

Falhas no envio de e-mail não poderão gerar inconsistência nos dados principais.

### RNF-AUTH-010 — Observabilidade

O módulo deverá disponibilizar métricas de:

* tentativas de login;
* falhas de login;
* bloqueios;
* redefinições de senha;
* tokens renovados;
* reutilização suspeita de refresh token;
* falhas de autorização;
* convites enviados e aceitos.

### RNF-AUTH-011 — Privacidade

Os logs não poderão conter:

* senha;
* hash de senha;
* token completo;
* cookie de sessão;
* segredo criptográfico;
* dados pessoais desnecessários.

---

## 19. Proteções de segurança

### 19.1 Rate limiting

Deverá existir limitação de requisições em endpoints sensíveis.

Exemplos:

```text
POST /auth/login
POST /auth/register
POST /auth/forgot-password
POST /auth/reset-password
POST /auth/verify-email/resend
POST /auth/refresh
POST /churches/{church_id}/invitations
```

Os limites poderão considerar:

* endereço IP;
* e-mail normalizado;
* usuário;
* sessão;
* combinação de IP e identidade;
* fingerprint técnico, respeitando as regras de privacidade.

### 19.2 Proteção contra enumeração

Respostas de login, recuperação de senha, reenvio de confirmação e convites não deverão revelar indevidamente a existência de uma conta.

### 19.3 Proteção contra força bruta

Após sucessivas tentativas inválidas, o sistema poderá:

* aplicar atraso progressivo;
* bloquear temporariamente novas tentativas;
* exigir desafio adicional;
* notificar o usuário;
* registrar o evento.

O bloqueio automático deverá ser temporário e não deverá facilitar ataques de negação de serviço contra contas específicas.

### 19.4 CSRF

Caso a autenticação utilize cookies, endpoints mutáveis deverão possuir proteção adequada contra CSRF.

A estratégia poderá combinar:

* `SameSite`;
* token CSRF;
* validação de origem;
* restrição de CORS.

### 19.5 CORS

A API deverá aceitar requisições apenas de origens explicitamente configuradas.

Não deverá ser utilizado:

```text
Access-Control-Allow-Origin: *
```

em conjunto com credenciais.

### 19.6 Replay de token

Tokens de uso único deverão ser invalidados imediatamente após o uso.

Refresh tokens deverão utilizar rotação e detecção de reutilização.

### 19.7 Escalada de privilégio

Alterações de papéis deverão verificar:

* permissão do ator;
* papel atual do alvo;
* papel solicitado;
* regras de hierarquia;
* proibição de autoelevação;
* impossibilidade de remover o último proprietário.

---

## 20. Eventos de auditoria

Deverão ser registrados, no mínimo:

```text
USER_REGISTERED
EMAIL_VERIFICATION_REQUESTED
EMAIL_VERIFIED
LOGIN_SUCCEEDED
LOGIN_FAILED
SESSION_CREATED
SESSION_REFRESHED
SESSION_REVOKED
ALL_SESSIONS_REVOKED
PASSWORD_CHANGE_SUCCEEDED
PASSWORD_RESET_REQUESTED
PASSWORD_RESET_SUCCEEDED
PASSWORD_RESET_FAILED
INVITATION_CREATED
INVITATION_ACCEPTED
INVITATION_REVOKED
CHURCH_MEMBERSHIP_APPROVED
CHURCH_MEMBERSHIP_REJECTED
CHURCH_MEMBERSHIP_BLOCKED
CHURCH_MEMBERSHIP_UNBLOCKED
CHURCH_MEMBERSHIP_REVOKED
ROLE_ASSIGNED
ROLE_REMOVED
AUTHORIZATION_DENIED
CHURCH_OWNERSHIP_TRANSFERRED
SUSPICIOUS_REFRESH_TOKEN_REUSE
```

Cada evento deverá possuir, conforme aplicável:

```text
event_id
event_type
occurred_at
actor_user_id
target_user_id
church_id
session_id
ip_address
user_agent
correlation_id
metadata sanitizada
```

Os registros de auditoria não deverão ser editáveis por usuários comuns.

---

## 21. Modelo de dados inicial

### 21.1 Tabela `users`

```text
id UUID PK
email VARCHAR NOT NULL
normalized_email VARCHAR NOT NULL UNIQUE
password_hash VARCHAR NOT NULL
status VARCHAR NOT NULL
email_verified_at TIMESTAMP NULL
last_login_at TIMESTAMP NULL
password_changed_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
deactivated_at TIMESTAMP NULL
```

### 21.2 Tabela `church_memberships`

```text
id UUID PK
church_id UUID NOT NULL FK
user_id UUID NOT NULL FK
role_id UUID NOT NULL FK
status VARCHAR NOT NULL
invited_by_user_id UUID NULL FK
invited_at TIMESTAMP NULL
accepted_at TIMESTAMP NULL
approved_by_user_id UUID NULL FK
approved_at TIMESTAMP NULL
blocked_by_user_id UUID NULL FK
blocked_at TIMESTAMP NULL
block_reason VARCHAR NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL

UNIQUE(church_id, user_id)
```

### 21.3 Tabela `roles`

```text
id UUID PK
code VARCHAR NOT NULL UNIQUE
name VARCHAR NOT NULL
description VARCHAR NULL
scope VARCHAR NOT NULL
is_system_role BOOLEAN NOT NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

### 21.4 Tabela `permissions`

```text
id UUID PK
code VARCHAR NOT NULL UNIQUE
resource VARCHAR NOT NULL
action VARCHAR NOT NULL
description VARCHAR NULL
```

### 21.5 Tabela `role_permissions`

```text
role_id UUID NOT NULL FK
permission_id UUID NOT NULL FK

PRIMARY KEY(role_id, permission_id)
```

### 21.6 Tabela `sessions`

```text
id UUID PK
user_id UUID NOT NULL FK
refresh_token_hash VARCHAR NOT NULL UNIQUE
token_family_id UUID NOT NULL
device_identifier VARCHAR NULL
user_agent VARCHAR NULL
ip_address VARCHAR NULL
created_at TIMESTAMP NOT NULL
last_used_at TIMESTAMP NOT NULL
expires_at TIMESTAMP NOT NULL
revoked_at TIMESTAMP NULL
revocation_reason VARCHAR NULL
```

### 21.7 Tabela `email_verification_tokens`

```text
id UUID PK
user_id UUID NOT NULL FK
token_hash VARCHAR NOT NULL UNIQUE
expires_at TIMESTAMP NOT NULL
used_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
```

### 21.8 Tabela `password_reset_tokens`

```text
id UUID PK
user_id UUID NOT NULL FK
token_hash VARCHAR NOT NULL UNIQUE
expires_at TIMESTAMP NOT NULL
used_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
```

### 21.9 Tabela `church_invitations`

```text
id UUID PK
church_id UUID NOT NULL FK
email VARCHAR NOT NULL
normalized_email VARCHAR NOT NULL
role_id UUID NOT NULL FK
token_hash VARCHAR NOT NULL UNIQUE
status VARCHAR NOT NULL
invited_by_user_id UUID NOT NULL FK
expires_at TIMESTAMP NOT NULL
accepted_by_user_id UUID NULL FK
accepted_at TIMESTAMP NULL
revoked_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
```

### 21.10 Tabela `security_audit_events`

```text
id UUID PK
event_type VARCHAR NOT NULL
actor_user_id UUID NULL
target_user_id UUID NULL
church_id UUID NULL
session_id UUID NULL
ip_address VARCHAR NULL
user_agent VARCHAR NULL
correlation_id VARCHAR NOT NULL
metadata JSONB NULL
occurred_at TIMESTAMP NOT NULL
```

---

## 22. Value Objects

O domínio deverá utilizar Value Objects para evitar o uso indiscriminado de tipos primitivos.

Exemplos:

```text
UserId
ChurchId
MembershipId
RoleId
PermissionCode
EmailAddress
NormalizedEmail
PasswordHash
RawPassword
SessionId
RefreshToken
TokenHash
IpAddress
UserAgent
```

Exemplo:

```python
@dataclass(frozen=True, slots=True)
class PermissionCode:
    value: str

    def __post_init__(self) -> None:
        resource, separator, action = self.value.partition(":")

        if not separator or not resource or not action:
            raise InvalidPermissionCodeError(self.value)
```

A senha em texto puro deverá existir apenas como valor transitório na camada de entrada e durante a validação pelo serviço de hash.

---

## 23. Serviços de domínio e aplicação

Interfaces recomendadas:

```python
class PasswordHasher(Protocol):
    def hash(self, password: RawPassword) -> PasswordHash:
        ...

    def verify(
        self,
        password: RawPassword,
        password_hash: PasswordHash,
    ) -> bool:
        ...


class TokenGenerator(Protocol):
    def generate(self) -> PlainToken:
        ...


class TokenHasher(Protocol):
    def hash(self, token: PlainToken) -> TokenHash:
        ...


class AccessTokenIssuer(Protocol):
    def issue(
        self,
        *,
        user_id: UserId,
        session_id: SessionId,
        issued_at: datetime,
        expires_at: datetime,
    ) -> AccessToken:
        ...


class AuthorizationService(Protocol):
    async def authorize(
        self,
        *,
        actor: Actor,
        church_id: ChurchId,
        permission: PermissionCode,
        resource: AuthorizableResource | None = None,
    ) -> AuthorizationDecision:
        ...
```

Outras dependências:

```text
UserRepository
ChurchRepository
ChurchMembershipRepository
RoleRepository
PermissionRepository
SessionRepository
InvitationRepository
PasswordResetTokenRepository
EmailVerificationTokenRepository
SecurityAuditRepository
EmailSender
Clock
IdGenerator
UnitOfWork
```

---

## 24. Casos de uso

Casos de uso iniciais:

```text
RegisterUser
RegisterChurchOwner
VerifyEmail
ResendEmailVerification
AuthenticateUser
RefreshSession
LogoutSession
LogoutAllSessions
ListUserSessions
RevokeUserSession
RequestPasswordReset
ResetPassword
ChangePassword
ListUserChurches
CreateChurchInvitation
AcceptChurchInvitation
RejectChurchInvitation
RevokeChurchInvitation
ApproveChurchMembership
RejectChurchMembership
BlockChurchMembership
UnblockChurchMembership
RevokeChurchMembership
AssignMembershipRole
TransferChurchOwnership
GetCurrentUser
GetAuthorizationContext
```

Cada caso de uso deverá:

* possuir entrada e saída fortemente tipadas;
* realizar uma única intenção de aplicação;
* depender de abstrações;
* controlar a transação por meio de `UnitOfWork`;
* produzir eventos de auditoria;
* não conhecer detalhes de HTTP;
* não retornar entidades de ORM diretamente.

---

## 25. APIs propostas

## 25.1 Autenticação

```http
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
POST /auth/logout-all
GET  /auth/me
POST /auth/change-password
POST /auth/forgot-password
POST /auth/reset-password
POST /auth/verify-email
POST /auth/verify-email/resend
GET  /auth/sessions
DELETE /auth/sessions/{session_id}
```

## 25.2 Igrejas do usuário

```http
GET /me/churches
GET /churches/{church_id}/me
```

## 25.3 Convites

```http
POST   /churches/{church_id}/invitations
GET    /churches/{church_id}/invitations
DELETE /churches/{church_id}/invitations/{invitation_id}
POST   /invitations/{token}/accept
POST   /invitations/{token}/reject
```

## 25.4 Gerenciamento de acessos

```http
GET  /churches/{church_id}/users
GET  /churches/{church_id}/users/{user_id}
POST /churches/{church_id}/users/{user_id}/approve
POST /churches/{church_id}/users/{user_id}/reject
POST /churches/{church_id}/users/{user_id}/block
POST /churches/{church_id}/users/{user_id}/unblock
POST /churches/{church_id}/users/{user_id}/revoke
PUT  /churches/{church_id}/users/{user_id}/role
```

## 25.5 Propriedade

```http
POST /churches/{church_id}/ownership-transfer
```

---

## 26. Respostas de erro

Erros deverão possuir estrutura consistente.

Exemplo:

```json
{
  "type": "https://api.saasigrejas.com/problems/invalid-credentials",
  "title": "Credenciais inválidas",
  "status": 401,
  "detail": "E-mail ou senha inválidos.",
  "code": "AUTH_INVALID_CREDENTIALS",
  "correlationId": "01J..."
}
```

Códigos iniciais:

```text
AUTH_INVALID_CREDENTIALS
AUTH_EMAIL_NOT_VERIFIED
AUTH_USER_BLOCKED
AUTH_USER_DEACTIVATED
AUTH_ACCESS_TOKEN_EXPIRED
AUTH_REFRESH_TOKEN_INVALID
AUTH_SESSION_REVOKED
AUTH_PERMISSION_DENIED
AUTH_CHURCH_ACCESS_DENIED
AUTH_MEMBERSHIP_NOT_ACTIVE
AUTH_INVITATION_INVALID
AUTH_INVITATION_EXPIRED
AUTH_INVITATION_ALREADY_USED
AUTH_ROLE_ASSIGNMENT_DENIED
AUTH_LAST_OWNER_REQUIRED
AUTH_PASSWORD_RESET_TOKEN_INVALID
AUTH_EMAIL_VERIFICATION_TOKEN_INVALID
AUTH_RATE_LIMIT_EXCEEDED
```

### Códigos HTTP esperados

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
429 Too Many Requests
```

Para evitar vazamento entre tenants, certos recursos inexistentes ou inacessíveis poderão retornar `404`, em vez de confirmar que o recurso existe em outra igreja.

---

## 27. Estrutura arquitetural sugerida

```text
src/
├── domain/
│   └── identity_access/
│       ├── entities/
│       ├── value_objects/
│       ├── enums/
│       ├── policies/
│       ├── services/
│       ├── events/
│       └── exceptions/
├── application/
│   └── identity_access/
│       ├── use_cases/
│       ├── commands/
│       ├── queries/
│       ├── dto/
│       ├── ports/
│       └── mappers/
├── infrastructure/
│   └── identity_access/
│       ├── persistence/
│       ├── security/
│       ├── tokens/
│       ├── email/
│       └── repositories/
└── presentation/
    └── http/
        ├── routes/
        ├── schemas/
        ├── dependencies/
        ├── middleware/
        └── exception_handlers/
```

A autorização transversal poderá possuir componentes compartilhados, desde que as regras de negócio permaneçam no domínio ou na aplicação.

---

## 28. Middleware e dependências HTTP

A camada HTTP poderá possuir componentes como:

```text
AuthenticationMiddleware
CurrentActorResolver
ChurchContextResolver
RequirePermissionDependency
CorrelationIdMiddleware
RateLimitMiddleware
SecurityHeadersMiddleware
```

Responsabilidades:

### `AuthenticationMiddleware`

* extrair o access token;
* validar assinatura e claims obrigatórias;
* criar a identidade autenticada básica;
* não executar regras de negócio específicas.

### `ChurchContextResolver`

* identificar a igreja da rota;
* validar o formato do identificador;
* disponibilizar o contexto ao endpoint.

### `RequirePermissionDependency`

* solicitar ao serviço de autorização a decisão;
* converter negação em erro HTTP apropriado;
* não implementar regras diretamente.

---

## 29. Estratégia de testes

O desenvolvimento deverá seguir TDD.

### 29.1 Testes unitários de domínio

Testar:

* normalização de e-mail;
* validação de senha;
* transições de estado;
* regras de vínculo;
* atribuição de papéis;
* políticas de autorização;
* transferência de propriedade;
* bloqueio do último administrador;
* reutilização de token;
* expiração.

### 29.2 Testes unitários de casos de uso

Testar:

* dependências simuladas;
* persistência esperada;
* eventos de auditoria;
* rollback em falhas;
* respostas de sucesso e erro;
* autorização negada;
* isolamento de tenant.

### 29.3 Testes de integração

Testar:

* repositórios;
* constraints;
* índices;
* transações;
* hash de senha;
* geração e validação de tokens;
* rotação de refresh token;
* persistência de auditoria.

### 29.4 Testes E2E

Cenários obrigatórios:

1. cadastro, verificação e login;
2. login com senha inválida;
3. recuperação e redefinição de senha;
4. renovação de sessão;
5. reutilização de refresh token;
6. logout;
7. convite de usuário inexistente;
8. convite de usuário existente;
9. autocadastro com aprovação;
10. acesso a uma igreja sem vínculo;
11. tentativa de acesso entre tenants;
12. tentativa de atribuir papel superior;
13. bloqueio de vínculo;
14. revogação de acesso;
15. transferência de propriedade;
16. tentativa de remover o último proprietário;
17. acesso de membro ao próprio perfil;
18. tentativa de membro acessar dados administrativos;
19. acesso de líder fora do seu escopo;
20. proteção de endpoints por rate limit.

---

## 30. Critérios de aceite

### CA-AUTH-001

Dado que um visitante informou dados válidos, quando concluir o cadastro, então o sistema deverá criar uma conta pendente de verificação e enviar um e-mail de confirmação.

### CA-AUTH-002

Dado que um usuário não verificou seu e-mail, quando tentar acessar uma funcionalidade restrita, então o sistema deverá negar o acesso.

### CA-AUTH-003

Dado que um usuário informou credenciais válidas, quando realizar login, então o sistema deverá criar uma sessão e emitir tokens válidos.

### CA-AUTH-004

Dado que um usuário informou uma senha inválida, quando realizar login, então o sistema deverá retornar uma mensagem neutra sem confirmar a existência do e-mail.

### CA-AUTH-005

Dado que o access token expirou e o refresh token é válido, quando solicitar renovação, então o sistema deverá emitir um novo par de tokens e invalidar o refresh token anterior.

### CA-AUTH-006

Dado que um refresh token já utilizado foi reapresentado, quando o sistema detectar sua reutilização, então deverá revogar a sessão e registrar um evento de segurança.

### CA-AUTH-007

Dado que um usuário possui papel administrativo apenas na Igreja A, quando tentar realizar uma ação administrativa na Igreja B, então o acesso deverá ser negado.

### CA-AUTH-008

Dado que um membro possui apenas permissão de edição do próprio perfil, quando tentar editar outro membro, então o sistema deverá negar a operação.

### CA-AUTH-009

Dado que um usuário autorizado convidou uma pessoa, quando o convite for aceito dentro do prazo, então um vínculo ativo deverá ser criado com o papel definido.

### CA-AUTH-010

Dado que uma solicitação de autocadastro está pendente, quando um usuário com `members:approve` aprová-la, então o vínculo deverá passar para `ACTIVE`.

### CA-AUTH-011

Dado que um usuário está bloqueado em uma igreja, quando tentar acessar recursos dessa igreja, então o sistema deverá negar o acesso, preservando acessos válidos em outras igrejas.

### CA-AUTH-012

Dado que um usuário não possui a permissão necessária, quando tentar executar a operação, então o sistema deverá retornar uma resposta de autorização negada e registrar o evento.

### CA-AUTH-013

Dado que um identificador de recurso pertence a outra igreja, quando o usuário tentar acessá-lo, então o sistema não deverá retornar dados nem confirmar sua existência.

### CA-AUTH-014

Dado que o proprietário deseja transferir a propriedade, quando informar um usuário elegível e confirmar a operação, então deverá existir exatamente um proprietário ativo após a transação.

### CA-AUTH-015

Dado que qualquer parte da transferência de propriedade falhou, então nenhuma alteração parcial deverá permanecer persistida.

---

## 31. Índices e constraints recomendados

```text
UNIQUE users(normalized_email)
UNIQUE church_memberships(church_id, user_id)
UNIQUE roles(code)
UNIQUE permissions(code)
UNIQUE role_permissions(role_id, permission_id)
UNIQUE sessions(refresh_token_hash)
UNIQUE email_verification_tokens(token_hash)
UNIQUE password_reset_tokens(token_hash)
UNIQUE church_invitations(token_hash)
```

Índices adicionais:

```text
church_memberships(user_id, status)
church_memberships(church_id, status)
sessions(user_id, revoked_at, expires_at)
church_invitations(church_id, normalized_email, status)
security_audit_events(church_id, occurred_at)
security_audit_events(actor_user_id, occurred_at)
security_audit_events(event_type, occurred_at)
```

A garantia de um único proprietário por igreja deverá ser implementada com constraint adequada, índice parcial ou mecanismo transacional compatível com o banco escolhido.

---

## 32. Decisões arquiteturais

### 32.1 Identidade global

A identidade do usuário será global, enquanto papéis e permissões serão vinculados à igreja.

### 32.2 Papel fora da entidade `User`

A entidade `User` não possuirá um campo global `role`.

O papel ficará em `ChurchMembership`.

### 32.3 Permissões explícitas

Os endpoints dependerão de permissões explícitas, e não de comparações diretas com nomes de papel.

### 32.4 JWT de curta duração

O access token será curto e não representará sozinho a fonte definitiva de autorização.

### 32.5 Refresh token opaco

O refresh token será opaco, rotativo e armazenado como hash.

### 32.6 Isolamento obrigatório por repositório

Repositórios de entidades pertencentes a igrejas deverão exigir `church_id`.

### 32.7 Auditoria como requisito de negócio

Eventos administrativos e de segurança deverão ser persistidos como parte da mesma transação quando necessário.

### 32.8 Autorização negada por padrão

Na ausência de uma permissão explícita ou política aplicável, o acesso deverá ser negado.

```text
Default deny
```

---

## 33. Dependências entre módulos

O módulo de autenticação e autorização dependerá conceitualmente de:

```text
Igrejas
Notificações por e-mail
Auditoria
Configuração da aplicação
Persistência
Observabilidade
```

Outros módulos dependerão dele:

```text
Membros
Congregações
Células
Ministérios
Eventos
Comunicação
Financeiro
Contribuições
Assinaturas
Configurações
```

A dependência deverá ocorrer por contratos estáveis, como:

```text
CurrentActor
AuthorizationService
PermissionCode
ChurchContext
```

Os demais módulos não deverão conhecer:

* detalhes do JWT;
* formato do refresh token;
* implementação do hash de senha;
* estrutura interna das sessões.

---

## 34. Sequência recomendada de implementação

### Etapa 1 — Fundamentos de identidade

* entidade `User`;
* Value Object `EmailAddress`;
* Value Object `PasswordHash`;
* serviço de hashing;
* cadastro;
* verificação de e-mail.

### Etapa 2 — Sessões

* login;
* access token;
* refresh token;
* rotação;
* logout;
* revogação.

### Etapa 3 — Multi-tenancy

* `ChurchMembership`;
* listagem de igrejas;
* seleção de igreja;
* validação de vínculo;
* isolamento por repositório.

### Etapa 4 — Autorização

* papéis;
* permissões;
* associação papel-permissão;
* serviço de autorização;
* dependências HTTP;
* políticas contextuais.

### Etapa 5 — Administração de acessos

* convites;
* aprovação;
* bloqueio;
* revogação;
* alteração de papel;
* transferência de propriedade.

### Etapa 6 — Segurança e observabilidade

* auditoria;
* rate limiting;
* métricas;
* alertas;
* detecção de reutilização de refresh token;
* revisão de logs e dados sensíveis.

---

## 35. Definition of Done

Uma funcionalidade deste módulo somente será considerada concluída quando:

* possuir regras de domínio implementadas;
* possuir entrada e saída fortemente tipadas;
* não possuir tipos desconhecidos ou parcialmente desconhecidos;
* possuir testes unitários;
* possuir testes de integração quando houver infraestrutura;
* possuir testes E2E para fluxos críticos;
* validar isolamento de tenant;
* validar autorização;
* registrar eventos de auditoria aplicáveis;
* não expor segredos nos logs;
* possuir documentação OpenAPI;
* possuir tratamento padronizado de erros;
* respeitar a Clean Architecture;
* utilizar injeção de dependências;
* passar pelas ferramentas de lint, tipagem e testes;
* possuir migrations de banco de dados;
* preservar compatibilidade com as políticas de segurança definidas nesta especificação.
