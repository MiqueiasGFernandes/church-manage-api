# Workflow de auditoria de segurança de código

## Sumário

1. Princípios e limites
2. Preparação e escopo
3. Inventário da superfície de ataque
4. Trilhas de análise
5. Validação de achados
6. Severidade e priorização
7. Redação do relatório
8. Exportação e Git
9. Validação final

## 1. Princípios e limites

- Tratar a auditoria como revisão orientada a ameaças, não como busca mecânica por palavras.
- Basear cada achado em código executável, configuração efetiva ou dependência realmente usada.
- Separar claramente:
  - vulnerabilidade confirmada pelo fluxo;
  - risco condicionado à topologia ou configuração;
  - melhoria de defesa em profundidade;
  - hipótese não validada, que não deve entrar como achado.
- Não fabricar CVE, CWE, CVSS, exploitabilidade ou impacto.
- Não registrar segredos, tokens, senhas, dados pessoais ou conteúdo de `.env` no relatório.
- Não executar exploração destrutiva, exfiltração, carga de negação de serviço ou ações externas.
- Usar PoCs locais e não destrutivas somente quando necessárias para confirmar comportamento.
- Não alterar código de produção em uma tarefa apenas de análise e relatório.
- Navegar na internet somente quando a solicitação incluir dependências/CVEs, versões atuais,
  advisories ou outra informação temporal; preferir fontes oficiais e bases primárias.

## 2. Preparação e escopo

1. Ler integralmente `AGENTS.md` e instruções equivalentes aplicáveis.
2. Inspecionar manifesto, lockfile, configuração de runtime, `.env.example`, containers, proxy,
   migrações, CI e documentação operacional.
3. Registrar no relatório:
   - data;
   - código e componentes analisados;
   - método utilizado;
   - itens explicitamente fora do escopo;
   - pressupostos de implantação relevantes.
4. Verificar o estado do Git e preservar alterações existentes do usuário.
5. Não ler arquivos de segredos além do necessário. Preferir exemplos versionados e nomes de
   variáveis; nunca imprimir valores sensíveis em comandos ou respostas.

Se o usuário não delimitar escopo, analisar o repositório local inteiro, priorizando componentes
expostos externamente e operações sensíveis.

## 3. Inventário da superfície de ataque

Mapear antes dos achados:

- Entradas HTTP, RPC, CLI, filas, webhooks, uploads e jobs.
- Endpoints públicos, autenticados, administrativos e internos.
- Identidades: usuário, serviço, tenant, sessão, API key e papel.
- Fronteiras: cliente/API, proxy/aplicação, aplicação/banco, aplicação/serviços externos.
- Dados sensíveis: credenciais, tokens, PII, dados financeiros, documentos e logs.
- Operações sensíveis: cadastro, login, recuperação, alteração de senha, permissões, exportação,
  exclusão, upload, cobrança e administração.
- Persistência, cache, filas, storage, e-mail e provedores externos.
- Segredos e configuração por ambiente.
- Bibliotecas/frameworks que implementam controles de segurança.

Formular ameaças por ativo e fronteira: quem controla a entrada, qual decisão de confiança ocorre e
qual propriedade precisa ser preservada.

## 4. Trilhas de análise

### 4.1 Autenticação e contas

Verificar:

- mensagens, status e timing que enumerem contas;
- armazenamento e verificação de senha;
- limites mínimo e máximo antes de hash caro;
- credential stuffing, brute force e rate limiting;
- estados bloqueado, desativado e não verificado;
- MFA, quando existente;
- recuperação e troca de credenciais;
- invalidação de tokens e sessões após eventos sensíveis;
- auditoria sem exposição de credenciais.

### 4.2 Tokens, cookies e sessões

Verificar:

- entropia, expiração, finalidade, issuer, audience e assinatura;
- armazenamento de tokens opacos somente como hash;
- rotação e detecção de reuso;
- consumo atômico de tokens de uso único;
- revogação e vínculo do token à sessão/usuário;
- flags `HttpOnly`, `Secure`, `SameSite`, `Path` e `Domain`;
- CSRF em endpoints autenticados por cookie;
- fixação, replay, concorrência e sessões órfãs;
- estabilidade e rotação de chaves.

### 4.3 Autorização e multi-tenancy

Rastrear do endpoint à query:

- autenticação antes da autorização;
- checagem explícita de tenant e pertencimento;
- IDOR/BOLA por identificadores controlados pelo cliente;
- permissões por operação, não apenas papel ou UI;
- filtros de tenant em leituras, alterações e exclusões;
- mass assignment e alteração de campos privilegiados;
- confusão entre identidade global e vínculo organizacional;
- respostas e contagens que vazem existência de recursos de outro tenant.

### 4.4 Entrada, saída e injeção

Verificar:

- SQL, shell, template, LDAP, path traversal, SSRF e desserialização;
- queries parametrizadas e allowlists;
- tamanho máximo de corpo, strings, listas, arquivos e decompression ratio;
- tipos MIME, extensões, nomes e armazenamento de uploads;
- escaping contextual em HTML, e-mail, logs e templates;
- redirecionamentos e URLs controladas;
- exposição excessiva de campos, stack traces e detalhes internos.

Não reportar injeção apenas porque há interpolação; confirmar se a entrada alcança um interpretador
sem parametrização ou validação adequada.

### 4.5 Criptografia e segredos

Verificar:

- primitivas e bibliotecas reconhecidas em vez de criptografia caseira;
- algoritmos, tamanhos, nonces, comparação constante e aleatoriedade segura;
- segredo obrigatório e de alta entropia em produção;
- segregação, armazenamento e rotação de chaves;
- ausência de segredos em código, Git, logs, URLs e mensagens de erro;
- TLS obrigatório nas fronteiras relevantes.

Comprimento mínimo não prova entropia. Defaults de desenvolvimento devem falhar de forma segura
quando executados em modo de produção.

### 4.6 Persistência, transações e concorrência

Verificar:

- constraints como última linha de defesa;
- transações cobrindo toda a operação sensível;
- TOCTOU entre leitura e alteração;
- `SELECT FOR UPDATE`, updates condicionais ou compare-and-set onde necessário;
- erros de unicidade mapeados sem `500` ou vazamento;
- rollback sem efeitos parciais;
- exclusão/cascade e retenção de auditoria;
- credenciais e hashes fora de respostas e logs.

### 4.7 Disponibilidade e abuso

Verificar:

- rate limiter distribuído, atômico, com TTL e cardinalidade limitada;
- operações caras antes de autenticação ou validações baratas;
- regex de complexidade perigosa;
- paginação e limites de consultas;
- crescimento ilimitado de memória, banco, filas e logs;
- envio de e-mail/SMS e integrações abusáveis;
- timeouts, retries, circuit breakers e backpressure;
- endpoints públicos de cadastro, busca, exportação e recuperação.

### 4.8 Configuração HTTP e implantação

Verificar:

- hosts e proxies confiáveis;
- CORS e credenciais;
- HSTS, `nosniff`, políticas de frame e referrer;
- documentação/debug em produção;
- cookies seguros e HTTPS;
- defaults de banco, e-mail, storage e chaves;
- isolamento entre workers/réplicas;
- saúde, logs e métricas sem dados sensíveis.

### 4.9 Dependências e supply chain

Executar somente se estiver no escopo ou for necessário para um risco observado:

- identificar lockfile e versões efetivas;
- usar ferramenta adequada ao ecossistema;
- consultar advisory primário e confirmar que o caminho vulnerável é usado;
- registrar versão afetada, corrigida e fonte;
- distinguir dependência direta, transitiva e falso positivo por código inalcançável.

Não afirmar vulnerabilidade apenas pela faixa ampla do manifesto quando o lockfile fixa outra versão.

## 5. Validação de achados

Para cada suspeita, responder antes de reportar:

1. Qual entrada ou capacidade o atacante controla?
2. Qual pré-condição é necessária?
3. Qual caminho completo leva ao comportamento inseguro?
4. Qual ativo ou propriedade é afetado?
5. Há controle compensatório no código, framework, banco ou proxy?
6. O impacto é reproduzível ou condicionado?
7. A correção proposta atua na causa raiz?

Registrar evidência como `caminho:linha-inicial-linha-final` e explicar o significado. Linhas podem
mudar; incluir também nomes de classe, função, endpoint ou variável.

Quando uma PoC for necessária:

- preferir teste unitário/integrado local ou script descartável em `/tmp`;
- usar dados fictícios e banco de teste;
- limitar volume e concorrência ao mínimo;
- remover instrumentação temporária;
- não incluir segredo funcional no relatório.

Excluir achados se o fluxo completo demonstrar controle suficiente. Mover recomendações sem impacto
demonstrável para defesa em profundidade e atribuir severidade baixa.

## 6. Severidade e priorização

Classificar qualitativamente, sem inventar precisão numérica:

- **Crítica:** comprometimento amplo e direto, com baixa complexidade, como RCE, bypass completo de
  autenticação, extração massiva de segredos ou cross-tenant sistêmico.
- **Alta:** impacto grave em conta, tenant, dados ou disponibilidade, explorável remotamente com
  pré-condições razoáveis.
- **Média:** impacto relevante, mas limitado, condicionado, com maior complexidade ou controles
  compensatórios parciais.
- **Baixa:** defesa em profundidade, exposição pequena ou cenário com pré-condições fortes.
- **Informativa:** observação útil sem vulnerabilidade; preferir a seção de pontos positivos ou
  limitações em vez de inflar a tabela de achados.

Considerar confidencialidade, integridade, disponibilidade, escopo multi-tenant, privilégios,
interação do usuário, detectabilidade e facilidade de repetição. Informar CWE somente quando o
mapeamento for adequado. Usar CVSS apenas se solicitado e com vetor completo justificado.

## 7. Redação do relatório

Copiar e preencher [../assets/report-template.md](../assets/report-template.md). O documento deve:

- começar com data, escopo, método e limitações;
- resumir quantidade por severidade sem contradizer a tabela;
- ordenar achados por severidade e prioridade;
- atribuir IDs estáveis `SEC-01`, `SEC-02`, ...;
- incluir em cada achado severidade, CWE quando aplicável, evidência, impacto, pré-condições e
  recomendação;
- evitar instruções ofensivas desnecessárias e dados sensíveis;
- registrar pontos positivos para contextualizar controles existentes;
- oferecer uma ordem de remediação pragmática;
- indicar validações externas ainda necessárias.

Não usar linguagem absoluta como “seguro”, “impossível” ou “totalmente protegido”. Não declarar
ausência de uma classe de vulnerabilidade sem qualificar com “no escopo analisado”.

## 8. Exportação e Git

Por padrão:

1. Criar `reports/security/`.
2. Gerar `reports/security/security-audit-AAAA-MM-DD.md`.
3. Adicionar exatamente `reports/security/` ao `.gitignore` se ainda não houver regra equivalente.
4. Confirmar com:

```bash
git check-ignore -v reports/security/security-audit-AAAA-MM-DD.md
```

5. Verificar que o relatório não aparece como untracked em `git status --short`.

Preservar padrões preexistentes do `.gitignore`. Se o usuário solicitar que o relatório seja
versionado, obedecer e não adicionar a regra de ignore.

## 9. Validação final

Antes de concluir:

- conferir contagens de severidade no resumo e na tabela;
- conferir todos os IDs, títulos e seções;
- validar caminhos e linhas citados;
- remover achados especulativos ou reclassificá-los como condicionais;
- confirmar que recomendações não enfraquecem segurança nem arquitetura;
- confirmar que o arquivo existe e está ignorado;
- revisar se algum segredo foi incluído acidentalmente;
- informar que auditoria estática não substitui pentest, SAST/DAST, revisão de infraestrutura ou
  auditoria atualizada de dependências.

Na resposta final, destacar apenas total/prioridades, caminho clicável, ignore confirmado e
limitações relevantes. Não reproduzir todo o relatório na conversa.
