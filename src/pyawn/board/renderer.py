import chess
from rich.console import Console
from rich.text import Text

from pyawn.ui.theme import (
    BLACK_PIECE,
    CHECK_SQ,
    DARK_SQ,
    HIGHLIGHT_SQ,
    LIGHT_SQ,
    MUTED,
    PIECE_SYMBOLS,
    WHITE_PIECE,
)

_FILES = "abcdefgh"


def _is_light(file: int, rank: int) -> bool:
    return (file + rank) % 2 == 1


def _square_bg(file: int, rank: int, highlighted: bool, in_check: bool) -> str:
    if in_check:
        return CHECK_SQ
    if highlighted:
        return HIGHLIGHT_SQ
    return LIGHT_SQ if _is_light(file, rank) else DARK_SQ


def render_board(
    board: chess.Board,
    console: Console,
    *,
    flipped: bool = False,
    last_move: chess.Move | None = None,
    info: dict[str, str] | None = None,
) -> None:
    highlight: set[int] = {last_move.from_square, last_move.to_square} if last_move else set()

    king_sq: int | None = None
    if board.is_check():
        king_sq = board.king(board.turn)

    ranks = list(range(7, -1, -1)) if not flipped else list(range(8))
    files = list(range(8)) if not flipped else list(range(7, -1, -1))

    # ── File header ───────────────────────────────────────────────────────────
    header = Text("      ")
    for f in files:
        header.append(f" {_FILES[f]} ", style=MUTED)
    console.print(header)

    # ── Ranks ─────────────────────────────────────────────────────────────────
    for rank_idx in ranks:
        label = str(rank_idx + 1)
        row = Text(f"  {label}  ")

        for file_idx in files:
            sq = chess.square(file_idx, rank_idx)
            piece = board.piece_at(sq)
            in_check = sq == king_sq
            bg = _square_bg(file_idx, rank_idx, sq in highlight, in_check)

            if piece:
                symbol = PIECE_SYMBOLS[(piece.piece_type, piece.color)]
                fg = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
                row.append(f" {symbol} ", style=f"{fg} {bg}")
            else:
                row.append("   ", style=bg)

        row.append(f"  {label}", style=MUTED)
        console.print(row)

    # ── File footer ───────────────────────────────────────────────────────────
    footer = Text("      ")
    for f in files:
        footer.append(f" {_FILES[f]} ", style=MUTED)
    console.print(footer)

    # ── Info panel ────────────────────────────────────────────────────────────
    if info:
        _render_info(console, info)


def _render_info(console: Console, info: dict[str, str]) -> None:
    console.print()
    parts: list[str] = []

    opening = info.get("opening")
    variation = info.get("variation")
    if opening:
        label = f"{opening} — {variation}" if variation else opening
        parts.append(f"[bold]{label}[/]")

    if eval_cp := info.get("eval"):
        parts.append(f"[dim]Stockfish:[/] [cyan]{eval_cp}[/]")

    if hint := info.get("move_hint"):
        parts.append(f"[yellow]Dica:[/] {hint}")

    for part in parts:
        console.print(f"  {part}")
