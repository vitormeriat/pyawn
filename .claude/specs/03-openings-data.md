# Spec: Dados de Abertura

## Objetivo

Definir o formato dos dados de abertura (JSON), o schema de variação com anotações estratégicas, e a interface do loader.

## Arquivos envolvidos

- `src/pyawn/openings/loader.py`
- `src/pyawn/openings/data/*.json`

## Formato JSON

Cada arquivo representa uma abertura e contém suas variações.

```json
{
  "id": "sicilian",
  "name": "Sicilian Defense",
  "eco": "B20-B99",
  "variations": [
    {
      "id": "najdorf",
      "name": "Najdorf",
      "eco": "B90",
      "moves": ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"],
      "annotations": [
        {"after_move": 1, "text": "1.e4 — controle do centro, abre diagonal para o Bf1 e a dama."},
        {"after_move": 2, "text": "1...c5 — a Siciliana. Pretas lutam pelo centro sem espelhar o peão branco."},
        {"after_move": 10, "text": "5...a6 — o lance de Najdorf. Previne Nb5 e prepara ...b5 para expansão na ala da dama."}
      ],
      "plan": "Pretas buscam contrajogo na ala da dama com ...b5; brancas atacam no lado do rei.",
      "master_games": [
        {
          "white": "Fischer",
          "black": "Petrosian",
          "year": 1959,
          "event": "Candidates Tournament",
          "pgn": "1.e4 c5 2.Nf3 d6 ..."
        }
      ]
    }
  ]
}
```

### Campos obrigatórios por variação

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | `str` | Identificador kebab-case único dentro da abertura |
| `name` | `str` | Nome legível |
| `moves` | `list[str]` | Sequência de lances em SAN, alternando brancas/pretas |
| `plan` | `str` | Descrição do plano estratégico em 1–3 frases |

### Campos opcionais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `eco` | `str` | Código ECO |
| `annotations` | `list` | Anotações por lance (índice base-1 em `after_move`) |
| `master_games` | `list` | Partidas de referência com PGN opcional |

## Interface do loader

```python
@dataclass
class Annotation:
    after_move: int
    text: str

@dataclass
class MasterGame:
    white: str
    black: str
    year: int
    event: str
    pgn: str | None = None

@dataclass
class Variation:
    id: str
    name: str
    moves: list[str]
    plan: str
    eco: str | None = None
    annotations: list[Annotation] = field(default_factory=list)
    master_games: list[MasterGame] = field(default_factory=list)

@dataclass
class Opening:
    id: str
    name: str
    variations: list[Variation]
    eco: str | None = None

def load_opening(opening_id: str) -> Opening: ...
def list_openings() -> list[tuple[str, str]]: ...  # [(id, name), ...]
def get_variation(opening_id: str, variation_id: str) -> Variation: ...
```

## Requisitos

- Arquivos JSON ficam em `src/pyawn/openings/data/` e são incluídos como `package_data` no `pyproject.toml`
- `load_opening()` valida o JSON contra os campos obrigatórios e levanta `ValueError` com mensagem clara em caso de dado inválido
- Moves são validados com `python-chess` durante o carregamento — se a sequência produzir posição ilegal, levanta `ValueError`
- Loader é lazy: abre o arquivo na primeira chamada e armazena em cache em memória
- IDs são case-insensitive e normalizam hífens (aceitar `"ruy_lopez"` e `"ruy-lopez"` como equivalentes)

## Testes

- `tests/unit/test_openings_loader.py`
- `tests/integration/test_openings_data.py` — valida todos os JSONs do pacote
- Usar fixtures de JSON mínimos nos testes unitários (não depender dos arquivos reais)

## Critérios de aceitação

- [ ] `load_opening("sicilian")` retorna objeto `Opening` com 3 variações
- [ ] Sequência de lances inválida no JSON levanta `ValueError` com descrição do lance problemático
- [ ] `list_openings()` retorna as 5 aberturas do MVP
- [ ] Arquivo JSON com campo obrigatório ausente levanta `ValueError`
- [ ] Carregamento em cache: segundo `load_opening()` não abre o arquivo novamente
