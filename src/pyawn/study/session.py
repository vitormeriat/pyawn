"""Study mode — guides the user through an opening variation move by move."""
from __future__ import annotations

from dataclasses import dataclass

import chess
from rich.console import Console
from rich.panel import Panel

from pyawn.board.renderer import render_board
from pyawn.openings.loader import Annotation, Variation

_MAX_ATTEMPTS = 3


@dataclass
class StudyResult:
    opening_id: str
    variation_id: str
    moves_guessed: int
    moves_revealed: int
    completed: bool


class StudySession:
    def __init__(
        self,
        opening_id: str,
        variation: Variation,
        console: Console,
    ) -> None:
        self._opening_id = opening_id
        self._variation = variation
        self._console = console

    def run(self) -> StudyResult:
        board = chess.Board()
        variation = self._variation
        moves_guessed = 0
        moves_revealed = 0

        try:
            self._render(board)
            self._console.print(f"  [bold cyan]{variation.name}[/]")
            self._console.print(f"  [dim]{variation.plan}[/]\n")
            self._console.input("  Pressione Enter para começar... ")

            for move_idx, san in enumerate(variation.moves):
                expected = board.parse_san(san)
                is_white = board.turn == chess.WHITE
                side = "Brancas" if is_white else "Pretas"
                move_num = move_idx // 2 + 1
                dots = "." if is_white else "..."

                self._render(board, progress=move_idx)
                guessed = self._prompt_move(side, move_num, dots, board, expected, san)

                if guessed:
                    moves_guessed += 1
                else:
                    moves_revealed += 1

                board.push(expected)
                annotation = self._annotation_for(move_idx + 1)
                self._render(board, last_move=expected, progress=move_idx + 1)

                if annotation:
                    self._console.print(
                        Panel(annotation.text, border_style="yellow", padding=(0, 2))
                    )
                    self._console.print()

                self._console.input("  Enter para continuar... ")

        except (KeyboardInterrupt, EOFError):
            self._console.print("\n  [dim]Sessão encerrada.[/]\n")
            return StudyResult(
                opening_id=self._opening_id,
                variation_id=variation.id,
                moves_guessed=moves_guessed,
                moves_revealed=moves_revealed,
                completed=False,
            )

        self._render(board, progress=len(variation.moves))
        self._show_summary(moves_guessed, moves_revealed)
        return StudyResult(
            opening_id=self._opening_id,
            variation_id=variation.id,
            moves_guessed=moves_guessed,
            moves_revealed=moves_revealed,
            completed=True,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _render(
        self,
        board: chess.Board,
        *,
        last_move: chess.Move | None = None,
        progress: int | None = None,
    ) -> None:
        self._console.clear()
        self._console.print()
        total = len(self._variation.moves)
        prog_str = f"  [dim]({progress}/{total} lances)[/]" if progress is not None else ""
        self._console.print(
            f"  [bold]{self._variation.name}[/]{prog_str}\n"
        )
        render_board(
            board,
            self._console,
            last_move=last_move,
            info={"white_name": "Brancas", "black_name": "Pretas"},
        )

    def _prompt_move(
        self,
        side: str,
        move_num: int,
        dots: str,
        board: chess.Board,
        expected: chess.Move,
        san: str,
    ) -> bool:
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            prefix = f"  [dim]({attempt}/{_MAX_ATTEMPTS})[/] " if attempt > 1 else "  "
            raw = self._console.input(
                f"{prefix}[bold]{side}[/] {move_num}{dots} › "
            ).strip()

            if not raw:
                self._console.print(f"  [dim]Lance: [bold]{san}[/][/]\n")
                return False

            try:
                user_move = board.parse_san(raw)
            except Exception:
                self._console.print("  [red]Lance inválido — tente novamente.[/]")
                continue

            if user_move == expected:
                self._console.print("  [green]✓[/]\n")
                return True

            if attempt < _MAX_ATTEMPTS:
                self._console.print("  [red]✗ — tente novamente.[/]")
            else:
                self._console.print(
                    f"  [red]✗ — o lance correto era [bold]{san}[/].[/]\n"
                )

        return False

    def _annotation_for(self, after_move: int) -> Annotation | None:
        for ann in self._variation.annotations:
            if ann.after_move == after_move:
                return ann
        return None

    def _show_summary(self, guessed: int, revealed: int) -> None:
        total = guessed + revealed
        pct = int(guessed / total * 100) if total else 0
        variation = self._variation

        self._console.print(f"  [bold green]Variação concluída![/]")
        self._console.print(f"  Acertos: [bold]{guessed}/{total}[/] ({pct}%)\n")
        self._console.print(f"  [dim]{variation.plan}[/]")

        if variation.master_games:
            g = variation.master_games[0]
            pgn_line = f"\n{g.pgn}" if g.pgn else ""
            self._console.print(
                Panel(
                    f"[bold]{g.white} × {g.black}[/]  [dim]{g.event}, {g.year}[/]{pgn_line}",
                    title="Partida de referência",
                    border_style="cyan",
                    padding=(0, 2),
                )
            )

        self._console.print()
