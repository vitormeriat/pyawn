import sys

import chess
import click
from rich.console import Console
from rich.text import Text

from pyawn.board.renderer import render_board
from pyawn.openings.loader import (
    OpeningStub,
    VariationStub,
    get_opening,
    has_study_data,
    list_openings,
    load_variation,
)
from pyawn.study.session import StudySession
from pyawn.ui.theme import ACCENT, BOX_BL, BOX_BR, BOX_H, BOX_TL, BOX_TR, BOX_V, MUTED

console = Console()

_BOX_WIDTH = 36


# ── Box drawing helpers ───────────────────────────────────────────────────────

def _box_top(label: str = "") -> str:
    fill = BOX_H * (_BOX_WIDTH - len(label) - 3)
    return f"{BOX_TL}{BOX_H} {label} {fill}{BOX_TR}"


def _box_bottom() -> str:
    return f"{BOX_BL}{BOX_H * _BOX_WIDTH}{BOX_BR}"


def _print_box(label: str, lines: list[str]) -> None:
    console.print(f"  [cyan]{_box_top(label)}[/]")
    for line in lines:
        console.print(f"  [cyan]{BOX_V}[/]  {line}")
    console.print(f"  [cyan]{_box_bottom()}[/]")


def _prompt_box(label: str = "Escolha") -> str:
    console.print(f"\n  [cyan]{_box_top(label)}[/]")
    value = console.input(f"  [cyan]{BOX_V}[/]  [bold]›[/] ")
    console.print(f"  [cyan]{_box_bottom()}[/]")
    return value.strip()


def _menu_item(key: str, label: str, note: str = "") -> None:
    """Print a menu option using Text to avoid Rich treating [b] as bold."""
    t = Text()
    t.append(f"  [{key}]", style="bold cyan")
    t.append(f"  {label}")
    if note:
        t.append(f"  {note}", style=MUTED)
    console.print(t)


# ── Header ────────────────────────────────────────────────────────────────────

def _print_header() -> None:
    console.clear()
    console.print()
    _print_box("pyawn", [
        "[bold]♟  Chess Opening Trainer[/]",
        f"[{MUTED}]Estude e treine aberturas de xadrez[/]",
    ])
    console.print()


# ── Opening / variation menus ─────────────────────────────────────────────────

def _select_opening() -> OpeningStub | None:
    openings = list_openings()
    _print_header()

    console.print(f"  [{ACCENT}]Aberturas disponíveis[/]\n")
    for i, op in enumerate(openings, 1):
        _menu_item(str(i), op.name, op.eco)
    console.print()
    _menu_item("b", "Voltar")

    choice = _prompt_box()
    if choice.lower() == "b":
        return None
    if choice.isdigit() and 1 <= int(choice) <= len(openings):
        return openings[int(choice) - 1]

    console.print("\n  [red]Opção inválida.[/]")
    return _select_opening()


def _select_variation(opening: OpeningStub) -> VariationStub | None:
    _print_header()
    console.print(f"  [{ACCENT}]{opening.name}[/] [dim]—[/] [bold]Variações[/]\n")

    for i, v in enumerate(opening.variations, 1):
        _menu_item(str(i), v.name)
    console.print()
    _menu_item("b", "Voltar")

    choice = _prompt_box()
    if choice.lower() == "b":
        return None
    if choice.isdigit() and 1 <= int(choice) <= len(opening.variations):
        return opening.variations[int(choice) - 1]

    console.print("\n  [red]Opção inválida.[/]")
    return _select_variation(opening)


# ── Mode runners ─────────────────────────────────────────────────────────────

def _run_study(opening: OpeningStub, variation: VariationStub) -> None:
    if not has_study_data(opening.id):
        console.clear()
        console.print()
        _print_box("Em breve", [
            f"[{MUTED}]Dados de estudo para[/] [bold]{opening.name}[/] [dim]ainda não disponíveis.[/]",
        ])
        console.print()
        console.input("  Pressione Enter para voltar... ")
        return

    try:
        var = load_variation(opening.id, variation.id)
    except ValueError as exc:
        console.print(f"\n  [red]{exc}[/]\n")
        console.input("  Pressione Enter para voltar... ")
        return

    StudySession(opening_id=opening.id, variation=var, console=console).run()


def _show_board_preview(opening: OpeningStub, variation: VariationStub) -> None:
    console.clear()
    console.print()
    console.print(
        f"  [bold]{opening.name}[/] [dim]·[/] [cyan]{variation.name}[/]"
        f"  [dim](DRILL)[/]\n"
    )
    render_board(chess.Board(), console, info={
        "opening": opening.name,
        "variation": variation.name,
    })
    console.print()
    _print_box("Em breve", [
        f"[{MUTED}]Modo drill ainda não implementado.[/]",
    ])
    console.print()
    console.input("  Pressione Enter para voltar... ")


# ── CLI ───────────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        _main_menu()


@cli.command()
@click.argument("opening_id", required=False, metavar="ABERTURA")
def study(opening_id: str | None) -> None:
    """Modo estudo — navegue por uma abertura lance a lance."""
    _run_mode("study", opening_id)


@cli.command()
@click.argument("opening_id", required=False, metavar="ABERTURA")
def drill(opening_id: str | None) -> None:
    """Modo treino — reproduza a abertura de memória."""
    _run_mode("drill", opening_id)


def _run_mode(mode: str, opening_id: str | None) -> None:
    if opening_id:
        opening = get_opening(opening_id)
        if not opening:
            console.print(f"\n  [red]Abertura '[bold]{opening_id}[/]' não encontrada.[/]\n")
            sys.exit(1)
    else:
        opening = _select_opening()
        if not opening:
            return

    variation = _select_variation(opening)
    if not variation:
        return

    if mode == "study":
        _run_study(opening, variation)
    else:
        _show_board_preview(opening, variation)


# ── Main menu ─────────────────────────────────────────────────────────────────

def _main_menu() -> None:
    while True:
        _print_header()

        _menu_item("1", "study", "Aprender aberturas")
        _menu_item("2", "drill", "Treinar linha")
        _menu_item("3", "stats", "Ver progresso  (em breve)")
        console.print()
        _menu_item("q", "Quit")

        choice = _prompt_box()

        if choice == "1":
            _run_mode("study", None)
        elif choice == "2":
            _run_mode("drill", None)
        elif choice == "3":
            console.print(f"\n  [{MUTED}]Stats ainda não implementado.[/]")
            console.input("  Pressione Enter para continuar... ")
        elif choice.lower() == "q":
            console.print(f"\n  [{MUTED}]Até logo! ♟[/]\n")
            break
        else:
            console.print("\n  [red]Opção inválida.[/]")
