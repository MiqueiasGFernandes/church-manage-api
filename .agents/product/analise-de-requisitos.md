# Adição — Autocadastro público de membros

## Inserir na seção 5 — Gestão de membros e visitantes

### RF-MEM-011 — Link público de autocadastro — P0

O sistema deverá permitir que cada igreja disponibilize um link público para autocadastro de membros e pessoas interessadas em ingressar na comunidade.

Cada igreja deverá possuir um endereço público exclusivo, por exemplo:

```text
https://app.exemplo.com.br/cadastro/igreja-batista-central
```

A igreja poderá:

* ativar ou desativar o autocadastro;
* definir o nome ou identificador do link;
* escolher a congregação associada ao formulário;
* definir quais campos serão exibidos;
* definir quais campos serão obrigatórios;
* personalizar o texto de apresentação;
* adicionar seu logotipo;
* publicar o aviso de privacidade;
* configurar uma mensagem de confirmação;
* limitar o cadastro a membros, visitantes ou ambos.

O acesso ao formulário público não deverá exigir autenticação.

---

### RF-MEM-012 — Formulário público de autocadastro — P0

O formulário deverá permitir a coleta de dados como:

* nome completo;
* nome social, quando informado;
* data de nascimento;
* telefone;
* e-mail;
* endereço;
* estado civil;
* congregação de interesse;
* vínculo familiar;
* data aproximada de início da participação;
* situação atual na igreja;
* célula de interesse;
* ministério de interesse;
* observações;
* autorização para contato;
* aceite do aviso de privacidade.

A igreja deverá poder configurar quais dessas informações serão solicitadas.

O formulário deverá priorizar a minimização de dados, coletando somente as informações necessárias para a finalidade informada.

Campos especialmente sensíveis não deverão ser incluídos no formulário público por padrão.

---

### RF-MEM-013 — Cadastro pendente de aprovação — P0

Um autocadastro realizado pelo link público não deverá criar imediatamente um membro ativo.

O sistema deverá criar uma solicitação com o status inicial:

```text
Pendente de análise
```

A solicitação deverá permanecer separada do cadastro oficial de membros até que seja analisada por um usuário autorizado.

Os possíveis status da solicitação serão:

* pendente de análise;
* em análise;
* aguardando correção;
* aprovada;
* rejeitada;
* possível duplicidade;
* expirada;
* cancelada.

Apenas solicitações aprovadas deverão gerar ou atualizar um cadastro oficial de membro.

---

### RF-MEM-014 — Aprovação por usuários autorizados — P0

As solicitações de autocadastro poderão ser analisadas por usuários que possuam uma permissão específica.

Por padrão, os seguintes perfis poderão receber essa permissão:

* administrador da igreja;
* pastor ou liderança principal;
* secretário.

A autorização não deverá depender apenas do nome do papel, mas de uma permissão explícita, por exemplo:

```text
member:self-registration:read
member:self-registration:review
member:self-registration:approve
member:self-registration:reject
```

A igreja poderá remover ou conceder essas permissões a outros papéis personalizados.

---

### RF-MEM-015 — Escopo de aprovação por congregação — P0

A análise de um autocadastro deverá respeitar o escopo organizacional do usuário.

Exemplos:

* um secretário de uma congregação poderá analisar apenas solicitações destinadas à sua congregação;
* um pastor regional poderá analisar solicitações das congregações sob sua responsabilidade;
* um administrador geral poderá analisar solicitações de toda a igreja;
* um líder de célula não poderá aprovar autocadastros, salvo quando receber permissão explícita.

O sistema deverá impedir que um usuário aprove solicitações fora de seu escopo de acesso.

---

### RF-MEM-016 — Tela de análise do autocadastro — P0

O sistema deverá disponibilizar uma fila de solicitações pendentes.

A tela deverá permitir filtrar por:

* data da solicitação;
* nome;
* status;
* congregação;
* responsável pela análise;
* possível duplicidade;
* faixa etária;
* célula de interesse;
* ministério de interesse.

Ao abrir uma solicitação, o usuário autorizado deverá visualizar:

* dados enviados;
* data e horário do envio;
* congregação escolhida;
* origem do cadastro;
* aceite do aviso de privacidade;
* possíveis cadastros semelhantes;
* histórico de alterações;
* observações internas;
* responsável atual pela análise.

---

### RF-MEM-017 — Ações de análise — P0

Durante a análise, o usuário autorizado poderá:

* aprovar a solicitação;
* rejeitar a solicitação;
* solicitar correções;
* editar informações antes da aprovação;
* vincular a um cadastro existente;
* transferir a solicitação para outra congregação;
* atribuir a análise a outro responsável;
* adicionar uma observação interna;
* marcar a solicitação como possível duplicidade.

A rejeição deverá exigir uma justificativa interna.

A igreja poderá definir se a justificativa será ou não comunicada ao solicitante.

---

### RF-MEM-018 — Aprovação e criação do membro — P0

Ao aprovar uma solicitação, o sistema deverá:

1. validar novamente os dados;
2. verificar possíveis duplicidades;
3. permitir ajustes finais;
4. criar o cadastro oficial do membro;
5. associar o membro à igreja;
6. associar o membro à congregação selecionada;
7. registrar a origem como autocadastro público;
8. armazenar o identificador da solicitação original;
9. registrar o usuário responsável pela aprovação;
10. registrar data e horário da aprovação;
11. gerar um evento de auditoria;
12. enviar uma confirmação ao solicitante, quando houver canal válido.

O cadastro poderá ser criado inicialmente com um status configurável, como:

* em integração;
* membro pendente;
* membro ativo;
* visitante cadastrado.

A igreja deverá definir qual será o status padrão dos autocadastros aprovados.

---

### RF-MEM-019 — Vinculação com cadastro existente — P0

Quando a pessoa já possuir cadastro, o sistema deverá permitir vincular a solicitação ao registro existente.

O sistema não deverá criar automaticamente um segundo membro quando forem identificadas semelhanças relevantes.

O analisador deverá poder:

* comparar os registros;
* manter o cadastro existente;
* atualizar campos autorizados;
* ignorar campos conflitantes;
* registrar a origem das novas informações;
* concluir a solicitação sem criar duplicidade.

A operação deverá ser registrada na auditoria.

---

### RF-MEM-020 — Detecção de duplicidades no autocadastro — P0

Antes do envio e antes da aprovação, o sistema deverá verificar possíveis duplicidades utilizando, quando disponíveis:

* telefone normalizado;
* e-mail normalizado;
* documento pessoal, quando coletado;
* nome completo;
* data de nascimento;
* combinação de nome, telefone e congregação.

Quando houver possível duplicidade, o sistema deverá:

* aceitar o envio da solicitação;
* marcar a solicitação para análise;
* impedir a criação automática de um segundo registro;
* apresentar os registros semelhantes apenas aos usuários autorizados.

O formulário público não deverá revelar que determinada pessoa já está cadastrada, pois isso poderia expor dados pessoais.

---

### RF-MEM-021 — Solicitação de correção — P1

O analisador poderá devolver a solicitação para correção.

Nesse caso, o sistema deverá:

* registrar quais informações precisam ser corrigidas;
* gerar um link temporário e de uso restrito;
* enviar o link ao solicitante;
* definir uma data de expiração;
* permitir somente a edição da própria solicitação;
* registrar as alterações realizadas;
* retornar a solicitação para a fila de análise.

O link não deverá permitir acesso a outros membros ou solicitações.

---

### RF-MEM-022 — Comunicação do resultado — P0

O sistema deverá poder informar ao solicitante quando sua solicitação for:

* recebida;
* aprovada;
* rejeitada;
* devolvida para correção;
* expirada.

A comunicação poderá ocorrer por:

* e-mail;
* notificação interna, caso já exista uma conta;
* WhatsApp, em uma evolução futura.

As mensagens deverão utilizar modelos configuráveis pela igreja.

---

### RF-MEM-023 — Criação de acesso para o membro — P1

Após a aprovação, a igreja poderá convidar o membro para criar uma conta de acesso.

O sistema deverá:

* enviar um convite de uso único;
* associar a conta ao cadastro aprovado;
* definir prazo de expiração;
* impedir que o convite seja utilizado por outra pessoa;
* solicitar criação de senha;
* validar o e-mail ou telefone, quando necessário;
* atribuir o papel de membro;
* limitar o acesso aos próprios dados e funcionalidades permitidas.

A aprovação do cadastro e a criação da conta deverão ser processos independentes.

Uma pessoa poderá estar cadastrada como membro sem possuir acesso ao sistema.

---

### RF-MEM-024 — Configuração do fluxo de aprovação — P1

Cada igreja poderá configurar:

* quais perfis podem analisar solicitações;
* quais perfis podem aprovar;
* se uma única aprovação é suficiente;
* se determinadas congregações exigem aprovação pastoral;
* prazo máximo para análise;
* status inicial após aprovação;
* mensagens enviadas ao solicitante;
* campos obrigatórios;
* critérios de possível duplicidade.

Em uma evolução futura, o fluxo poderá exigir múltiplas aprovações.

Exemplo:

```text
Secretário valida os dados
→ Pastor aprova a integração
→ Sistema cria o cadastro oficial
```

---

### RF-MEM-025 — Responsável pela solicitação — P1

Uma solicitação poderá ser atribuída a um responsável.

O sistema deverá permitir:

* assumir uma solicitação;
* atribuir a outro usuário;
* visualizar solicitações sem responsável;
* visualizar solicitações sob responsabilidade do usuário;
* registrar o histórico de responsáveis;
* alertar sobre solicitações sem análise por período excessivo.

---

### RF-MEM-026 — Indicadores de autocadastro — P1

O sistema deverá apresentar indicadores como:

* solicitações recebidas;
* solicitações pendentes;
* solicitações aprovadas;
* solicitações rejeitadas;
* solicitações aguardando correção;
* tempo médio de aprovação;
* solicitações por congregação;
* taxa de aprovação;
* quantidade de possíveis duplicidades;
* origem dos novos cadastros.

Os indicadores deverão respeitar o escopo de acesso do usuário.

---

## Inserir na seção 13 — Auditoria

### RF-AUD-005 — Auditoria de autocadastros — P0

O sistema deverá registrar todas as operações relacionadas ao autocadastro, incluindo:

* envio da solicitação;
* alteração de status;
* atribuição de responsável;
* edição administrativa;
* solicitação de correção;
* aprovação;
* rejeição;
* vinculação com cadastro existente;
* criação do cadastro oficial;
* envio de convite de acesso.

O registro deverá conter:

* solicitação afetada;
* usuário responsável, quando aplicável;
* data e horário;
* ação realizada;
* status anterior;
* novo status;
* campos alterados;
* justificativa, quando exigida.

---

## Inserir na seção 14 — Privacidade e gestão de dados pessoais

### RF-PRI-007 — Privacidade no formulário público — P0

Antes do envio do autocadastro, o formulário deverá apresentar:

* identificação da igreja responsável;
* finalidade da coleta;
* informações sobre como os dados serão utilizados;
* canais de contato;
* aviso de privacidade;
* campos obrigatórios e opcionais;
* autorização para contato, quando necessária.

O aceite deverá registrar:

* versão do aviso apresentado;
* data e horário;
* origem da solicitação;
* finalidades aceitas;
* eventual autorização para comunicação.

O formulário não deverá utilizar caixas de consentimento previamente marcadas.

---

### RF-PRI-008 — Retenção de solicitações rejeitadas — P1

A igreja deverá poder definir por quanto tempo manterá solicitações:

* rejeitadas;
* canceladas;
* expiradas;
* não concluídas.

Após o prazo configurado, os dados deverão ser:

* excluídos;
* anonimizados;
* ou mantidos quando houver uma justificativa administrativa ou legal documentada.

---

## Inserir na seção 16 — Requisitos não funcionais

### RNF-031 — Segurança do formulário público

O formulário público deverá possuir mecanismos contra:

* envios automatizados;
* spam;
* força bruta;
* enumeração de membros;
* injeção de conteúdo;
* upload malicioso;
* excesso de requisições;
* reutilização indevida de links;
* criação massiva de solicitações falsas.

Deverão ser utilizados, quando aplicáveis:

* rate limiting;
* CAPTCHA adaptativo;
* validação de campos;
* normalização de telefone e e-mail;
* bloqueio temporário de origens abusivas;
* limites por dispositivo ou rede;
* análise de comportamento;
* logs de segurança.

O CAPTCHA deverá ser aplicado preferencialmente de maneira adaptativa, evitando prejudicar desnecessariamente a experiência de usuários legítimos.

---

### RNF-032 — Privacidade contra enumeração

As respostas do formulário público não deverão revelar:

* se um e-mail já pertence a um membro;
* se um telefone já está cadastrado;
* se uma pessoa específica participa da igreja;
* se existe uma solicitação anterior vinculada aos dados informados.

As mensagens deverão ser genéricas, como:

```text
Recebemos sua solicitação. Ela será analisada pela equipe responsável.
```

---

### RNF-033 — Links temporários de autocadastro

Links enviados para correção, validação ou criação de acesso deverão:

* possuir tokens criptograficamente seguros;
* ter prazo de validade;
* ser de uso único quando aplicável;
* ser armazenados de forma segura;
* ser revogáveis;
* não conter dados pessoais diretamente na URL;
* não conceder acesso além da ação específica.

---

### RNF-034 — Concorrência na aprovação

O sistema deverá impedir aprovações conflitantes quando dois usuários analisarem a mesma solicitação simultaneamente.

Deverão ser utilizados mecanismos como:

* controle de versão;
* bloqueio otimista;
* validação do status atual;
* operações transacionais.

Caso outro usuário já tenha concluído a solicitação, o segundo usuário deverá ser informado de que os dados foram atualizados.

---

### RNF-035 — Acessibilidade do formulário público

O formulário deverá:

* funcionar adequadamente em smartphones;
* permitir navegação por teclado;
* possuir labels acessíveis;
* apresentar erros próximos aos respectivos campos;
* preservar os dados após erros de validação;
* indicar claramente campos obrigatórios;
* oferecer contraste adequado;
* evitar dependência exclusiva de cores.

---

## Atualizar a seção 17 — Escopo recomendado para o MVP

Adicionar aos itens incluídos no MVP:

```text
16. Link público configurável para autocadastro de membros e visitantes.
17. Fila administrativa de análise e aprovação de autocadastros.
18. Aprovação por administradores, pastores e secretários autorizados.
19. Detecção de possíveis duplicidades antes da criação do membro.
20. Comunicação de recebimento e aprovação da solicitação.
```

---

## Inserir na seção 18 — Principais fluxos críticos do MVP

### Fluxo 6 — Autocadastro e aprovação de membro

```text
Pessoa acessa o link público da igreja
→ Visualiza o aviso de privacidade
→ Preenche seus dados
→ Sistema valida as informações
→ Sistema verifica possíveis duplicidades
→ Solicitação é criada como pendente
→ Administrador, pastor ou secretário analisa
→ Responsável aprova, rejeita ou solicita correção
→ Em caso de aprovação, o cadastro oficial é criado
→ Membro é associado à congregação
→ Sistema registra a operação na auditoria
→ Solicitante recebe a confirmação
```

### Fluxo 7 — Autocadastro com possível duplicidade

```text
Pessoa envia o formulário público
→ Sistema encontra um cadastro semelhante
→ Solicitação é marcada como possível duplicidade
→ Usuário autorizado compara os registros
→ Responsável vincula a solicitação ao membro existente
→ Dados permitidos são atualizados
→ Nenhum novo membro é criado
→ Operação é registrada na auditoria
```

### Fluxo 8 — Solicitação de correção

```text
Responsável identifica dados incompletos
→ Solicitação é devolvida para correção
→ Sistema envia um link temporário
→ Solicitante atualiza as informações
→ Solicitação retorna para a fila de análise
→ Responsável realiza uma nova avaliação
```

---

## Atualizar a seção 19 — Critérios gerais de aceite do MVP

Adicionar os seguintes critérios:

16. uma igreja conseguir publicar um link público de autocadastro;

17. uma pessoa conseguir enviar seus dados sem possuir conta no sistema;

18. o autocadastro não criar um membro ativo antes da aprovação;

19. apenas administradores, pastores, secretários ou usuários explicitamente autorizados conseguirem aprovar solicitações;

20. o aprovador visualizar apenas solicitações pertencentes ao seu escopo organizacional;

21. o sistema alertar sobre possíveis duplicidades sem expor informações no formulário público;

22. uma solicitação aprovada gerar um cadastro oficial de membro;

23. uma solicitação vinculada a um membro existente não gerar um cadastro duplicado;

24. aprovações, rejeições e alterações serem registradas na auditoria;

25. links de correção ou convite expirarem e não permitirem acesso a outros registros;

26. o solicitante receber uma confirmação genérica após o envio;

27. o formulário público funcionar adequadamente em dispositivos móveis.

---

## Atualizar a seção 20 — Ordem sugerida de implementação

Na etapa 2 — Membros, acrescentar:

* configuração do formulário público;
* link público por igreja;
* recebimento de solicitações;
* fila de aprovação;
* análise por escopo de congregação;
* detecção de duplicidades;
* aprovação, rejeição e solicitação de correção;
* conversão da solicitação em membro;
* comunicação do resultado;
* convite opcional para criação de conta.
