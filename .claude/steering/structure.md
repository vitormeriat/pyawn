---
inclusion: always
---

# Estrutura do projeto

```
pyawn/
├── src/
│   └── pyawn/
│       ├── __init__.py
│       ├── __main__.py          # python -m pyawn → Click entrypoint
│       ├── cli.py               # Grupos e comandos Click (study, drill)
│       ├── board/
│       │   └── renderer.py      # Renderização do tabuleiro com Rich
│       ├── engine/
│       │   └── stockfish.py     # Wrapper UCI — único ponto de contato com o engine
│       ├── openings/
│       │   ├── loader.py        # Carrega e indexa os dados de abertura
│       │   └── data/            # Arquivos estáticos (JSON + PGN)
│       │       ├── sicilian.json
│       │       ├── ruy-lopez.json
│       │       ├── french.json
│       │       ├── caro-kann.json
│       │       └── italian.json
│       ├── study/
│       │   └── session.py       # Lógica da sessão de estudo guiado
│       ├── drill/
│       │   └── session.py       # Lógica da sessão de treino com validação
│       └── db/
│           ├── schema.sql       # DDL — fonte de verdade do schema
│           └── progress.py      # Acesso SQLite (sem ORM)
├── tests/
│   ├── unit/                    # Testes sem I/O externo
│   └── integration/             # Testes que usam SQLite real ou fixtures PGN
├── .claude/
│   ├── specs/                   # Specs de feature — ler antes de implementar
│   └── steering/                # Contexto sempre carregado para o agente
├── pyproject.toml
└── CLAUDE.md
```

## Convenções de nomenclatura

- Módulos: `snake_case`
- Classes: `PascalCase`
- Constantes: `SCREAMING_SNAKE_CASE`
- Arquivos de dados em `openings/data/` seguem o ID da abertura (ex: `ruy-lopez.json`)
- Specs em `.claude/specs/` são prefixadas com dois dígitos para ordenação (ex: `01-cli.md`)

## Invariantes de arquitetura

- Todo acesso ao Stockfish passa por `engine/stockfish.py` — nunca instanciar `Stockfish()` diretamente em outro módulo
- Todo acesso ao SQLite passa por `db/progress.py` — nunca abrir conexão fora desse módulo
- Dados de abertura são carregados via `openings/loader.py` — nunca ler JSON/PGN diretamente em outros módulos
- `__main__.py` só importa `cli.py`; toda lógica de negócio fica fora de `cli.py`
