---
inclusion: always
---

# Stack técnica e convenções

## Dependências principais

| Pacote | Uso | Notas |
|--------|-----|-------|
| `click` | Framework CLI | Grupos, comandos, opções, prompts interativos |
| `python-chess` | Tabuleiro, PGN, validação | `chess.Board`, `chess.pgn`, notação SAN/UCI |
| `stockfish` | Bindings UCI | Apenas via `engine/stockfish.py` |
| `rich` | Output terminal | Console, Table, Panel, Live, prompt |
| `httpx` | HTTP (offline por padrão) | Só para extração offline de dados — nunca em runtime |

## Ferramentas de desenvolvimento

```bash
ruff check .          # linting (substitui flake8 + isort)
ruff format .         # formatação (substitui black)
mypy pyawn/           # type checking
pytest                # todos os testes
pytest --cov=pyawn    # cobertura
```

## Convenções de código

- **Type hints** em todas as funções públicas — mypy deve passar sem erros
- **Docstrings** apenas em funções públicas não-óbvias; sem multi-linha desnecessária
- **Sem comentários** que explicam o "quê" — apenas o "por quê" quando não-óbvio
- Preferir `dataclass` ou `TypedDict` a dicionários soltos para dados estruturados
- Erros de negócio: exceções customizadas em `pyawn/exceptions.py`; nunca `Exception` genérica

## Click

- Entrypoint: grupo `@click.group()` em `cli.py`, importado por `__main__.py`
- Menus interativos: `click.prompt()` com `type=click.Choice()`
- Confirmações destrutivas: `click.confirm()`
- Nunca usar `sys.exit()` diretamente — usar `ctx.exit()` ou deixar Click tratar

## python-chess

- Posições representadas como `chess.Board`
- Lances em SAN (`board.push_san()`) — entrada do usuário
- PGN parseado com `chess.pgn.read_game()`
- Validação: `board.is_legal(move)` antes de aplicar qualquer lance externo

## Rich

- Um único `Console()` global instanciado em `cli.py` e passado para os módulos
- Tabuleiro: renderizado com caracteres Unicode de peças de xadrez (♙♘♗♖♕♔)
- Cores: peças brancas em `white`, pretas em `black`; casas claras/escuras alternando `on grey23`/`on grey50`
- Progresso: `rich.progress.Progress` para animações de carregamento
- Erros do usuário: `[red]`; dicas: `[yellow]`; acertos: `[green]`

## SQLite

- Schema definido em `db/schema.sql` — é a fonte de verdade
- Conexão aberta com `sqlite3.connect(path, check_same_thread=False)`
- Migrations explícitas: cada alteração de schema gera um arquivo `db/migrations/NNNN_descricao.sql`
- Sem ORM — SQL puro com parâmetros nomeados (`:param`) para evitar SQL injection
- Path do banco: `~/.pyawn/progress.db` (criado automaticamente na primeira execução)

## Stockfish

- Timeout padrão: 100ms (env `STOCKFISH_TIMEOUT` sobrescreve)
- Verificar disponibilidade do binary antes de inicializar: `shutil.which("stockfish")`
- Em caso de falha, logar warning e operar em modo degradado (sem avaliação de centipawns)
- Nunca bloquear o event loop principal esperando análise — usar timeout agressivo

## Pytest

- Fixtures em `tests/conftest.py`
- Testes unitários em `tests/unit/` — sem I/O, sem Stockfish real
- Testes de integração em `tests/integration/` — SQLite em memória (`:memory:`), fixtures PGN locais
- Mockar Stockfish com `unittest.mock.MagicMock` em testes unitários
- Nomear testes: `test_<módulo>_<comportamento>_<cenário>`
