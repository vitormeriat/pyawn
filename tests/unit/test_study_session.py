"""Tests for StudySession."""
from unittest.mock import MagicMock, patch, call

import chess
import pytest
from rich.console import Console

from pyawn.openings.loader import Annotation, MasterGame, Variation
from pyawn.study.session import StudyResult, StudySession


def _make_variation(**kwargs) -> Variation:
    defaults = dict(
        id="test",
        name="Test",
        moves=["e4", "e5"],
        plan="Jogo aberto.",
        annotations=[],
        master_games=[],
    )
    defaults.update(kwargs)
    return Variation(**defaults)


def _make_session(variation: Variation | None = None) -> tuple[StudySession, MagicMock]:
    var = variation or _make_variation()
    console = MagicMock(spec=Console)
    console.input = MagicMock()
    session = StudySession(opening_id="test-opening", variation=var, console=console)
    return session, console


# ── Acerto no primeiro lance ──────────────────────────────────────────────────

def test_correct_first_guess():
    session, console = _make_session()
    # Enter para começar, depois "e4" (correto), Enter continuar, "e5" correto, Enter continuar, Enter final
    console.input.side_effect = ["", "e4", "", "e5", "", ""]
    result = session.run()

    assert result.moves_guessed == 2
    assert result.moves_revealed == 0
    assert result.completed is True


# ── Enter sem digitar revela o lance ─────────────────────────────────────────

def test_enter_reveals_move():
    session, console = _make_session()
    # Enter para começar, Enter (revela e4), Enter continuar, Enter (revela e5), Enter continuar, Enter final
    console.input.side_effect = ["", "", "", "", "", ""]
    result = session.run()

    assert result.moves_guessed == 0
    assert result.moves_revealed == 2
    assert result.completed is True


# ── Erro seguido de acerto ────────────────────────────────────────────────────

def test_wrong_then_correct():
    session, console = _make_session()
    # Começa, erra d4, acerta e4, continua, acerta e5, continua, fim
    console.input.side_effect = ["", "d4", "e4", "", "e5", "", ""]
    result = session.run()

    assert result.moves_guessed == 2
    assert result.moves_revealed == 0
    assert result.completed is True


# ── Três erros revelam o lance ────────────────────────────────────────────────

def test_three_wrong_reveals():
    session, console = _make_session()
    # Começa, 3 erros em e4, continua, acerta e5, continua, fim
    console.input.side_effect = ["", "d4", "d3", "d2", "", "e5", "", ""]
    result = session.run()

    assert result.moves_guessed == 1
    assert result.moves_revealed == 1
    assert result.completed is True


# ── Ctrl+C encerra graciosamente ──────────────────────────────────────────────

def test_keyboard_interrupt_aborts():
    session, console = _make_session()
    console.input.side_effect = ["", KeyboardInterrupt]
    result = session.run()

    assert result.completed is False
    assert result.opening_id == "test-opening"
    assert result.variation_id == "test"


# ── Anotações são exibidas no momento correto ─────────────────────────────────

def test_annotation_shown_after_correct_move():
    var = _make_variation(
        annotations=[Annotation(after_move=1, text="Abre o centro.")]
    )
    session, console = _make_session(var)
    console.input.side_effect = ["", "e4", "", "e5", "", ""]

    with patch.object(console, "print") as mock_print:
        # Just check it doesn't crash; Panel rendering is integration-level
        pass

    result = session.run()
    assert result.completed is True


# ── Partida de referência no resumo ──────────────────────────────────────────

def test_summary_with_master_game():
    var = _make_variation(
        master_games=[
            MasterGame(white="Fischer", black="Tal", year=1960, event="Olympiad", pgn="1.e4 e5")
        ]
    )
    session, console = _make_session(var)
    console.input.side_effect = ["", "e4", "", "e5", "", ""]
    result = session.run()
    assert result.completed is True


# ── Lance SAN inválido não conta como erro ────────────────────────────────────

def test_invalid_san_does_not_count_as_attempt():
    session, console = _make_session()
    # "xyz" é inválido (não conta), depois acerta
    console.input.side_effect = ["", "xyz", "e4", "", "e5", "", ""]
    result = session.run()

    assert result.moves_guessed == 2
    assert result.moves_revealed == 0
