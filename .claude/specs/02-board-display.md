# Spec: Renderização do Tabuleiro

## Objetivo

Renderizar o tabuleiro de xadrez no terminal usando Rich, de forma legível para jogadores iniciantes e intermediários.

## Arquivos envolvidos

- `src/pyawn/board/renderer.py`

## Comportamento esperado

### Layout do tabuleiro

```
    a  b  c  d  e  f  g  h
  ┌──┬──┬──┬──┬──┬──┬──┬──┐
8 │♜ │♞ │♝ │♛ │♚ │♝ │♞ │♜ │
  ├──┼──┼──┼──┼──┼──┼──┼──┤
7 │♟ │♟ │♟ │♟ │♟ │♟ │♟ │♟ │
  ├──┼──┼──┼──┼──┼──┼──┼──┤
  ...
1 │♖ │♘ │♗ │♕ │♔ │♗ │♘ │♖ │
  └──┴──┴──┴──┴──┴──┴──┴──┘
```

- Casas claras e escuras com cores de fundo alternadas
- Peças brancas: `♙♘♗♖♕♔` (U+2659–U+2654)
- Peças pretas: `♟♞♝♜♛♚` (U+265F–U+265A)
- Coordenadas de coluna (a–h) acima e abaixo; linha (1–8) à esquerda

### Orientação

- Por padrão, renderiza com as brancas na parte inferior (perspectiva das brancas)
- `render_board(board, flipped=True)` renderiza com pretas na parte inferior

### Destaque de lance

- O lance mais recente é destacado: casas de origem e destino com cor de fundo diferente (ex: `on dark_olive_green3`)
- `render_board(board, last_move=move)` recebe um `chess.Move` opcional

### Painel de informações

Abaixo do tabuleiro, exibir um painel Rich com:
- Abertura e variação atual
- Número do lance (ex: `Lance 5 — Pretas`)
- Avaliação do Stockfish em centipawns (quando disponível)

## Interface pública

```python
def render_board(
    board: chess.Board,
    console: Console,
    *,
    flipped: bool = False,
    last_move: chess.Move | None = None,
    info: dict[str, str] | None = None,
) -> None: ...
```

`info` pode conter chaves: `"opening"`, `"variation"`, `"eval"`, `"move_hint"`.

## Requisitos

- Não usar `print()` — sempre `console.print()`
- A função não deve ter efeitos colaterais além de escrever no `console`
- Deve funcionar em terminais de 80 colunas sem quebrar layout
- Sem dependências além de `rich` e `python-chess`

## Testes

- `tests/unit/test_board_renderer.py`
- Testar: posição inicial, posição com peças capturadas, tabuleiro virado, destaque de lance
- Usar `Console(file=io.StringIO())` para capturar output nos testes

## Critérios de aceitação

- [ ] Tabuleiro renderiza corretamente na posição inicial
- [ ] Lance `e2e4` resulta em destaque nas casas e2 e e4
- [ ] `flipped=True` inverte linhas e colunas corretamente
- [ ] Painel de info exibe avaliação quando `info["eval"]` está presente
- [ ] Largura total não ultrapassa 60 caracteres
