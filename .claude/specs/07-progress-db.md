# Spec: Persistência de Progresso (SQLite)

## Objetivo

Registrar e consultar o histórico de sessões de estudo e treino do usuário em um banco SQLite local.

## Arquivos envolvidos

- `src/pyawn/db/schema.sql`
- `src/pyawn/db/progress.py`

## Schema

```sql
-- schema.sql

CREATE TABLE IF NOT EXISTS openings_studied (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    opening_id    TEXT    NOT NULL,
    variation_id  TEXT    NOT NULL,
    studied_at    TEXT    NOT NULL,  -- ISO 8601: "2026-04-26T14:30:00"
    moves_guessed INTEGER NOT NULL DEFAULT 0,
    moves_revealed INTEGER NOT NULL DEFAULT 0,
    completed     INTEGER NOT NULL DEFAULT 0  -- 0 ou 1
);

CREATE TABLE IF NOT EXISTS drill_results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    opening_id    TEXT    NOT NULL,
    variation_id  TEXT    NOT NULL,
    difficulty    INTEGER NOT NULL,  -- 1 ou 2
    drilled_at    TEXT    NOT NULL,  -- ISO 8601
    moves_correct INTEGER NOT NULL DEFAULT 0,
    moves_total   INTEGER NOT NULL DEFAULT 0,
    accuracy      REAL    NOT NULL DEFAULT 0.0,
    final_eval    INTEGER,           -- centipawns, NULL se indisponível
    completed     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_studied_opening  ON openings_studied(opening_id, variation_id);
CREATE INDEX IF NOT EXISTS idx_drill_opening    ON drill_results(opening_id, variation_id);
```

## Interface pública

```python
class ProgressDB:
    def __init__(self, db_path: Path | str = "~/.pyawn/progress.db") -> None: ...

    def record_study(self, result: StudyResult) -> None: ...
    def record_drill(self, result: DrillResult) -> None: ...

    def get_study_stats(self, opening_id: str) -> dict[str, Any]: ...
    def get_drill_stats(self, opening_id: str) -> dict[str, Any]: ...

    def close(self) -> None: ...
    def __enter__(self) -> "ProgressDB": ...
    def __exit__(self, *args: object) -> None: ...
```

### `get_study_stats(opening_id)` retorna

```python
{
    "total_sessions": int,
    "completed_sessions": int,
    "variations_studied": list[str],
    "avg_accuracy": float,          # moves_guessed / (moves_guessed + moves_revealed)
    "last_studied": str | None,     # ISO 8601
}
```

### `get_drill_stats(opening_id)` retorna

```python
{
    "total_sessions": int,
    "best_accuracy": float,
    "avg_accuracy": float,
    "last_drilled": str | None,
    "by_difficulty": {
        1: {"sessions": int, "avg_accuracy": float},
        2: {"sessions": int, "avg_accuracy": float},
    },
}
```

## Comportamento

### Inicialização

1. `__init__` expande `~` no path e cria o diretório pai (`~/.pyawn/`) se necessário
2. Executa `schema.sql` com `executescript()` — idempotente graças ao `IF NOT EXISTS`
3. Habilita WAL mode: `PRAGMA journal_mode=WAL`

### Migrations

- Alterações futuras ao schema geram arquivo em `src/pyawn/db/migrations/NNNN_descricao.sql`
- Migrations são aplicadas em ordem numérica na inicialização
- Rastrear migrations aplicadas em tabela `_migrations(name TEXT PRIMARY KEY, applied_at TEXT)`

### Timestamps

- Sempre armazenar em UTC: `datetime.now(timezone.utc).isoformat(timespec="seconds")`

## Testes

- `tests/unit/test_progress_db.py` — usar SQLite `:memory:` via `ProgressDB(":memory:")`
- Testar: `record_study`, `record_drill`, `get_study_stats`, `get_drill_stats`, criação do diretório, schema idempotente

## Critérios de aceitação

- [ ] `ProgressDB(":memory:")` cria todas as tabelas sem erro
- [ ] `record_study()` persiste `StudyResult` corretamente (verificar via SELECT)
- [ ] `record_drill()` persiste `DrillResult` corretamente
- [ ] `get_study_stats("sicilian")` retorna dict com estrutura esperada
- [ ] Múltiplas chamadas a `__init__` com o mesmo banco não duplicam tabelas
- [ ] `close()` é chamado pelo context manager mesmo após exceção
