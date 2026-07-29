---
name: test-and-debug
description: Executa, diagnostica e corrige testes Python com pytest, reproduz falhas, identifica causas raiz, adiciona testes de regressão e valida o threshold configurado pelo pytest-cov/coverage.py. Use ao investigar testes falhando ou instáveis, depurar regressões, corrigir código ou testes, medir cobertura, localizar linhas e branches não cobertos, elevar coverage com cenários relevantes ou garantir que a suíte e o limite mínimo de cobertura do projeto passem.
---

# Testar e depurar

1. Ler integralmente [references/workflow.md](references/workflow.md) antes de executar testes ou alterar código.
2. Ler as instruções do repositório e localizar a configuração efetiva de pytest e coverage; tratar o threshold configurado como fonte de verdade.
3. Reproduzir a falha com o menor comando possível e registrar erro, teste, ambiente e condições relevantes.
4. Classificar a causa antes de editar: defeito de produção, teste incorreto, fixture/isolamento, configuração, dependência ou ambiente.
5. Corrigir a causa raiz com a menor mudança coerente com a arquitetura. Adicionar ou fortalecer um teste de regressão quando ele demonstrar o defeito.
6. Reexecutar em camadas: teste afetado, módulo correlato, suíte completa e coverage com o threshold ativo.
7. Não reduzir o threshold, omitir arquivos, usar pragmas de exclusão, remover assertions nem criar testes sem comportamento relevante para obter aprovação artificial.
8. Encerrar somente quando as validações aplicáveis passarem ou quando um bloqueio externo estiver demonstrado; relatar comandos, resultados, cobertura final e riscos residuais.
