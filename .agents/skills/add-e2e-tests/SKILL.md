---
name: add-e2e-tests
description: Adiciona e mantém testes end-to-end assíncronos com pytest e httpx que exercitam a aplicação FastAPI pela interface HTTP e validam regras de negócio, autorização, isolamento multi-tenant, erros, transações e fluxos críticos contra a composição real da aplicação. Use ao criar ou alterar testes E2E, testes de API ponta a ponta, cenários HTTP com AsyncClient/ASGITransport, regressões de regras de negócio observáveis pela API ou validações que exigem PostgreSQL real.
---

# Adicionar testes E2E

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de analisar ou alterar testes.
2. Ler as instruções do repositório, requisitos, regras de domínio, contrato HTTP e código do fluxo afetado.
3. Identificar a regra de negócio e descrevê-la como comportamento observável, sem acoplar o teste a classes internas.
4. Implementar o menor cenário E2E que atravesse a API com `httpx.AsyncClient`, usando a aplicação e a composição de dependências reais.
5. Usar PostgreSQL real quando o comportamento envolver persistência, constraints, transações ou isolamento por tenant.
6. Executar primeiro o teste específico e depois as validações de testes, lint, formatação e tipos aplicáveis.
7. Relatar cenários cobertos, arquivos alterados, comandos executados e riscos residuais.
