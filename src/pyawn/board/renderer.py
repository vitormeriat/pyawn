"""
Board renderer — layout inspirado no chs / python-chess SVG.

Colunas lado a lado:
  [rank label + 8 squares]  [eval bar 2-char]  [info panel]
"""
import math
from typing import NamedTuple

import chess
from rich.console import Console
from rich.text import Text

# ── Square colours (python-chess SVG defaults) ────────────────────────────────
_LIGHT       = "#f0d9b5"
_DARK        = "#b58863"
_HL_LIGHT    = "#cdd26a"   # last-move highlight, light square
_HL_DARK     = "#aaa23a"   # last-move highlight, dark square
_CHECK       = "#ff6b6b"   # king-in-check overlay

# ── Eval bar ──────────────────────────────────────────────────────────────────
_EVAL_WHITE  = "#e8e8e8"
_EVAL_BLACK  = "#1c1c1c"

# ── Piece colours ─────────────────────────────────────────────────────────────
_WP_FG = "bold #ffffff"
_BP_FG = "bold #1a1a1a"

# ── Chess symbols ─────────────────────────────────────────────────────────────
SYMBOLS: dict[tuple[int, bool], str] = {
    (chess.PAWN,   True ): "♙", (chess.PAWN,   False): "♟",
    (chess.KNIGHT, True ): "♘", (chess.KNIGHT, False): "♞",
    (chess.BISHOP, True ): "♗", (chess.BISHOP, False): "♝",
    (chess.ROOK,   True ): "♖", (chess.ROOK,   False): "♜",
    (chess.QUEEN,  True ): "♕", (chess.QUEEN,  False): "♛",
    (chess.KING,   True ): "♔", (chess.KING,   False): "♚",
}

_PIECE_VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
              chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

_FILES = "abcdefgh"

# ── Public entry point ────────────────────────────────────────────────────────

def render_board(
    board: chess.Board,
    console: Console,
    *,
    flipped: bool = False,
    last_move: chess.Move | None = None,
    info: dict[str, str] | None = None,
) -> None:
    """
    Render the board with eval bar and info panel side by side.

    info keys (all optional):
      white_name, black_name  — player labels
      eval                    — centipawn int/str (e.g. 56 or "+56")
      wp                      — win probability 0-100 (white's perspective)
      opening, variation      — shown in the prompt area
    """
    info = info or {}

    highlight: set[int] = (
        {last_move.from_square, last_move.to_square} if last_move else set()
    )
    king_sq = board.king(board.turn) if board.is_check() else None

    ranks = list(range(7, -1, -1)) if not flipped else list(range(8))
    files = list(range(8))         if not flipped else list(range(7, -1, -1))

    captured = _get_captured(board)
    adv      = _material_adv(captured)
    history  = _format_history(board)
    eval_cp  = _parse_eval(info.get("eval"))
    ratio    = _eval_to_ratio(eval_cp)
    n_black  = 8 - round(ratio * 8)   # rows from top that are "black's"

    info_lines = _build_info_lines(board, info, captured, adv, history, eval_cp)

    white_name = info.get("white_name", "White")
    black_name = info.get("black_name", "Black")

    # ── Header: turn indicator ────────────────────────────────────────────────
    turn_label = "White to move" if board.turn == chess.WHITE else "Black to move"
    board_w = 2 + 8 * 3  # rank-label (2) + 8 squares × 3 chars
    console.print(
        Text.assemble(
            ("  ┌─ ", "cyan"),
            (turn_label, "bold white"),
            (" " + "─" * (board_w - len(turn_label) - 4) + "┐", "cyan"),
        )
    )

    # ── Board rows ────────────────────────────────────────────────────────────
    for row_i, rank_idx in enumerate(ranks):
        # Board squares
        board_row = Text(f"  {rank_idx + 1} ")
        for file_idx in files:
            sq = chess.square(file_idx, rank_idx)
            piece = board.piece_at(sq)
            bg = _sq_bg(file_idx, rank_idx, sq in highlight, sq == king_sq)
            if piece:
                fg = _WP_FG if piece.color == chess.WHITE else _BP_FG
                sym = SYMBOLS[(piece.piece_type, piece.color)]
                board_row.append(f" {sym} ", style=f"{fg} {bg}")
            else:
                board_row.append("   ", style=f"on {bg}")

        # Eval bar (2-char wide cell)
        eval_bg = _EVAL_BLACK if row_i < n_black else _EVAL_WHITE
        eval_cell = Text("  ", style=f"on {eval_bg}")

        # Combine on one line
        combined = Text()
        combined.append_text(board_row)
        combined.append_text(eval_cell)
        combined.append("  ")
        combined.append_text(info_lines[row_i])
        console.print(combined)

    # ── File labels + bottom info ─────────────────────────────────────────────
    file_row = Text("     ")
    for f in files:
        file_row.append(f" {_FILES[f]} ", style="dim")
    file_row.append("  ")   # align with eval bar gap
    # White's captured pieces on footer line
    wcap = _captured_str(captured[chess.WHITE], chess.BLACK)
    adv_w = adv[chess.WHITE]
    file_row.append(f"  {wcap}", style="dim")
    if adv_w > 0:
        file_row.append(f" +{adv_w}", style="dim")
    console.print(file_row)
    console.print()


# ── Info panel builder ────────────────────────────────────────────────────────

def _build_info_lines(
    board: chess.Board,
    info: dict[str, str],
    captured: dict[bool, list[int]],
    adv: dict[bool, int],
    history: list[tuple[int, str, str]],
    eval_cp: int | None,
) -> list[Text]:
    """Return exactly 8 Text objects, one per rank row (rank 8 → rank 1)."""
    lines: list[Text] = [Text() for _ in range(8)]

    black_name = info.get("black_name", "Black")
    white_name = info.get("white_name", "White")

    # Row 0: black player name
    lines[0].append("● ", style="green")
    lines[0].append(black_name, style="bold")

    # Row 1: black's captured pieces + advantage
    bcap = _captured_str(captured[chess.BLACK], chess.WHITE)
    adv_b = adv[chess.BLACK]
    lines[1].append("  ")
    if bcap:
        lines[1].append(bcap)
        if adv_b > 0:
            lines[1].append(f" +{adv_b}", style="dim")

    # Rows 2-4: move history (last 3 pairs)
    for i, (num, w, b) in enumerate(history[-3:]):
        lines[2 + i].append(f"  {num}.", style="dim")
        lines[2 + i].append(f"  {w:<7}")
        lines[2 + i].append(f"  {b}", style="bold")

    # Row 5: eval info
    if eval_cp is not None:
        wp = info.get("wp", "")
        lines[5].append("  ")
        if wp:
            lines[5].append(f"wp:{wp}%  ", style="dim")
        lines[5].append(f"cp:{eval_cp:+d}", style="dim")

    # Row 7: white player name
    lines[7].append("● ", style="green")
    lines[7].append(white_name, style="bold")

    return lines


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sq_bg(file: int, rank: int, highlighted: bool, in_check: bool) -> str:
    if in_check:
        return _CHECK
    light = (file + rank) % 2 == 1
    if highlighted:
        return _HL_LIGHT if light else _HL_DARK
    return _LIGHT if light else _DARK


def _get_captured(board: chess.Board) -> dict[bool, list[int]]:
    """Returns {capturing_color: [piece_types_captured]}."""
    initial = chess.Board()
    result: dict[bool, list[int]] = {chess.WHITE: [], chess.BLACK: []}
    for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for color in [chess.WHITE, chess.BLACK]:
            missing = len(initial.pieces(pt, color)) - len(board.pieces(pt, color))
            if missing > 0:
                result[not color].extend([pt] * missing)
    return result


def _material_adv(captured: dict[bool, list[int]]) -> dict[bool, int]:
    adv: dict[bool, int] = {}
    for color in [chess.WHITE, chess.BLACK]:
        gained = sum(_PIECE_VAL[pt] for pt in captured[color])
        lost   = sum(_PIECE_VAL[pt] for pt in captured[not color])
        adv[color] = max(0, gained - lost)
    return adv


def _captured_str(pieces: list[int], piece_color: bool) -> str:
    if not pieces:
        return ""
    ordered = sorted(pieces, key=lambda p: _PIECE_VAL[p], reverse=True)
    return " ".join(SYMBOLS[(pt, piece_color)] for pt in ordered)


def _format_history(board: chess.Board, max_pairs: int = 3) -> list[tuple[int, str, str]]:
    temp = chess.Board()
    pairs: list[tuple[int, str, str]] = []
    half_moves = list(board.move_stack)
    i = 0
    while i < len(half_moves):
        move_num = i // 2 + 1
        try:
            w = temp.san(half_moves[i]); temp.push(half_moves[i])
        except Exception:
            w = "?"
        b = ""
        if i + 1 < len(half_moves):
            try:
                b = temp.san(half_moves[i + 1]); temp.push(half_moves[i + 1])
            except Exception:
                b = "?"
        pairs.append((move_num, w, b))
        i += 2
    return pairs[-max_pairs:]


def _parse_eval(val: str | int | None) -> int | None:
    if val is None:
        return None
    try:
        return int(str(val).replace("+", ""))
    except ValueError:
        return None


def _eval_to_ratio(cp: int | None) -> float:
    if cp is None:
        return 0.5
    return 1.0 / (1.0 + math.exp(-cp / 400.0))
