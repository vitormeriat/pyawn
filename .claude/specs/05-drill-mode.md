# Spec: Modo Drill — Treino com Validação

## Objetivo

Testar a memória do usuário sobre uma abertura sem mostrar os lances antecipadamente. O "oponente" joga os lances da linha principal e o usuário deve responder corretamente.

## Arquivos envolvidos

- `src/pyawn/drill/session.py`
- `src/pyawn/cli.py` (comando `drill`)

## Fluxo da sessão

```
1. Usuário seleciona abertura + variação + nível de dificuldade
2. Sistema apresenta tabuleiro na posição inicial
3. Loop de lances:
   a. Lance do "oponente" (sistema): aplica automaticamente o lance da linha, exibe tabuleiro
   b. Lance do usuário: prompt "Seu lance:"
      - Correto → exibir tabuleiro com lance destacado, continuar
      - Errado  → feedback conforme nível de dificuldade (ver abaixo)
4. Ao final: exibir placar (acertos/total) e avaliação Stockfish da posição final (se disponível)
5. Registrar resultado no banco
6. Perguntar: "Treinar novamente? [s/N]"
```

## Níveis de dificuldade

### Nível 1 — Linha principal
- O sistema sempre joga os lances da linha principal
- Feedback em caso de erro: exibir o lance correto após 1 tentativa

### Nível 2 — Variações
- Em lances ímpares (oponente), o sistema pode desviar da linha principal com 30% de probabilidade
- Desvio escolhido aleatoriamente entre lances legais comuns (baseado nas variações carregadas)
- Usuário deve responder de forma plausível (qualquer lance legal é aceito neste cenário)
- Feedback: Stockfish avalia o lance do usuário e classifica como: Excelente / Bom / Imprecisão / Erro

## Interface pública

```python
class DrillSession:
    def __init__(
        self,
        variation: Variation,
        console: Console,
        db: ProgressDB,
        engine: StockfishEngine | None,
        difficulty: Literal[1, 2] = 1,
        rng: random.Random | None = None,
    ) -> None: ...

    def run(self) -> DrillResult: ...

@dataclass
class DrillResult:
    opening_id: str
    variation_id: str
    difficulty: int
    moves_correct: int
    moves_total: int
    accuracy: float        # moves_correct / moves_total
    completed: bool
    final_eval: int | None  # centipawns, None se Stockfish indisponível
```

## Feedback de erro (Nível 1)

```
✗  Lance incorreto. O lance correto era Nxd4.
   Dica: capture o peão central para ganhar controle do centro.
```

- A "dica" vem da anotação do lance, se disponível; caso contrário, omitir a linha de dica

## Feedback de lance (Nível 2, pós-desvio)

```
Stockfish: ♟ +0.3 — Bom lance!
```

Classificação por centipawns (perspectiva do jogador):

| Delta vs. melhor lance | Classificação |
|------------------------|---------------|
| 0–20 cp                | Excelente     |
| 21–50 cp               | Bom           |
| 51–100 cp              | Imprecisão    |
| > 100 cp               | Erro          |

- Se Stockfish indisponível: aceitar qualquer lance legal sem classificar

## Determinismo em testes

- `rng` injetável para controlar desvios aleatórios em testes
- `DrillSession(..., rng=random.Random(42))` garante comportamento reproduzível

## Requisitos

- `DrillSession` não deve importar Click
- Lances do oponente são aplicados automaticamente com delay visual de 0.5s (exibir "...")
- Se Stockfish não responder dentro do timeout, degradar silenciosamente
- Ctrl+C encerra a sessão e registra resultado parcial

## Testes

- `tests/unit/test_drill_session.py`
- Mockar `StockfishEngine` e `ProgressDB`
- Testar: acerto, erro nível 1, desvio nível 2, Stockfish indisponível, Ctrl+C

## Critérios de aceitação

- [ ] Sessão completa sem erros retorna `accuracy=1.0`
- [ ] Lance errado no nível 1 exibe lance correto e continua (não encerra)
- [ ] No nível 2, quando oponente desvia, qualquer lance legal do usuário é aceito
- [ ] `final_eval` é `None` quando Stockfish não está disponível
- [ ] Resultado é registrado mesmo em sessão encerrada via Ctrl+C
