---
name: add-feature
description: Implementa funcionalidades de ponta a ponta com Clean Architecture, Clean Code, DRY, SOLID, tipagem forte e TDD. Use ao criar ou alterar casos de uso, regras de negócio, entidades, value objects, endpoints, persistência, integrações ou histórias de usuário neste produto, especialmente quando a tarefa atravessa domínio, aplicação, infraestrutura e apresentação.
---

# Adicionar feature

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de analisar ou alterar o projeto.
2. Ler as instruções do repositório, requisitos, especificações, ADRs e regras de domínio aplicáveis.
3. Antes de alterar arquivos versionados, confirmar o Git Flow `feature/<descricao-curta> → develop → main` definido no `AGENTS.md`.
4. Identificar o módulo afetado, os padrões existentes e a menor alteração que atende aos critérios de aceite.
5. Seguir o fluxo incremental e orientado a testes definido no workflow, mantendo as dependências apontadas para dentro.
6. Executar testes, lint, formatação e verificação de tipos relevantes.
7. Relatar arquivos alterados, decisões, validações e qualquer risco residual.
