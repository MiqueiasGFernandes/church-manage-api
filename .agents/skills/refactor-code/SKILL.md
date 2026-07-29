---
name: refactor-code
description: Refatora código existente para alinhá-lo às regras arquiteturais e de qualidade do projeto, preservando comportamento. Use ao corrigir violações de Clean Architecture, dependências entre camadas, responsabilidades indevidas, acoplamento, duplicação, tipagem, injeção de dependências, testabilidade, organização modular ou padrões definidos no AGENTS.md.
---

# Refatorar código

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de analisar ou alterar código.
2. Ler integralmente o AGENTS.md aplicável e consultar ADRs, requisitos e testes relacionados.
3. Antes de alterar arquivos versionados, confirmar o Git Flow `feature/<descricao-curta> → develop → main` definido no `AGENTS.md`.
4. Caracterizar e proteger o comportamento atual com testes antes de alterar a estrutura.
5. Aplicar mudanças pequenas e incrementais segundo o workflow, sem expandir o escopo funcional.
6. Executar testes, lint, formatação e verificação de tipos relevantes.
7. Relatar comportamento preservado, melhorias estruturais, validações e riscos residuais.
