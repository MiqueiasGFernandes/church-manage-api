---
name: generate-openapi-docs
description: Gera, atualiza, valida e organiza contratos OpenAPI para APIs HTTP, mantendo documentação, requisitos, casos de uso, domínio e implementação sincronizados. Use ao criar ou alterar endpoints, schemas, autenticação, erros, paginação, arquivos openapi.yaml/openapi.json, documentação Swagger/Redoc, testes de contrato ou ao revisar compatibilidade e divergências de uma API HTTP.
---

# Gerar documentação OpenAPI

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de analisar ou alterar o projeto.
2. Ler as instruções do repositório e identificar a fonte canônica do contrato HTTP.
3. Antes de alterar arquivos versionados, confirmar o Git Flow `feature/<descricao-curta> → develop → main` definido no `AGENTS.md`.
4. Inspecionar requisitos, casos de uso, modelos, rotas, schemas, autenticação e testes relacionados.
5. Aplicar o fluxo contract-first ou, para código existente, sincronizar contrato e implementação conforme o workflow.
6. Executar todas as validações relevantes indicadas pelo projeto e pelo workflow.
7. Relatar divergências, breaking changes e validações realizadas.
