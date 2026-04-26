"""Tests for the opening data loader."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from pyawn.openings.loader import (
    Opening,
    Variation,
    Annotation,
    get_opening,
    has_study_data,
    list_openings,
    load_variation,
    _parse_opening,
    _parse_variation,
    _normalize,
)

_MINIMAL_VARIATION = {
    "id": "test-var",
    "name": "Test Variation",
    "moves": ["e4", "e5"],
    "plan": "Centro aberto.",
}

_MINIMAL_OPENING = {
    "id": "test",
    "name": "Test Opening",
    "variations": [_MINIMAL_VARIATION],
}


# ── _normalize ────────────────────────────────────────────────────────────────

def test_normalize_lowercase():
    assert _normalize("Sicilian") == "sicilian"

def test_normalize_underscores():
    assert _normalize("ruy_lopez") == "ruy-lopez"

def test_normalize_mixed():
    assert _normalize("Ruy_Lopez") == "ruy-lopez"


# ── list_openings ─────────────────────────────────────────────────────────────

def test_list_openings_returns_five():
    openings = list_openings()
    assert len(openings) == 5

def test_list_openings_contains_sicilian():
    ids = [op.id for op in list_openings()]
    assert "sicilian" in ids

def test_list_openings_have_variations():
    for op in list_openings():
        assert len(op.variations) > 0


# ── get_opening ───────────────────────────────────────────────────────────────

def test_get_opening_found():
    op = get_opening("sicilian")
    assert op is not None
    assert op.name == "Sicilian Defense"

def test_get_opening_case_insensitive():
    op = get_opening("Sicilian")
    assert op is not None
    assert op.id == "sicilian"

def test_get_opening_underscore():
    op = get_opening("ruy_lopez")
    assert op is not None
    assert op.id == "ruy-lopez"

def test_get_opening_not_found():
    assert get_opening("nimzo-indian") is None


# ── has_study_data ────────────────────────────────────────────────────────────

def test_has_study_data_sicilian():
    assert has_study_data("sicilian") is True

def test_has_study_data_ruy_lopez():
    assert has_study_data("ruy-lopez") is False

def test_has_study_data_unknown():
    assert has_study_data("nimzo-indian") is False


# ── _parse_variation ──────────────────────────────────────────────────────────

def test_parse_variation_minimal():
    var = _parse_variation(_MINIMAL_VARIATION)
    assert var.id == "test-var"
    assert var.moves == ["e4", "e5"]
    assert var.annotations == []
    assert var.master_games == []

def test_parse_variation_missing_required_field():
    bad = {k: v for k, v in _MINIMAL_VARIATION.items() if k != "plan"}
    with pytest.raises(ValueError, match="plan"):
        _parse_variation(bad)

def test_parse_variation_illegal_move():
    bad = {**_MINIMAL_VARIATION, "moves": ["e4", "e5", "Qh8"]}
    with pytest.raises(ValueError, match="inválido"):
        _parse_variation(bad)

def test_parse_variation_with_annotations():
    data = {
        **_MINIMAL_VARIATION,
        "annotations": [{"after_move": 1, "text": "Abre o jogo."}],
    }
    var = _parse_variation(data)
    assert len(var.annotations) == 1
    assert var.annotations[0].after_move == 1
    assert var.annotations[0].text == "Abre o jogo."


# ── _parse_opening ────────────────────────────────────────────────────────────

def test_parse_opening_minimal():
    op = _parse_opening(_MINIMAL_OPENING)
    assert op.id == "test"
    assert len(op.variations) == 1

def test_parse_opening_missing_field():
    bad = {"id": "x", "name": "X"}  # missing variations
    with pytest.raises(ValueError, match="variations"):
        _parse_opening(bad)


# ── load_variation (integration with real JSON) ───────────────────────────────

def test_load_variation_najdorf():
    var = load_variation("sicilian", "najdorf")
    assert var.id == "najdorf"
    assert len(var.moves) == 10
    assert var.moves[-1] == "a6"

def test_load_variation_has_annotations():
    var = load_variation("sicilian", "najdorf")
    assert len(var.annotations) > 0

def test_load_variation_has_master_game():
    var = load_variation("sicilian", "najdorf")
    assert len(var.master_games) == 1
    assert var.master_games[0].white == "Fischer"

def test_load_variation_no_data_opening():
    with pytest.raises(ValueError, match="Nenhum dado"):
        load_variation("ruy-lopez", "berlin")

def test_load_variation_not_found():
    with pytest.raises(ValueError, match="não encontrada"):
        load_variation("sicilian", "benoni")
