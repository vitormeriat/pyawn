# Spec: Wrapper do Stockfish

## Objetivo

Encapsular toda a comunicação com o engine Stockfish, garantindo timeout, degradação graciosa e isolamento do restante do código.

## Arquivos envolvidos

- `src/pyawn/engine/stockfish.py`

## Interface pública

```python
class StockfishEngine:
    def __init__(self, timeout_ms: int = 100) -> None: ...

    @classmethod
    def create(cls) -> "StockfishEngine | None":
        """Retorna None se o binary não estiver disponível."""
        ...

    def evaluate(self, board: chess.Board) -> int | None:
        """
        Avalia a posição. Retorna centipawns do ponto de vista das brancas.
        Retorna None se o engine falhar ou timeout estourar.
        """
        ...

    def best_move(self, board: chess.Board) -> chess.Move | None:
        """
        Retorna o melhor lance para a posição atual.
        Retorna None se o engine falhar ou timeout estourar.
        """
        ...

    def close(self) -> None:
        """Encerra o processo do Stockfish."""
        ...

    def __enter__(self) -> "StockfishEngine": ...
    def __exit__(self, *args: object) -> None: ...
```

## Comportamento

### Inicialização

1. `StockfishEngine.create()` chama `shutil.which("stockfish")` — se `None`, logar warning e retornar `None`
2. `__init__` recebe `timeout_ms` (padrão: `int(os.getenv("STOCKFISH_TIMEOUT", "100"))`)
3. Instanciar `stockfish.Stockfish(path=..., parameters={"Threads": 1, "Hash": 16})`

### Análise

- `evaluate()` e `best_move()` capturam qualquer exceção do pacote `stockfish` e retornam `None`
- Timeout aplicado via parâmetro `time` na chamada UCI (não via `threading`)
- Resultado de `evaluate()` normalizado: positivo = brancas melhor; negativo = pretas melhor

### Degradação graciosa

Chamadores devem sempre tratar `None` como "engine indisponível" — nunca presumir que o engine está disponível.

### Context manager

`StockfishEngine` implementa `__enter__` / `__exit__` para garantir `close()` mesmo em exceções.

## Logging

- Usar `logging.getLogger("pyawn.engine")` — nunca `print()`
- `WARNING` quando binary não encontrado
- `DEBUG` para cada chamada de análise (posição FEN + resultado)
- `ERROR` quando exceção inesperada do pacote stockfish

## Requisitos

- Nenhum outro módulo importa o pacote `stockfish` diretamente
- `StockfishEngine` é stateless entre chamadas — cada `evaluate()` prepara a posição do zero
- Thread-safe: não usar instância compartilhada entre threads sem lock (para MVP, uso single-thread é suficiente)

## Testes

- `tests/unit/test_stockfish_engine.py`
- Mockar `stockfish.Stockfish` com `unittest.mock.patch`
- Testar: binary não encontrado → `create()` retorna `None`, exceção durante análise → retorna `None`, timeout → retorna `None`, context manager fecha o engine

## Critérios de aceitação

- [ ] `StockfishEngine.create()` retorna `None` quando `stockfish` não está no PATH
- [ ] `evaluate()` retorna `None` em vez de propagar exceção
- [ ] `close()` é chamado pelo context manager mesmo após exceção
- [ ] `timeout_ms` é lido de `STOCKFISH_TIMEOUT` quando não passado explicitamente
- [ ] Nenhum `print()` no módulo — apenas logging
