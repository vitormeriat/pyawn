# Spec: Modo Study — Aprendizado Guiado

## Objetivo

Permitir que o usuário navegue por uma abertura lance a lance, vendo o tabuleiro atualizado e lendo a anotação estratégica de cada lance.

## Arquivos envolvidos

- `src/pyawn/study/session.py`
- `src/pyawn/cli.py` (comando `study`)

## Fluxo da sessão

```
1. Usuário seleciona abertura + variação (via CLI ou menu)
2. Sistema exibe tabuleiro na posição inicial + texto introdutório da variação
3. Loop por cada lance da variação:
   a. Exibir "Próximo lance: [brancas/pretas] — digite ou pressione Enter para ver"
   b. Usuário digita o lance (SAN) ou pressiona Enter sem digitar
   c. Se digitou: validar se é o lance correto
      - Correto → exibir tabuleiro com lance destacado + anotação daquele lance
      - Errado  → exibir "Ops! O lance correto era Nf3. Tente memorizar."
                   → aplicar o lance correto e continuar
   d. Se pressionou Enter: revelar o lance, aplicar, exibir tabuleiro + anotação
4. Ao final da variação: exibir resumo do plano estratégico + partida de referência (se houver)
5. Registrar sessão no banco (abertura, variação, data, lances acertados/errados)
6. Perguntar: "Estudar outra variação? [s/N]"
```

## Interface pública

```python
class StudySession:
    def __init__(
        self,
        variation: Variation,
        console: Console,
        db: ProgressDB,
    ) -> None: ...

    def run(self) -> StudyResult: ...

@dataclass
class StudyResult:
    opening_id: str
    variation_id: str
    moves_guessed: int
    moves_revealed: int
    completed: bool
```

## Comportamento de validação de lance

- Entrada do usuário é lida com `click.prompt()`
- Lance é convertido para objeto `chess.Move` via `board.parse_san(user_input)`
- Se parse falhar (lance inválido em SAN), exibir "Lance inválido — tente novamente" e repetir prompt
- Comparar `chess.Move` do usuário com o esperado da variação
- Máximo de 3 tentativas por lance; na terceira, revelar automaticamente

## Exibição de anotações

- Após cada lance, verificar se `variation.annotations` tem entrada para aquele índice (`after_move == lance_atual`)
- Se sim, exibir em painel Rich amarelo abaixo do tabuleiro
- Se não, continuar sem painel (silencioso)

## Exibição de partida de referência

- Se a variação tem `master_games`, ao final exibir a primeira:
  ```
  ┌─ Partida de referência ────────────────────────────┐
  │ Fischer × Petrosian — Candidates Tournament, 1959  │
  │ 1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6   │
  └────────────────────────────────────────────────────┘
  ```

## Requisitos

- `StudySession` não deve importar Click — recebe `console` e `db` por injeção
- Stockfish **não é usado** neste modo
- Limpar a tela antes de renderizar cada novo estado do tabuleiro (`console.clear()`)
- Ao pressionar Ctrl+C, encerrar a sessão graciosamente e registrar progresso parcial

## Testes

- `tests/unit/test_study_session.py`
- Mockar `Console` e `ProgressDB`
- Testar: acerto no primeiro lance, erro seguido de acerto, Enter para revelar, Ctrl+C no meio

## Critérios de aceitação

- [ ] Sessão completa de Najdorf registra `StudyResult` com `completed=True`
- [ ] Lance errado incrementa `moves_revealed`, não `moves_guessed`
- [ ] Lance correto incrementa `moves_guessed`
- [ ] Três erros consecutivos revelam o lance e continuam a sessão
- [ ] Ctrl+C salva progresso parcial e exibe "Sessão encerrada."
