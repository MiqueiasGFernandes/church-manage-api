---
name: add-github-actions-workflow
description: Cria, altera e valida workflows do GitHub Actions em `.github/workflows`, incluindo CI, testes, lint, build, release, deploy, jobs reutilizáveis, execução manual e automações de pull request. Use ao adicionar ou revisar arquivos YAML de Actions, configurar eventos, condições, matrizes, cache, artifacts, environments, permissões, secrets, concorrência ou integrações com provedores externos.
---

# Adicionar workflow do GitHub Actions

## Fluxo

1. Ler integralmente `AGENTS.md` e instruções equivalentes aplicáveis ao repositório.
2. Inspecionar `.github/workflows`, scripts, manifests, lockfiles, documentação e comandos locais.
3. Definir o evento exato, os filtros de branch/path, as condições de execução e o resultado esperado.
4. Confirmar comandos no repositório; não inventar scripts, versões, secrets, ambientes ou recursos externos.
5. Fazer a menor alteração que entregue o fluxo solicitado e preserve workflows existentes.
6. Validar sintaxe, expressões, segurança, comandos e comportamento observável.
7. Relatar arquivos alterados, gatilhos, requisitos externos, validações e riscos residuais.

## Projetar o gatilho

- Usar `push` quando qualquer commit aceito na branch deve iniciar o workflow.
- Usar `pull_request` quando o workflow depende do ciclo do PR. Para agir somente após merge, usar `types: [closed]` e exigir `github.event.pull_request.merged == true`.
- Conferir `base.ref` e `head.ref` quando a direção das branches importa.
- Usar `workflow_dispatch` somente quando execução manual agrega valor.
- Evitar eventos duplicados que executem a mesma operação para o mesmo commit.
- Definir `concurrency` para deploys, releases e operações que não podem se sobrepor; decidir conscientemente se execuções anteriores podem ser canceladas.

## Segurança

- Declarar `permissions` no menor escopo possível, preferencialmente no job que necessita delas.
- Tratar conteúdo, branches e inputs de pull requests como não confiáveis.
- Não usar `pull_request_target` com checkout ou execução de código não confiável. Se esse evento for indispensável, manter o job sem executar conteúdo controlado pelo PR.
- Nunca gravar tokens, senhas, chaves ou valores de secrets no YAML, comandos, artifacts ou logs.
- Usar GitHub Secrets para credenciais e GitHub Environments para deploys que exigem proteção ou aprovação.
- Não transmitir secrets para workflows originados de forks.
- Preferir credenciais temporárias via OIDC quando o provedor suportar; caso contrário, documentar o secret necessário.
- Fixar actions de terceiros por SHA completo. Manter o nome da versão em comentário quando isso facilitar atualizações.
- Usar interpolação de contexto em `env` quando inserir dados potencialmente não confiáveis em comandos shell, evitando composição direta no script.

## Implementação

- Nomear workflow, jobs e steps pelo resultado produzido.
- Definir `runs-on`, timeout e versões de runtime explicitamente.
- Usar o gerenciador de dependências e lockfile reais do projeto.
- Restaurar caches com chaves derivadas do sistema, runtime e lockfile; não fazer cache de secrets nem artifacts mutáveis de deploy.
- Fazer upload de artifacts somente quando forem consumidos ou úteis para diagnóstico, com retenção adequada.
- Reutilizar scripts existentes para impedir divergência entre execução local e CI.
- Separar validação de deploy. Fazer o deploy depender das verificações necessárias ou de um workflow de CI obrigatório já existente.
- Para deploy, apontar para um commit ou artifact imutável e aguardar o resultado do provedor quando a ferramenta oferecer essa opção.
- Preservar comentários que expliquem restrições não óbvias; remover comentários que apenas repetem o YAML.

## Integrações externas

Antes de escrever um deploy, confirmar na documentação oficial atual:

- método de autenticação e escopos mínimos;
- comando ou action suportada e comportamento no primeiro deploy e nos seguintes;
- nomes e formato dos secrets, variables e environments;
- forma de selecionar organização, projeto, serviço e região;
- mecanismo de health check, rollback e espera por conclusão.

Não criar, alterar ou excluir recursos remotos sem autorização explícita. É permitido preparar o workflow e indicar os valores que o usuário deve cadastrar.

## Validação

Executar, conforme aplicável:

1. `actionlint` em todos os workflows. Se não estiver instalado e Docker estiver disponível, usar a imagem oficial/de referência do projeto conscientemente.
2. Parser YAML adicional quando necessário, sem tratar YAML 1.1 como fonte definitiva para a semântica do GitHub Actions.
3. Comandos locais chamados pelo workflow: testes, lint, type checking, build e scripts.
4. Build e smoke test da imagem quando o workflow publica ou implanta container.
5. `git diff --check` e inspeção do diff final.

Não alegar que o workflow foi executado no GitHub sem uma execução real. Quando a validação completa depender de secrets, runners, environments ou serviços externos, registrar claramente essa limitação e fornecer os nomes exatos que precisam ser configurados.

## Critérios de conclusão

- O YAML é válido e está em `.github/workflows` com extensão `.yml` ou `.yaml`.
- O gatilho corresponde exatamente à solicitação e não amplia deploy ou publicação.
- Permissões, secrets e código não confiável estão isolados.
- Actions externas estão fixadas de forma verificável.
- Os comandos existem e passam localmente na medida possível.
- Pré-requisitos externos e comportamento operacional estão documentados.
