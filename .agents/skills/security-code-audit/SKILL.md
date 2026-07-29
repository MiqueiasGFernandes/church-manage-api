---
name: security-code-audit
description: Audita estaticamente a segurança de código e configuração, valida vulnerabilidades com evidências rastreáveis, classifica severidade e CWE, distingue achados confirmados de riscos condicionais e exporta um relatório Markdown acionável e ignorado pelo Git. Use ao procurar vulnerabilidades, revisar autenticação, autorização, sessões, criptografia, validação de entrada, persistência, multi-tenancy, segredos, dependências, configuração HTTP, abuso ou disponibilidade, produzir security review, threat-oriented code review ou relatório em reports/security.
---

# Auditar segurança do código

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de iniciar a análise.
2. Ler as instruções do repositório e definir escopo, modelo de implantação e limitações conhecidas.
3. Mapear superfícies de ataque e fronteiras de confiança antes de procurar achados isolados.
4. Validar cada suspeita no fluxo completo e eliminar falsos positivos antes de classificá-la.
5. Usar evidências rastreáveis de arquivo e linha; nunca afirmar explorabilidade além do demonstrado.
6. Priorizar impacto real em confidencialidade, integridade, disponibilidade e isolamento de tenant.
7. Gerar o relatório a partir de [assets/report-template.md](assets/report-template.md), adaptando seções ao escopo.
8. Salvar por padrão em `reports/security/security-audit-AAAA-MM-DD.md` e garantir que
   `reports/security/` esteja no `.gitignore`, salvo instrução diferente do usuário.
9. Não corrigir vulnerabilidades durante uma solicitação apenas de auditoria. Implementar correções
   somente quando solicitado, usando as skills especializadas aplicáveis.
10. Revisar o relatório final, confirmar que está ignorado pelo Git e informar achados, limitações e
    caminho do artefato.
