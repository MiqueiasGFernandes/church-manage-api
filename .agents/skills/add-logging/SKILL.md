---
name: add-logging
description: Adiciona e revisa logs estruturados, contextuais, seguros, acionáveis e não redundantes neste projeto. Use ao instrumentar novos fluxos, melhorar observabilidade, criar middleware de logging, registrar erros ou eventos de negócio, definir níveis e campos, propagar correlação ou remover logs duplicados e dados sensíveis.
---

# Adicionar logs

1. Ler integralmente as seções `Logging` e `Dados sensíveis` de
   `.agents/AGENTS.md` antes de analisar ou alterar código.
2. Mapear o fluxo completo e os logs existentes nas camadas envolvidas.
3. Definir o evento no limite que reúne contexto suficiente para explicá-lo.
   Não registrar o mesmo resultado novamente em camadas internas e externas.
4. Preferir um evento de resultado a pares `started`/`completed`. Registrar início
   somente para operações longas em que ausência de conclusão seja útil.
5. Usar a infraestrutura de `app.observability`; não configurar handlers em
   módulos de negócio nem adicionar outra biblioteca sem necessidade comprovada.
6. Escrever `message` técnica, estável, em inglês e no passado quando representar
   um fato. Manter valores variáveis exclusivamente em campos estruturados.
7. Incluir `operation`, contexto mínimo de investigação e `action`. Usar
   `No action required.` apenas em resultados saudáveis; em avisos e erros,
   indicar uma ação concreta para diagnóstico ou mitigação.
8. Classificar o nível: `INFO` para sucesso relevante, `WARNING` para rejeição ou
   condição tratada que merece atenção e `ERROR`/`EXCEPTION` apenas para falha
   inesperada. Incluir stack trace uma única vez, no limite responsável.
9. Nunca registrar segredos, credenciais, tokens, cookies, payloads, cabeçalhos,
   query strings, documentos, dados financeiros, e-mails, telefones, IPs ou IDs de
   sessão. Avaliar identificadores de recurso pelo princípio da minimização.
10. Excluir health checks e probes de alta frequência quando saudáveis.
11. Adicionar testes que capturem os registros e comprovem campos, nível,
    correlação, ausência de redundância e ausência de dados sensíveis relevantes.
12. Executar testes, Ruff e Pyright; revisar o diff procurando mensagens vagas,
    ações genéricas, duplicação e serialização acidental de objetos sensíveis.
