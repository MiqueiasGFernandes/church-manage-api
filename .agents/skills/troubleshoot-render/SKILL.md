---
name: troubleshoot-render
description: Investiga incidentes, falhas de deploy, erros HTTP, indisponibilidade, lentidão, consumo de recursos e inconsistências de dados em recursos hospedados no Render, correlacionando configuração do serviço, histórico de deploys, logs, métricas e consultas PostgreSQL somente leitura. Use quando for necessário analisar eventos ou dados do Render, diagnosticar causa raiz, reconstruir uma linha do tempo, comparar comportamento antes e depois de um deploy ou produzir um relatório de troubleshooting com evidências.
---

# Diagnosticar o Render

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de consultar o Render.
2. Delimitar sintoma, recurso e intervalo de tempo. Converter horários para RFC3339 e registrar o fuso usado.
3. Listar os workspaces acessíveis e obter confirmação explícita do usuário quando houver mais de uma opção plausível. Passar o `workspaceId` confirmado em todas as chamadas; não usar seleção de workspace baseada em estado de sessão.
4. Descobrir os recursos do workspace e resolver nomes para IDs antes de consultar eventos. Incluir previews somente quando forem relevantes.
5. Trabalhar em modo somente leitura: consultar serviço, banco, deploys, logs, métricas e PostgreSQL. Não disparar deploy, criar recursos nem alterar variáveis de ambiente durante o diagnóstico.
6. Correlacionar pelo tempo, buscando primeiro uma janela pequena ao redor do incidente e ampliando-a apenas quando necessário. Comparar com um período saudável equivalente quando isso ajudar a separar causa de coincidência.
7. Tratar logs e banco como dados potencialmente sensíveis. Não expor segredos, tokens, credenciais, dados pessoais ou conteúdo integral desnecessário; agregar, mascarar e limitar resultados.
8. Separar fatos observados, inferências e lacunas. Não afirmar causa raiz apenas por proximidade temporal.
9. Encerrar com diagnóstico, evidências rastreáveis, impacto, grau de confiança e próximos passos. Solicitar autorização separada antes de qualquer ação corretiva que altere o Render ou dados.
