# Workflow de troubleshooting no Render

## 1. Definir o incidente

Registrar antes das consultas:

- sintoma observável e resultado esperado;
- serviço, banco ou Key Value afetado;
- início e fim aproximados, fuso e se o incidente continua;
- host, rota, método, status HTTP, request/correlation ID ou mensagem de erro conhecidos;
- mudança recente suspeita, sem tratá-la antecipadamente como causa.

Se o usuário disser apenas “agora”, começar pelos últimos 60 minutos. Usar RFC3339 nas consultas e explicitar as conversões de fuso. O Render limita logs e métricas aos últimos 30 dias; informar essa limitação quando o incidente estiver fora da janela.

## 2. Resolver workspace e recursos com segurança

1. Usar `render_list_workspaces`.
2. Se houver mais de um workspace plausível, apresentar nomes e pedir ao usuário que escolha. Não inferir pelo workspace armazenado na sessão.
3. Reutilizar o `workspaceId` confirmado em todas as chamadas seguintes.
4. Usar `render_list_services`, `render_list_postgres_instances` e `render_list_key_value` conforme o escopo.
5. Resolver o nome informado para um ID único. Quando houver ambiguidade, pedir confirmação antes de acessar dados.
6. Usar `render_get_service`, `render_get_postgres` ou `render_get_key_value` para obter contexto do recurso.

Não usar `render_select_workspace`: a seleção é legada e pode direcionar chamadas posteriores ao ambiente errado.

## 3. Construir a linha do tempo

Consultar na seguinte ordem, adaptando ao sintoma:

1. **Deploys:** usar `render_list_deploys` e `render_get_deploy` para identificar início, conclusão, status, commit/imagem e deploy ativo. Incluir logs de tipo `build` quando houver falha de build ou startup.
2. **Logs:** usar `render_list_logs` com recurso e janela explícitos. Começar com filtros de alta precisão disponíveis, como tipo, nível, status, host, método, path, instance, texto ou identificador de correlação.
3. **Métricas:** usar `render_get_metrics` na mesma janela para CPU, memória, instâncias, requisições, latência, banda ou conexões ativas, conforme o tipo de recurso.
4. **Dados:** usar `render_query_render_postgres` somente quando uma hipótese exigir confirmação no banco.

Alinhar timestamps dos eventos em uma linha do tempo única. Comparar, quando útil, cinco pontos: antes da mudança, início do deploy, ativação, primeiro sintoma e recuperação.

### Paginação e cardinalidade

- Em deploys, seguir o cursor somente até cobrir a janela relevante.
- Em logs, se `hasMore` for verdadeiro, reutilizar `nextStartTime` e `nextEndTime`; não concluir ausência de eventos olhando apenas a primeira página.
- Usar `render_list_log_label_values` para descobrir filtros disponíveis quando a cardinalidade ou nomenclatura for desconhecida.
- Preferir filtros e agregações a despejos extensos. Para métricas, aumentar `resolution` se a quantidade de pontos causar erro.

## 4. Escolher evidências por sintoma

### Falha de deploy ou inicialização

- Comparar deploy atual e último deploy saudável.
- Consultar logs `build` e `app` desde o início do deploy.
- Procurar erro de dependência, comando, migração, bind de porta, health check, timeout, OOM ou configuração ausente.
- Verificar se o primeiro erro precede ou sucede a ativação do deploy.

### Erros HTTP ou indisponibilidade

- Agregar `http_request_count` por `statusCode`.
- Consultar `http_latency` em p50, p95 e p99 quando a distribuição importar.
- Filtrar logs `request` por host, path, método e status; correlacionar com logs `app` próximos.
- Separar erro da aplicação, saturação, ausência de instâncias e falha de dependência.

### Lentidão ou saturação

- Comparar `cpu_usage`/`memory_usage` com limites e targets.
- Correlacionar instâncias, latência, volume de requisições e banda.
- Para Postgres ou Key Value, verificar conexões ativas e sinais correspondentes nos logs.
- Não inferir saturação somente por um pico isolado; observar duração e coincidência com degradação.

### Suspeita de inconsistência no PostgreSQL

Consultar apenas os dados mínimos necessários. Preferir:

- `COUNT`, agregações e agrupamentos;
- colunas técnicas e identificadores não sensíveis;
- filtros por tenant, estado e intervalo temporal;
- `LIMIT` explícito em amostras;
- consultas ao catálogo para descobrir schema antes de presumir nomes.

Nunca consultar senhas, hashes, tokens, segredos, documentos pessoais ou payloads integrais sem necessidade comprovada. Não usar `SELECT *`. Embora a ferramenta imponha transação somente leitura, evitar consultas sem filtro, scans grandes, funções custosas e locks explícitos.

## 5. Testar hipóteses

Para cada hipótese relevante, registrar:

1. previsão observável;
2. consulta ou comparação usada;
3. evidência favorável e contrária;
4. conclusão: confirmada, provável, improvável ou inconclusiva.

Exigir pelo menos duas fontes independentes para uma causa raiz de alta confiança quando elas existirem, por exemplo deploy + logs, logs + métricas ou logs + banco. Proximidade temporal gera hipótese, não causalidade.

## 6. Preservar segurança operacional

- Mascarar segredos e identificadores pessoais nos trechos apresentados.
- Parafrasear payloads sensíveis e retornar somente as linhas indispensáveis.
- Não armazenar resultados do Render em arquivos do repositório sem pedido explícito.
- Não executar `render_trigger_deploy`, `render_update_environment_variables` nem ferramentas de criação durante troubleshooting.
- Se uma correção for recomendada, explicar efeito, risco e forma de validação e obter autorização em uma etapa separada.
- Não executar SQL de escrita, DDL, funções com efeitos colaterais ou tentativas de contornar o modo somente leitura.

## 7. Relatar o resultado

Usar esta estrutura compacta:

```markdown
## Diagnóstico
<causa confirmada ou hipótese mais provável; confiança alta/média/baixa>

## Linha do tempo
- <timestamp e fuso> — <evento e fonte>

## Evidências
- <deploy/log/métrica/query, recurso, janela e observação>

## Impacto
<recursos, rotas, tenants e duração comprovados>

## Próximos passos
1. <ação recomendada, risco e validação>

## Lacunas
- <dado ausente ou hipótese ainda não comprovada>
```

Não reproduzir segredos nem grandes blocos de logs no relatório. Citar IDs de recurso, deploy e horários suficientes para tornar a análise reproduzível.
