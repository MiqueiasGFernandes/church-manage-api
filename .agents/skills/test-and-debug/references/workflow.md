# Workflow de teste, depuração e coverage

## 1. Descobrir as regras do projeto

1. Ler `AGENTS.md` e arquivos equivalentes aplicáveis ao escopo.
2. Inspecionar `pyproject.toml`, `pytest.ini`, `setup.cfg`, `tox.ini` e `.coveragerc` existentes.
3. Identificar:
   - comando e ambiente oficiais de teste;
   - diretórios e markers da suíte;
   - configuração assíncrona, fixtures e serviços externos;
   - fontes medidas, branches, omissões e `fail_under` do coverage.
4. Preservar a configuração versionada. Neste projeto, usar `uv run pytest` e considerar `[tool.coverage.report].fail_under` no `pyproject.toml` como threshold vigente.

Não presumir que um teste isolado representa a suíte completa. Testes de integração ou E2E podem exigir PostgreSQL e variáveis documentadas no repositório.

## 2. Reproduzir antes de corrigir

Executar primeiro o menor alvo que reproduza o problema, por exemplo:

```bash
uv run pytest tests/<arquivo>.py::<teste> -vv -x
```

- Capturar o primeiro traceback completo e a diferença entre esperado e obtido.
- Reexecutar um teste suspeito de instabilidade algumas vezes apenas quando houver evidência de flakiness.
- Não alterar código antes de confirmar a falha, salvo erro estático inequívoco ou impossibilidade documentada de montar o ambiente.
- Se o problema não reproduzir, comparar comando, variáveis, dependências, banco, ordem, relógio, locale e aleatoriedade com o ambiente onde ocorreu.

## 3. Diagnosticar a causa raiz

Rastrear o fluxo do teste até o primeiro estado incorreto. Inspecionar implementação, contratos, fixtures e testes correlatos. Classificar a falha:

- **Produção:** a implementação viola requisito, contrato ou invariante.
- **Teste:** a expectativa está desatualizada ou testa detalhe interno sem garantia pública.
- **Isolamento:** há estado compartilhado, ordem implícita, cleanup incompleto ou colisão de dados.
- **Ambiente:** serviço, variável, migração, versão ou dependência está ausente ou divergente.
- **Concorrência/tempo:** há race condition, timeout arbitrário, relógio real ou espera não determinística.

Usar `-s`, logs, debugger, `caplog`, inspeções temporárias ou queries somente para obter evidência. Remover instrumentação descartável antes de concluir. Não mascarar sintomas com retries, sleeps maiores ou assertions mais fracas.

## 4. Corrigir e proteger contra regressão

1. Fazer a menor alteração que restaure o comportamento correto na camada responsável.
2. Preservar Clean Architecture, tipagem e contratos públicos do projeto.
3. Adicionar teste de regressão que falhe sem a correção e passe com ela quando não existir cobertura comportamental suficiente.
4. Corrigir o teste somente quando a expectativa estiver comprovadamente errada; não adaptar expectativas a uma implementação defeituosa.
5. Para falhas de isolamento, tornar dados únicos, controlar fronteiras não determinísticas e limpar apenas o estado pertencente ao teste.

Quando a correção exigir trabalho especializado de feature, infraestrutura ou E2E, aplicar também a skill específica disponível no projeto.

## 5. Validar em camadas

Executar progressivamente:

```bash
uv run pytest tests/<arquivo>.py::<teste> -q
uv run pytest tests/<área-relacionada> -q
uv run pytest -q
uv run pytest --cov --cov-report=term-missing
```

O último comando deve terminar com código zero e aplicar automaticamente o `fail_under` configurado. Não passar um `--cov-fail-under` menor. Se a configuração do projeto exigir alvos explícitos, reproduzir os valores de `[tool.coverage.run].source` sem alterar seu escopo.

Executar também as verificações afetadas pela mudança:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

Adaptar comandos somente às convenções reais do repositório. Se a suíte completa for cara, ainda executar o coverage oficial quando ele for parte do critério solicitado; não inferir aprovação a partir de uma seleção parcial.

## 6. Corrigir déficit de coverage com qualidade

1. Ler o relatório `term-missing` e priorizar regras, branches de erro e invariantes relevantes não exercitados.
2. Mapear cada linha ausente para um comportamento observável antes de criar o teste.
3. Preferir testes no nível mais baixo que comprovem a regra sem duplicar cobertura já existente; usar integração/E2E quando o risco estiver na composição ou persistência real.
4. Cobrir caminhos felizes, erros, limites e branches somente quando representarem comportamento possível e relevante.
5. Reexecutar o teste novo isoladamente e depois o comando completo de coverage.

É proibido elevar o número artificialmente por meio de testes que apenas importam módulos, chamam código sem assertions significativas, acessam privados só para marcar linhas, duplicam cenários, removem código válido da medição ou adicionam `# pragma: no cover` sem justificativa estrutural independente do threshold.

## 7. Critérios de conclusão

- A causa raiz está identificada e a correção está na camada responsável.
- Existe proteção de regressão adequada quando aplicável.
- Teste focado, testes correlatos e suíte completa passam.
- O comando oficial de coverage passa com o threshold versionado e o percentual final é informado.
- Ruff, formatação e Pyright passam quando afetados.
- Nenhum mecanismo de qualidade foi enfraquecido.
- Qualquer validação não executada tem motivo verificável, impacto e próximo passo explícitos.
