# Contexto do projeto

Confirmar estas informações nas fontes citadas antes de criar ou alterar um workflow; os arquivos
do repositório prevalecem quando houver divergência.

## Integração e runtime

- Seguir `feature/<descricao-curta> → develop → main`, conforme `.agents/AGENTS.md`.
- Usar Python 3.12 e `uv`, conforme `pyproject.toml`, `uv.lock` e `.agents/AGENTS.md`.
- Não editar `uv.lock` manualmente nem substituir Ruff, Pyright ou Pytest por ferramentas
  sobrepostas.

## CI

- Sincronizar dependências a partir do lockfile, sem atualizar resoluções implicitamente.
- Executar `uv run ruff check .`.
- Limitar a verificação de formato a `src` e `tests` enquanto os documentos Markdown em `.agents`
  contiverem exemplos Python deliberadamente não formatados: `uv run ruff format --check src tests`.
- Executar `uv run pyright` em modo estrito.
- Subir o serviço `postgres` de `docker-compose.yml` antes da suíte completa; os testes E2E usam o
  PostgreSQL de teste na porta publicada pelo Compose.
- Executar `uv run pytest --cov --cov-report=term-missing`. O limite vigente está em
  `[tool.coverage.report].fail_under` no `pyproject.toml` e não pode ser reduzido pelo workflow.
- Preferir os mesmos comandos do hook em `.pre-commit-config.yaml` quando isso mantiver CI e
  validação local equivalentes.

## Container e deploy

- Validar `docker compose config --quiet` quando alterar serviços ou dependências de teste.
- Construir a aplicação pelo `Dockerfile` existente; confirmar argumentos e smoke test no próprio
  arquivo e no `README.md`.
- Preservar portabilidade entre provedores. Não introduzir dependência exclusiva de cloud sem uma
  decisão arquitetural autorizada.
- Para deploy em produção, respeitar o Git Flow e exigir verificações anteriores, environment
  protegido, concorrência explícita e credenciais mínimas. Confirmar na documentação oficial atual
  os detalhes do provedor e nunca criar recursos remotos sem autorização.
