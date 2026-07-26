---

name: readme-maintainer
description: Cria, reorganiza e atualiza o README.md do projeto, mantendo a documentação clara, visualmente agradável, tecnicamente correta e sincronizada com o código-fonte.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# README Maintainer

## Objetivo

Criar ou atualizar o arquivo `README.md` do projeto de forma que ele seja:

* visualmente agradável;
* fácil de navegar;
* tecnicamente correto;
* coerente com a arquitetura atual;
* útil para novos desenvolvedores;
* útil para usuários e mantenedores;
* conciso, sem omitir informações importantes;
* sincronizado com o código-fonte e com os documentos oficiais do projeto.

A skill deve analisar o repositório antes de modificar o README. Nunca deve inventar funcionalidades, comandos, tecnologias, integrações ou decisões arquiteturais que não possam ser confirmadas no projeto.

---

## Quando utilizar esta skill

Utilize esta skill quando a solicitação envolver:

* criar um novo `README.md`;
* melhorar a organização do README existente;
* atualizar instruções de instalação ou execução;
* documentar novas funcionalidades;
* atualizar arquitetura, stack ou estrutura de diretórios;
* adicionar badges;
* documentar variáveis de ambiente;
* documentar comandos de testes, lint, build ou migrações;
* corrigir informações desatualizadas;
* preparar o projeto para publicação no GitHub;
* melhorar a experiência de onboarding de desenvolvedores;
* padronizar a documentação principal do repositório.

---

## Princípios obrigatórios

### 1. O repositório é a fonte da verdade

Antes de criar ou atualizar o README, analise os arquivos relevantes do projeto.

Priorize, quando existirem:

* `AGENTS.md`;
* `pyproject.toml`;
* `requirements.txt`;
* `requirements-dev.txt`;
* `poetry.lock`;
* `uv.lock`;
* `Pipfile`;
* `Dockerfile`;
* `docker-compose.yml`;
* `compose.yml`;
* `.env.example`;
* `Makefile`;
* `Taskfile.yml`;
* arquivos de configuração de CI/CD;
* arquivos de configuração de testes;
* arquivos de configuração de lint e type checking;
* diretórios principais do código;
* scripts de inicialização;
* documentação dentro de `docs/`;
* arquivos de migração;
* especificações OpenAPI;
* manifests de infraestrutura;
* README existente.

Não presuma que um comando comum funciona apenas porque a tecnologia está presente.

Exemplo incorreto:

```bash
pytest
```

Esse comando só deve ser documentado se o projeto realmente utilizar `pytest` e se o modo de execução puder ser confirmado.

---

### 2. Não inventar informações

Nunca invente:

* funcionalidades;
* endpoints;
* comandos;
* variáveis de ambiente;
* versões;
* requisitos;
* integrações;
* decisões arquiteturais;
* fluxos de autenticação;
* instruções de deploy;
* badges;
* URLs;
* status de build;
* percentual de cobertura;
* licença;
* roadmap;
* contribuidores.

Quando uma informação necessária não estiver disponível:

1. omita a informação; ou
2. utilize um marcador explícito, como:

```markdown
> TODO: documentar o processo de deploy.
```

Não transforme uma suposição em afirmação.

---

### 3. Preservar informações válidas

Ao atualizar um README existente:

* preserve informações corretas e ainda relevantes;
* remova duplicações;
* corrija informações comprovadamente desatualizadas;
* reorganize conteúdo confuso;
* não apague seções importantes sem justificativa;
* não substitua conteúdo específico por texto genérico;
* mantenha instruções operacionais que ainda sejam necessárias;
* preserve links válidos;
* preserve avisos importantes;
* preserve créditos e licenças existentes.

A atualização deve ser incremental sempre que possível.

---

### 4. Clareza acima de ornamentação

O README deve ser bonito, mas não excessivamente decorativo.

Use com moderação:

* emojis;
* badges;
* tabelas;
* diagramas;
* blocos de destaque;
* separadores;
* elementos HTML.

Evite:

* excesso de emojis;
* dezenas de badges;
* banners sem função;
* textos promocionais genéricos;
* imagens pesadas;
* seções vazias;
* tabelas muito largas;
* centralização excessiva;
* HTML desnecessário;
* frases produzidas apenas para parecer sofisticadas.

A estética deve melhorar a leitura, não competir com o conteúdo.

---

## Processo obrigatório

## Etapa 1 — Analisar o projeto

Antes de editar o README:

1. identifique a linguagem principal;
2. identifique o framework principal;
3. identifique o gerenciador de dependências;
4. identifique a versão mínima da linguagem;
5. identifique os comandos realmente disponíveis;
6. identifique a arquitetura utilizada;
7. identifique os módulos principais;
8. identifique os serviços externos;
9. identifique como as configurações são fornecidas;
10. identifique como a aplicação é executada;
11. identifique como os testes são executados;
12. identifique como lint, formatação e type checking são executados;
13. identifique como o banco de dados é preparado;
14. identifique como as migrações são executadas;
15. identifique se existe Docker;
16. identifique se existe documentação adicional;
17. identifique se o projeto possui licença;
18. identifique se existe CI/CD;
19. identifique se há instruções específicas no `AGENTS.md`;
20. compare essas informações com o README atual.

---

## Etapa 2 — Classificar o estado do README

Classifique internamente o README em uma das seguintes situações:

### Inexistente

Não há `README.md`.

A ação esperada é criar o documento do zero com base no conteúdo real do repositório.

### Mínimo

Existe, mas contém apenas título, descrição curta ou poucas instruções.

A ação esperada é expandir o documento sem inventar informações.

### Desorganizado

Possui informações úteis, porém:

* seções estão fora de ordem;
* comandos estão misturados;
* existem repetições;
* a formatação é inconsistente;
* faltam links internos;
* há blocos excessivamente longos.

A ação esperada é reorganizar e padronizar.

### Desatualizado

Contém informações incompatíveis com o código atual.

A ação esperada é atualizar os pontos confirmados pelo repositório.

### Maduro

Já possui boa estrutura e informações corretas.

A ação esperada é fazer alterações pontuais, preservando a organização existente.

---

## Etapa 3 — Definir a estrutura adequada

Não é obrigatório utilizar todas as seções disponíveis.

Selecione apenas as seções relevantes para o projeto.

Uma ordem recomendada é:

1. cabeçalho;
2. visão geral;
3. principais funcionalidades;
4. demonstração ou screenshots;
5. arquitetura;
6. stack tecnológica;
7. requisitos;
8. instalação;
9. configuração;
10. execução;
11. testes e qualidade;
12. estrutura do projeto;
13. API;
14. banco de dados;
15. Docker;
16. deploy;
17. documentação adicional;
18. contribuição;
19. roadmap;
20. licença.

A ordem pode ser adaptada conforme o tipo de projeto.

---

## Estrutura recomendada do README

## 1. Cabeçalho

O cabeçalho pode conter:

```markdown
# Nome do projeto

Descrição curta e objetiva do propósito do projeto.
```

Opcionalmente:

```html
<div align="center">

# Nome do projeto

Descrição curta e objetiva.

</div>
```

Evite centralizar todo o documento.

---

## 2. Badges

Adicione badges apenas quando seus valores e URLs forem verificáveis.

Exemplos possíveis:

* versão da linguagem;
* versão do framework;
* status do CI;
* cobertura de testes;
* licença;
* formatter;
* linter;
* type checker;
* Docker.

Nunca utilize badges falsos ou placeholders que pareçam reais.

Quando o projeto ainda não possuir integração verificável, prefira não incluir o badge.

---

## 3. Visão geral

Explique:

* qual problema o projeto resolve;
* para quem ele foi criado;
* qual seu principal objetivo;
* qual o escopo atual;
* o que diferencia o projeto.

Evite introduções genéricas como:

```markdown
Este é um projeto moderno, escalável e robusto.
```

Prefira informações concretas:

```markdown
O projeto fornece uma API para gestão de igrejas, incluindo membros,
congregações, células, ministérios, eventos e contribuições financeiras.
```

---

## 4. Funcionalidades

Liste apenas funcionalidades existentes ou explicitamente identificadas como planejadas.

Separe funcionalidades implementadas de funcionalidades futuras.

Exemplo:

```markdown
## Funcionalidades

- Cadastro de igrejas.
- Gestão de membros.
- Aprovação de autocadastros.
- Organização de células e ministérios.
```

Para funcionalidades futuras:

```markdown
## Roadmap

- [ ] Importação de membros por planilha.
- [ ] Integração com meios de pagamento.
```

Não apresente roadmap como funcionalidade pronta.

---

## 5. Arquitetura

Quando a arquitetura puder ser confirmada, explique:

* estilo arquitetural;
* camadas;
* direção das dependências;
* responsabilidades principais;
* limites entre domínio e infraestrutura;
* mecanismos de injeção de dependência;
* principais fluxos.

Exemplo para Clean Architecture:

```markdown
## Arquitetura

A aplicação utiliza Clean Architecture, separando as responsabilidades em:

- `domain`: entidades, value objects e regras de negócio;
- `application`: casos de uso e contratos;
- `infrastructure`: persistência, integrações e implementações técnicas;
- `presentation`: interfaces HTTP e schemas de entrada e saída.

As dependências apontam para as camadas internas. O domínio não depende de
frameworks, banco de dados ou mecanismos de transporte.
```

Não declare que o projeto segue Clean Architecture apenas por possuir pastas com nomes semelhantes. Confirme também pelas dependências e responsabilidades.

---

## 6. Stack tecnológica

Prefira uma tabela pequena e objetiva:

```markdown
## Stack tecnológica

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| API | FastAPI |
| Validação | Pydantic |
| Persistência | SQLAlchemy |
| Banco de dados | PostgreSQL |
| Testes | Pytest |
| Qualidade | Ruff e mypy |
```

Inclua somente tecnologias confirmadas.

Não liste bibliotecas transitivas como parte da stack principal.

---

## 7. Requisitos

Documente pré-requisitos reais.

Exemplo:

```markdown
## Requisitos

- Python 3.12 ou superior.
- PostgreSQL 16.
- Docker e Docker Compose, para execução em containers.
```

Quando houver alternativas, deixe claro:

```markdown
O Docker é opcional. A aplicação também pode ser executada diretamente em um
ambiente virtual Python.
```

---

## 8. Instalação

Os comandos devem ser copiáveis e executáveis.

Exemplo:

````markdown
## Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_DIRETORIO>
````

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

````

Ajuste os comandos ao gerenciador realmente utilizado pelo projeto.

Não misture `pip`, Poetry, uv e Pipenv sem explicar claramente as alternativas.

---

## 9. Configuração

Quando existir `.env.example`, documente o processo:

```markdown
## Configuração

Copie o arquivo de exemplo:

```bash
cp .env.example .env
````

Preencha as variáveis de acordo com o ambiente.

````

Quando útil, documente as variáveis em tabela:

```markdown
| Variável | Obrigatória | Descrição | Exemplo |
|---|---:|---|---|
| `DATABASE_URL` | Sim | URL de conexão com o banco | `postgresql+asyncpg://...` |
| `APP_ENV` | Não | Ambiente da aplicação | `development` |
````

Nunca exponha:

* senhas;
* tokens;
* chaves privadas;
* secrets reais;
* credenciais;
* URLs internas sensíveis.

Utilize valores fictícios claramente identificáveis.

---

## 10. Execução

Separe os modos de execução quando necessário.

Exemplo:

````markdown
## Executando a aplicação

### Desenvolvimento

```bash
uvicorn src.main:app --reload
````

### Produção

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

````

Documente portas e URLs apenas quando confirmadas.

---

## 11. Testes e qualidade

Agrupe comandos relacionados:

```markdown
## Testes e qualidade

Executar os testes:

```bash
pytest
````

Executar testes com cobertura:

```bash
pytest --cov=src --cov-report=term-missing
```

Executar lint:

```bash
ruff check .
```

Executar formatação:

```bash
ruff format .
```

Executar verificação de tipos:

```bash
mypy src tests
```

````

Se o projeto possuir um comando unificado, prefira documentá-lo:

```bash
make check
````

Explique brevemente o que o comando executa.

---

## 12. Estrutura de diretórios

Mostre apenas os diretórios importantes.

Exemplo:

```text
.
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── tests/
├── docs/
├── migrations/
├── pyproject.toml
└── README.md
```

Não copie toda a árvore do repositório.

Ignore normalmente:

* `.git`;
* `.venv`;
* caches;
* arquivos compilados;
* dependências instaladas;
* arquivos temporários;
* diretórios gerados;
* secrets;
* logs.

Após a árvore, explique os diretórios principais quando os nomes não forem autoexplicativos.

---

## 13. API

Quando o projeto fornecer uma API, documente:

* URL local;
* prefixo de rotas;
* documentação Swagger;
* documentação ReDoc;
* autenticação;
* versionamento;
* formato de erro;
* link para especificação OpenAPI.

Exemplo:

```markdown
## API

Com a aplicação em execução:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI: `http://localhost:8000/openapi.json`
```

Inclua esses endereços somente se forem compatíveis com a configuração real.

Não replique no README toda a documentação da API. Direcione para a especificação OpenAPI ou para documentos específicos.

---

## 14. Banco de dados e migrações

Quando aplicável, documente:

* banco utilizado;
* criação inicial;
* migrações;
* rollback;
* seed;
* reset local;
* restrições importantes.

Exemplo:

````markdown
## Migrações

Aplicar todas as migrações:

```bash
alembic upgrade head
````

Criar uma nova migração:

```bash
alembic revision --autogenerate -m "descrição da alteração"
```

Reverter a última migração:

```bash
alembic downgrade -1
```

````

Somente documente comandos confirmados pela configuração do projeto.

---

## 15. Docker

Quando o projeto tiver suporte a containers:

```markdown
## Docker

Subir os serviços:

```bash
docker compose up --build
````

Executar em segundo plano:

```bash
docker compose up -d
```

Parar os serviços:

```bash
docker compose down
```

````

Explique quais serviços são iniciados, por exemplo:

- API;
- PostgreSQL;
- Redis;
- worker;
- proxy.

Não presuma os nomes dos serviços.

---

## 16. Diagramas

Diagramas podem ser criados em Mermaid quando melhorarem a compreensão.

Exemplo:

```mermaid
flowchart LR
    Client[Cliente] --> API[API]
    API --> UseCase[Casos de uso]
    UseCase --> Domain[Domínio]
    UseCase --> Repository[Contrato de repositório]
    Repository --> Database[(Banco de dados)]
````

Use diagramas apenas quando:

* houver um fluxo relevante;
* a arquitetura não puder ser explicada claramente apenas com texto;
* os componentes puderem ser confirmados;
* o diagrama permanecer legível.

Evite diagramas grandes e excessivamente detalhados no README. Mova diagramas complexos para `docs/architecture/`.

---

## 17. Documentação adicional

Crie links para documentos existentes:

```markdown
## Documentação

- [Requisitos funcionais](docs/requirements.md)
- [Modelagem de domínio](docs/domain-model.md)
- [Arquitetura](docs/architecture.md)
- [Decisões arquiteturais](docs/adr/)
- [Especificação da API](docs/openapi.yaml)
```

Confirme os caminhos antes de criar os links.

---

## 18. Contribuição

Se o projeto aceitar contribuições, documente um fluxo realista:

```markdown
## Contribuição

1. Crie uma branch a partir de `main`.
2. Implemente a alteração.
3. Adicione ou atualize os testes.
4. Execute as verificações de qualidade.
5. Abra um pull request descrevendo a mudança.
```

Não invente convenções de branch, commit ou pull request.

Quando houver `CONTRIBUTING.md`, mantenha apenas um resumo no README e direcione para o arquivo completo.

---

## 19. Licença

Somente informe uma licença quando existir evidência no projeto, como:

* arquivo `LICENSE`;
* campo de licença no manifesto;
* documentação oficial do projeto.

Exemplo:

```markdown
## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo
[LICENSE](LICENSE) para mais informações.
```

Na ausência de licença, não declare que o projeto é open source.

---

## Padrões visuais

## Títulos

Utilize uma hierarquia consistente:

```markdown
# Título principal
## Seção
### Subseção
```

Nunca pule níveis sem necessidade.

Evite títulos inteiramente em letras maiúsculas.

---

## Sumário

Adicione sumário quando o README for longo.

Exemplo:

```markdown
## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Testes](#testes-e-qualidade)
```

Confirme que os links internos funcionam com os títulos utilizados.

---

## Emojis

Emojis são opcionais.

Quando utilizados, limite-os preferencialmente aos títulos das principais seções.

Exemplo aceitável:

```markdown
## 🚀 Execução
## 🧪 Testes
## 🏗️ Arquitetura
```

Não utilize emojis diferentes em todos os parágrafos ou itens.

Para projetos corporativos, prefira títulos sem emojis, salvo quando o padrão atual do repositório já os utilizar.

---

## Tabelas

Utilize tabelas quando facilitarem comparação ou consulta.

Boas aplicações:

* stack tecnológica;
* variáveis de ambiente;
* comandos;
* status de módulos;
* requisitos;
* portas;
* serviços.

Evite tabelas para textos extensos.

---

## Blocos de código

Todos os comandos devem utilizar uma linguagem apropriada:

```bash
```

```powershell
```

```python
```

```yaml
```

```json
```

Nunca inclua o símbolo `$` antes de comandos copiáveis, exceto quando for necessário representar uma sessão de terminal.

Prefira:

```bash
pytest
```

Em vez de:

```bash
$ pytest
```

---

## Links

Antes de adicionar ou preservar um link:

* confirme se o caminho local existe;
* confirme se a URL está correta;
* utilize texto descritivo;
* evite escrever “clique aqui”;
* prefira links relativos para documentos do repositório.

Exemplo:

```markdown
Consulte a [modelagem de domínio](docs/domain-model.md).
```

---

## Linguagem

O README deve seguir o idioma predominante do projeto.

Para este projeto, utilize português do Brasil, salvo instrução contrária.

Regras de escrita:

* use frases objetivas;
* explique siglas na primeira ocorrência;
* mantenha termos técnicos quando forem mais precisos;
* evite traduções artificiais;
* use voz ativa;
* evite marketing exagerado;
* mantenha consistência terminológica;
* revise ortografia e concordância;
* use acentuação correta.

Exemplo:

```markdown
A aplicação utiliza injeção de dependências para desacoplar os casos de uso
das implementações de infraestrutura.
```

---

## README para projetos Python

Quando o projeto for Python, verifique especialmente:

* versão do Python;
* gerenciador de dependências;
* ambiente virtual;
* pacote principal;
* layout `src`;
* framework web;
* servidor ASGI ou WSGI;
* configuração do `pyproject.toml`;
* comandos de lint;
* formatter;
* type checker;
* testes;
* cobertura;
* migrações;
* variáveis de ambiente;
* entry points;
* Docker;
* scripts registrados no projeto.

O README deve respeitar a forma oficial de execução do repositório.

Exemplo com uv:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src tests
```

Exemplo com Poetry:

```bash
poetry install
poetry run pytest
```

Exemplo com pip:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

Não escolha um gerenciador por preferência pessoal. Utilize o gerenciador configurado no projeto.

---

## Compatibilidade com o AGENTS.md

O `README.md` não deve contradizer o `AGENTS.md`.

Verifique especialmente:

* versão da linguagem;
* arquitetura;
* padrões de código;
* comandos oficiais;
* estratégia de testes;
* ferramentas de qualidade;
* tipagem;
* injeção de dependências;
* estrutura de diretórios;
* regras de contribuição;
* tecnologias permitidas ou proibidas.

Quando houver conflito entre o README atual e o `AGENTS.md`, confirme a situação pelo código e pelos arquivos de configuração.

O `AGENTS.md` orienta o trabalho dos agentes, mas o código e as configurações executáveis continuam sendo evidências essenciais.

---

## Segurança

Nunca inclua no README:

* credenciais reais;
* tokens;
* chaves de API;
* senhas;
* connection strings reais;
* cookies;
* certificados privados;
* chaves SSH;
* informações internas sensíveis;
* URLs privadas;
* dados pessoais;
* segredos presentes acidentalmente no repositório.

Caso encontre um secret real, não o replique. Substitua por um exemplo seguro e sinalize o problema.

Exemplo seguro:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/app
SECRET_KEY=replace-with-a-secure-random-value
```

---

## Estratégia para atualizações

Ao receber uma solicitação para documentar uma nova funcionalidade:

1. encontre a implementação;
2. identifique os pontos de entrada;
3. identifique configurações necessárias;
4. identifique impactos na arquitetura;
5. identifique comandos novos;
6. identifique migrações;
7. identifique alterações de API;
8. identifique testes relacionados;
9. atualize apenas as seções afetadas;
10. verifique se o restante do README continua correto.

Não reescreva todo o documento quando uma atualização pontual for suficiente.

---

## Validação obrigatória

Antes de finalizar, revise o README usando o checklist abaixo.

### Conteúdo

* [ ] O nome do projeto está correto.
* [ ] A descrição corresponde ao propósito real.
* [ ] As funcionalidades foram confirmadas.
* [ ] A stack foi confirmada pelos arquivos do projeto.
* [ ] A arquitetura descrita corresponde ao código.
* [ ] Os requisitos estão completos.
* [ ] Os comandos foram confirmados.
* [ ] As variáveis de ambiente existem.
* [ ] As instruções de banco estão corretas.
* [ ] As instruções de Docker estão corretas.
* [ ] Os links locais apontam para arquivos existentes.
* [ ] A licença foi confirmada.
* [ ] Nenhum segredo foi exposto.

### Organização

* [ ] Há apenas um título de nível 1.
* [ ] A hierarquia de títulos está correta.
* [ ] As seções seguem uma ordem lógica.
* [ ] Não existem seções duplicadas.
* [ ] Não existem parágrafos desnecessariamente longos.
* [ ] O sumário corresponde aos títulos.
* [ ] As tabelas estão legíveis.
* [ ] Os blocos de código possuem linguagem definida.

### Qualidade técnica

* [ ] Os comandos são copiáveis.
* [ ] Não existem comandos inventados.
* [ ] As versões estão corretas.
* [ ] Os nomes de arquivos e diretórios estão corretos.
* [ ] As portas estão corretas.
* [ ] Os exemplos não contêm dados sensíveis.
* [ ] O README não contradiz o `AGENTS.md`.
* [ ] O README não descreve funcionalidades planejadas como implementadas.

### Qualidade textual

* [ ] O texto está em português do Brasil.
* [ ] Não existem erros ortográficos evidentes.
* [ ] A terminologia está consistente.
* [ ] O texto é objetivo.
* [ ] Não existe excesso de emojis ou badges.
* [ ] Não existem frases promocionais sem conteúdo concreto.

---

## Comportamento esperado do agente

Ao executar esta skill, o agente deve:

1. localizar o `README.md`;
2. analisar o repositório;
3. analisar o `AGENTS.md`;
4. identificar divergências;
5. criar ou atualizar o README;
6. preservar conteúdo válido;
7. corrigir conteúdo desatualizado;
8. não inventar informações;
9. aplicar uma estrutura visual consistente;
10. validar comandos, caminhos e referências;
11. revisar o resultado final;
12. apresentar um resumo objetivo das alterações realizadas.

---

## Formato da resposta final

Após editar o README, informe:

```markdown
## README atualizado

Principais alterações:

- reorganização das seções;
- atualização da stack tecnológica;
- inclusão das instruções de instalação;
- documentação dos comandos de testes e qualidade;
- inclusão da visão geral da arquitetura.

Pendências identificadas:

- processo de deploy ainda não está documentado no repositório;
- não foi encontrada uma licença;
- não existe `.env.example`.
```

A lista deve refletir apenas o que realmente foi alterado ou encontrado.

Não apresente como concluída uma mudança que não tenha sido aplicada.

---

## Restrições

É proibido:

* criar informações sem evidência;
* adicionar badges falsos;
* declarar cobertura não verificada;
* declarar build como aprovado sem evidência;
* expor secrets;
* substituir documentação específica por texto genérico;
* remover avisos importantes;
* alterar código-fonte fora do escopo sem necessidade;
* modificar arquivos arquiteturais apenas para fazer o README parecer correto;
* documentar comandos que não funcionam;
* declarar licença inexistente;
* utilizar links quebrados deliberadamente;
* adicionar funcionalidades futuras como se estivessem prontas;
* criar uma árvore completa e poluída do repositório;
* transformar o README em documentação técnica excessivamente detalhada.

---

## Critério de conclusão

A tarefa estará concluída quando:

1. o `README.md` existir;
2. estiver bem organizado;
3. estiver visualmente consistente;
4. representar corretamente o estado atual do projeto;
5. possuir instruções executáveis quando disponíveis;
6. não contiver informações inventadas;
7. não contiver dados sensíveis;
8. estiver coerente com o `AGENTS.md`;
9. facilitar o onboarding de novos desenvolvedores;
10. tiver passado pelo checklist de validação desta skill.
