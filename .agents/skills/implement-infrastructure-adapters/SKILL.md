---
name: implement-infrastructure-adapters
description: Implementa ou altera adapters da camada de infraestrutura para contratos internos, incluindo repositories SQLAlchemy, Unit of Work, clientes HTTP, gateways, publishers, storage, e-mail, hashing e outros provedores externos. Use quando a tarefa exigir conectar casos de uso a banco de dados ou serviços externos, criar uma implementação concreta de uma porta, registrar o adapter no Dependency Injector, substituir adapters in-memory ou adicionar testes de integração e contrato, sem mover regras de negócio para a infraestrutura.
---

# Implementar adapters de infraestrutura

## Preparar

1. Ler integralmente o `AGENTS.md` aplicável.
2. Localizar requisitos, especificações, ADRs, modelos de domínio e testes relacionados.
3. Ler [references/workflow.md](references/workflow.md) integralmente antes de alterar código.
4. Antes de alterar arquivos versionados, confirmar o Git Flow `feature/<descricao-curta> → develop → main` definido no `AGENTS.md`.
5. Identificar a porta interna, seus consumidores, o composition root e adapters existentes.
6. Executar os testes relevantes para estabelecer o comportamento baseline.

Se a porta ainda não existir, defini-la na camada interna apropriada antes do adapter:

- colocar contratos de persistência em `application/repositories/` ou no domínio quando fizerem parte de seu vocabulário;
- colocar contratos de serviços externos e demais portas em `application/ports/`;
- usar `Protocol` e prefixar toda interface com `I`;
- expor tipos de domínio ou DTOs internos, nunca tipos do SDK, HTTP ou ORM.

## Implementar

1. Criar o adapter concreto em `infrastructure/` no módulo proprietário.
2. Manter tradução, serialização, queries, SDKs e detalhes técnicos dentro do adapter.
3. Preservar multi-tenancy, transações, idempotência, segurança e tipagem forte conforme o contrato.
4. Traduzir resultados e falhas externas para tipos e erros internos estáveis.
5. Registrar configurações, recursos e adapters no composition root com Dependency Injector.
6. Não instanciar infraestrutura em casos de uso nem acessar o container como service locator.

## Testar e validar

1. Adicionar testes de contrato e unidade para mapeamentos e traduções determinísticas.
2. Adicionar testes de integração para banco, transações, clientes e ciclo de vida de recursos.
3. Validar isolamento entre tenants em toda persistência multi-tenant.
4. Validar sucesso, ausência, conflito, rollback e falhas relevantes do provedor.
5. Executar os comandos configurados de formatação, lint, tipagem e testes.
6. Revisar o diff para impedir vazamento de tipos externos, regras de negócio no adapter ou dependências invertidas.

## Entregar

Informar adapters e registros adicionados, contratos implementados, estratégia de erros e transações, validações executadas e riscos externos remanescentes.
