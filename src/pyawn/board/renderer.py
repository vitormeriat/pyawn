"""
Board renderer — layout inspirado no chs / python-chess SVG.

Colunas lado a lado:
  [rank label + 8 squares × 3 chars]  [gap]  [eval bar]  [info panel]
"""
import math

import chess
from rich.console import Console
from rich.text import Text

# ── Square colours (python-chess SVG defaults) ────────────────────────────────
_LIGHT     = "#f0d9b5"
_DARK      = "#b58863"
_HL_LIGHT  = "#cdd26a"
_HL_DARK   = "#aaa23a"
_CHECK     = "#ff6b6b"

# ── Eval bar ──────────────────────────────────────────────────────────────────
_EVAL_WHITE = "#e8e8e8"
_EVAL_BLACK = "#1c1c1c"

# ── Piece colours — white=bright white, black=pure black ─────────────────────
_WP_FG = "bold #ffffff"
_BP_FG = "bold #1a1a1a"

_SQ_W = 3   # chars per square: " P " or "   "

_PIECE_VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
              chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

SYMBOLS: dict[tuple[int, bool], str] = {
    (chess.PAWN,   True ): "♟", (chess.PAWN,   False): "♟", #♙
    (chess.KNIGHT, True ): "♞", (chess.KNIGHT, False): "♞", #♘
    (chess.BISHOP, True ): "♝", (chess.BISHOP, False): "♝", #♗
    (chess.ROOK,   True ): "♜", (chess.ROOK,   False): "♜", #♖
    (chess.QUEEN,  True ): "♛", (chess.QUEEN,  False): "♛", #♕
    (chess.KING,   True ): "♚", (chess.KING,   False): "♚", #♔
}

_FILES = "abcdefgh"

# ─────────────────────────────────────────────────────────────────────────────

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
    """
    info = info or {}

    highlight: set[int] = (
        {last_move.from_square, last_move.to_square} if last_move else set()
    )
    king_sq = board.king(board.turn) if board.is_check() else None

    ranks = list(range(7, -1, -1)) if not flipped else list(range(8))
    files = list(range(8))         if not flipped else list(range(7, -1, -1))

    captured  = _get_captured(board)
    adv       = _material_adv(captured)
    history   = _format_history(board)
    eval_cp   = _parse_eval(info.get("eval"))
    ratio     = _eval_to_ratio(eval_cp)
    n_black   = 8 - round(ratio * 8)

    info_lines = _build_info_lines(captured, adv, history, info, eval_cp)

    # ── Header ────────────────────────────────────────────────────────────────
    turn_label = "White to move" if board.turn == chess.WHITE else "Black to move"
    # board_w = rank-label (2) + 8 squares × _SQ_W
    board_w = 2 + 8 * _SQ_W
    fill = "─" * (board_w - len(turn_label) - 4)
    console.print(
        Text.assemble(
            ("  ┌─ ", "cyan"),
            (turn_label, "bold"),
            (f" {fill}┐", "cyan"),
        )
    )

    # ── Board rows ────────────────────────────────────────────────────────────
    for row_i, rank_idx in enumerate(ranks):
        row = Text()
        row.append("  ")   # left margin

        # Rank label: plain text, no background colour
        row.append(f"{rank_idx + 1} ")

        # Squares — all 64 cells have the light/dark checkered background
        for file_idx in files:
            sq = chess.square(file_idx, rank_idx)
            piece = board.piece_at(sq)
            bg = _sq_bg(file_idx, rank_idx, sq in highlight, sq == king_sq)
            if piece:
                fg = _WP_FG if piece.color == chess.WHITE else _BP_FG
                sym = SYMBOLS[(piece.piece_type, piece.color)]
                row.append(f" {sym} ", style=f"{fg} on {bg}")
            else:
                row.append(" " * _SQ_W, style=f"on {bg}")

        # Gap between board and eval bar
        row.append("   ")

        # Eval bar (2-char wide)
        eval_bg = _EVAL_BLACK if row_i < n_black else _EVAL_WHITE
        row.append("  ", style=f"on {eval_bg}")

        # Info panel
        row.append("  ")
        row.append_text(info_lines[row_i])

        console.print(row)

    # ── File labels + white's captured pieces ─────────────────────────────────
    file_row = Text("    ")   # 2 margin + 2 rank-label
    for f in files:
        file_row.append(f" {_FILES[f]} ", style="dim")
    file_row.append("   ")   # gap + eval bar placeholder
    wcap = _captured_str(captured[chess.WHITE], chess.BLACK)
    adv_w = adv[chess.WHITE]
    file_row.append(f"  {wcap}", style="dim")
    if adv_w > 0:
        file_row.append(f" +{adv_w}", style="dim")
    console.print(file_row)
    console.print()


# ── Info panel ────────────────────────────────────────────────────────────────

def _build_info_lines(
    captured: dict[bool, list[int]],
    adv: dict[bool, int],
    history: list[tuple[int, str, str]],
    info: dict[str, str],
    eval_cp: int | None,
) -> list[Text]:
    """Return exactly 8 Text objects aligned with ranks 8 → 1."""
    lines: list[Text] = [Text() for _ in range(8)]

    black_name = info.get("black_name", "Black")
    white_name = info.get("white_name", "White")

    # Row 0 (rank 8): black player
    lines[0].append("● ", style="green")
    lines[0].append(black_name, style="bold")

    # Row 1 (rank 7): black's captured pieces
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
        if b:
            lines[2 + i].append(f"  {b}", style="bold")

    # Row 5: eval
    if eval_cp is not None:
        wp = info.get("wp", "")
        lines[5].append("  ")
        if wp:
            lines[5].append(f"wp:{wp}%  ", style="dim")
        lines[5].append(f"cp:{eval_cp:+d}", style="dim")

    # Row 7 (rank 1): white player
    lines[7].append("● ", style="green")
    lines[7].append(white_name, style="bold")

    return lines


# ── Square helpers ────────────────────────────────────────────────────────────

def _is_light(file: int, rank: int) -> bool:
    return (file + rank) % 2 == 1

def _sq_bg(file: int, rank: int, highlighted: bool, in_check: bool) -> str:
    if in_check:
        return _CHECK
    if highlighted:
        return _HL_LIGHT if _is_light(file, rank) else _HL_DARK
    return _LIGHT if _is_light(file, rank) else _DARK


# ── Data helpers ──────────────────────────────────────────────────────────────

def _get_captured(board: chess.Board) -> dict[bool, list[int]]:
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
        num = i // 2 + 1
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
        pairs.append((num, w, b))
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
