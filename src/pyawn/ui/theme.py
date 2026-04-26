"""Visual constants — colors, box-drawing chars, piece symbols."""

# ── Square backgrounds ────────────────────────────────────────────────────────
LIGHT_SQ = "on grey30"
DARK_SQ = "on grey15"
HIGHLIGHT_SQ = "on dark_olive_green3"   # last move
CHECK_SQ = "on dark_red"                # king in check

# ── Piece foregrounds ─────────────────────────────────────────────────────────
WHITE_PIECE = "bold bright_white"
BLACK_PIECE = "bold color(235)"         # very dark grey, distinct from both backgrounds

# ── UI palette ────────────────────────────────────────────────────────────────
ACCENT = "bold cyan"
DIM = "dim"
ERROR = "bold red"
HINT = "bold yellow"
SUCCESS = "bold green"
MUTED = "grey62"

# ── Box drawing (chs-inspired) ────────────────────────────────────────────────
BOX_H = "━"
BOX_TL = "┏"
BOX_TR = "┓"
BOX_BL = "┗"
BOX_BR = "┛"
BOX_V = "┃"

# ── Unicode chess pieces ──────────────────────────────────────────────────────
import chess  # noqa: E402

PIECE_SYMBOLS: dict[tuple[int, bool], str] = {
    (chess.PAWN,   chess.WHITE): "♙",
    (chess.KNIGHT, chess.WHITE): "♘",
    (chess.BISHOP, chess.WHITE): "♗",
    (chess.ROOK,   chess.WHITE): "♖",
    (chess.QUEEN,  chess.WHITE): "♕",
    (chess.KING,   chess.WHITE): "♔",
    (chess.PAWN,   chess.BLACK): "♟",
    (chess.KNIGHT, chess.BLACK): "♞",
    (chess.BISHOP, chess.BLACK): "♝",
    (chess.ROOK,   chess.BLACK): "♜",
    (chess.QUEEN,  chess.BLACK): "♛",
    (chess.KING,   chess.BLACK): "♚",
}
