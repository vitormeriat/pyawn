# Spec: CLI — Entrypoint e Navegação

## Objetivo

Definir a estrutura do CLI Click, o fluxo de navegação entre comandos e as responsabilidades de `__main__.py` e `cli.py`.

## Arquivos envolvidos

- `src/pyawn/__main__.py`
- `src/pyawn/cli.py`

## Comportamento esperado

### Entrypoint

```
python -m pyawn                 # abre menu principal interativo
python -m pyawn study           # vai direto para seleção de abertura (modo estudo)
python -m pyawn study sicilian  # vai direto para seleção de variação da Siciliana
python -m pyawn drill           # vai direto para seleção de abertura (modo treino)
python -m pyawn drill ruy-lopez # vai direto para seleção de variação do Ruy López
```

### Menu principal (sem subcomando)

Quando chamado sem argumentos, exibir menu com Rich:

```
  ♟  pyawn — Chess Opening Trainer

  [1] Study   — Aprender uma abertura
  [2] Drill   — Treinar uma abertura
  [3] Stats   — Ver progresso
  [q] Quit

  Escolha:
```

### Seleção de abertura

Quando o subcomando não recebe o argumento de abertura, exibir menu:

```
  Aberturas disponíveis:
  [1] Sicilian Defense
  [2] Ruy López
  [3] French Defense
  [4] Caro-Kann Defense
  [5] Italian Game
  [b] Voltar
```

### Seleção de variação

Cada abertura tem variações listadas dinamicamente a partir dos dados em `openings/data/`. Exemplo para Sicilian:

```
  Sicilian Defense — Variações:
  [1] Najdorf
  [2] Dragon
  [3] Scheveningen
  [b] Voltar
```

## Estrutura Click

```python
# cli.py
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx): ...

@cli.command()
@click.argument("opening", required=False)
def study(opening): ...

@cli.command()
@click.argument("opening", required=False)
def drill(opening): ...
```

## Requisitos

- `__main__.py` só contém `from pyawn.cli import cli; cli()`
- `cli.py` não contém lógica de negócio — delega para `study/session.py` e `drill/session.py`
- Todos os menus usam `click.prompt()` + `click.Choice()` ou Rich interativo — nunca `input()` puro
- IDs de abertura são normalizados para kebab-case lowercase antes de passar para os módulos (ex: `"Ruy López"` → `"ruy-lopez"`)
- Ao receber `q` ou `b`, o programa volta ao nível anterior ou encerra graciosamente

## Testes

- `tests/unit/test_cli.py` usa `click.testing.CliRunner`
- Testar: chamada sem args, chamada com abertura válida, chamada com abertura inválida, fluxo de seleção via menu

## Critérios de aceitação

- [ ] `python -m pyawn --help` lista os subcomandos
- [ ] `python -m pyawn study sicilian` inicia sessão de estudo da Siciliana sem menu intermediário
- [ ] Argumento de abertura inválido exibe erro claro e encerra com código 1
- [ ] Sem subcomando, exibe menu principal e aceita escolha do usuário
