# Workflow de repositories e integrações externas

## Sumário

1. Limites arquiteturais
2. Implementação de repositories
3. Implementação de integrações externas
4. Injeção de dependências
5. Estratégia de testes
6. Checklist de conclusão

## 1. Limites arquiteturais

Tratar todo componente de infraestrutura como adapter de uma porta definida em camada interna. Fazer a dependência apontar da infraestrutura para aplicação ou domínio.

Manter fora de domínio e aplicação:

- SQLAlchemy, sessões, statements e modelos ORM;
- clientes HTTP, códigos de status, headers e payloads de provedores;
- SDKs, filas, storage e bibliotecas específicas de fornecedor;
- configuração de conexão, credenciais, retries e timeouts;
- serialização técnica e observabilidade do adapter.

Não colocar regras de negócio no adapter. Implementar somente persistência, comunicação, tradução e garantias técnicas exigidas pela porta.

Usar nomes concretos que revelem a tecnologia ou estratégia, como `SqlAlchemyMemberRepository`, `HttpEmailGateway`, `S3ObjectStorage` ou `InMemoryEventPublisher`. Reservar o prefixo `I` às interfaces.

## 2. Implementação de repositories

### Contrato

Definir uma interface específica para o agregado ou conceito persistido. Evitar repositories CRUD genéricos e não expor `AsyncSession`, modelos ORM, expressões SQL ou paginação específica do banco.

Receber e retornar entidades, value objects e DTOs internos tipados. Representar ausência com `T | None` apenas quando ela fizer parte do contrato.

### SQLAlchemy

Usar APIs SQLAlchemy 2.x assíncronas e tipadas. Separar modelos ORM de entidades de domínio e centralizar conversões em mappers determinísticos quando a conversão não for trivial.

Não executar `commit` dentro do repository quando o caso de uso depender de atomicidade entre operações. Delegar o limite transacional ao `IUnitOfWork`; permitir `flush` apenas quando necessário para cumprir o contrato e sem encerrar a transação.

Tratar violações previsíveis de constraints no limite da infraestrutura e traduzi-las para erros internos estáveis quando o contrato exigir. Não expor mensagens, SQL ou classes de exceção do driver.

### Multi-tenancy

Incluir `church_id` em toda leitura, atualização e exclusão de dados pertencentes a uma igreja. Obter o tenant de um parâmetro interno confiável e nunca inferi-lo apenas do identificador do recurso.

Adicionar testes que criem dados para pelo menos dois tenants e comprovem que um tenant não lê nem altera dados do outro. Considerar constraints e índices compostos quando unicidade ou busca dependerem do tenant.

### Unit of Work

Implementar entrada e saída assíncronas, commit e rollback conforme a interface interna. Garantir rollback em exceções e também quando o escopo termina sem commit, se essa for a semântica definida pelo projeto.

Não misturar sessões síncronas e assíncronas. Vincular repositories participantes à mesma sessão durante uma unidade transacional.

## 3. Implementação de integrações externas

### Fronteira tipada

Receber DTOs ou value objects internos e retornar resultados internos. Tratar respostas sem tipo como `object` e validá-las imediatamente com Pydantic, `TypedDict`, dataclass ou wrapper tipado.

Não propagar para a aplicação:

- modelos ou exceções do SDK;
- estruturas JSON sem contrato;
- códigos HTTP e detalhes do protocolo;
- identificadores ou estados externos sem tradução explícita.

### Configuração e segurança

Receber endpoint, credenciais, timeouts e demais configurações pelo construtor. Carregar segredos de configuração externa e nunca registrá-los em logs ou persistir payloads sensíveis sem necessidade.

Definir timeouts explícitos. Reutilizar clientes e pools quando forem seguros para concorrência e encerrar recursos no lifecycle da aplicação.

### Falhas e resiliência

Classificar falhas relevantes em erros internos, distinguindo ao menos indisponibilidade temporária, timeout, rejeição permanente, autenticação/configuração inválida e resposta malformada quando esses estados afetarem o caso de uso.

Adicionar retries apenas para operações seguras ou idempotentes. Aplicar quantidade limitada de tentativas e backoff. Não repetir automaticamente operações que possam duplicar cobranças, mensagens ou gravações sem idempotency key ou garantia equivalente.

Preservar identificadores de correlação e idempotência quando suportados. Não capturar `Exception` de forma indiscriminada; capturar falhas documentadas da biblioteca no menor escopo possível.

### Observabilidade

Registrar operação, duração, resultado técnico, request ID, tenant e identificadores não sensíveis. Não registrar tokens, senhas, cookies, documentos completos, payloads pessoais ou respostas integrais do provedor.

## 4. Injeção de dependências

Registrar toda implementação concreta no composition root com Dependency Injector:

- `Singleton` para clientes compartilháveis e thread-safe;
- `Factory` para adapters sem estado ou com estado por resolução;
- `Resource` para clientes e conexões que exigem inicialização e encerramento;
- `Configuration` para endpoints, credenciais, timeouts e flags.

Injetar a interface no caso de uso e a implementação concreta apenas no container. Validar que providers resolvem, overrides funcionam nos testes e resources encerram corretamente.

## 5. Estratégia de testes

### Testes de contrato

Executar o mesmo conjunto de comportamentos essenciais contra fakes e adapters reais quando viável. Verificar semântica, não detalhes internos de queries ou chamadas privadas.

### Repositories

Cobrir:

- criação, consulta, atualização e ausência previstas pelo contrato;
- mapeamento completo entre domínio e ORM;
- constraints, duplicidade e tradução de erros;
- commit e rollback;
- isolamento multi-tenant;
- paginação e ordenação determinística, quando aplicáveis.

Usar PostgreSQL real em container para semântica de persistência sempre que o projeto disponibilizar esse ambiente; não assumir equivalência do SQLite.

### Integrações externas

Cobrir:

- request produzido e response traduzida;
- autenticação e headers sem expor segredos;
- timeout, indisponibilidade e rejeição permanente;
- resposta inválida ou incompleta;
- idempotency key, retries e ausência de repetição insegura;
- encerramento do cliente e comportamento do provider no container.

Usar servidor fake, transport controlado ou stub oficial do cliente. Não depender da rede pública nem de credenciais reais na suíte automatizada.

## 6. Checklist de conclusão

- [ ] Ler `AGENTS.md`, especificações e ADRs aplicáveis.
- [ ] Confirmar que a porta interna existe e usa prefixo `I`.
- [ ] Evitar tipos de ORM, HTTP ou SDK no contrato interno.
- [ ] Manter regras de negócio fora da infraestrutura.
- [ ] Implementar mapeamento e tradução de erros explicitamente.
- [ ] Preservar tenant em todas as operações persistentes.
- [ ] Definir transações e rollback corretamente.
- [ ] Configurar timeouts, lifecycle, idempotência e retries seguros.
- [ ] Registrar o adapter no Dependency Injector.
- [ ] Proteger dados sensíveis em configuração e logs.
- [ ] Adicionar testes de contrato e integração proporcionais ao risco.
- [ ] Executar Ruff format, Ruff check, Pyright e Pytest.
- [ ] Revisar o diff e relatar limitações externas reais.
