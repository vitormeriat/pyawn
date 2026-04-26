"""Opening data loader — reads JSON files from openings/data/."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import chess

_DATA_DIR = Path(__file__).parent / "data"

# Registry of all openings — used for menu display without loading full JSON.
_REGISTRY: dict[str, dict] = {
    "sicilian": {
        "name": "Sicilian Defense",
        "eco": "B20-B99",
        "file": "sicilian.json",
        "variations": {"najdorf": "Najdorf", "dragon": "Dragon", "scheveningen": "Scheveningen"},
    },
    "ruy-lopez": {
        "name": "Ruy López",
        "eco": "C60-C99",
        "file": None,
        "variations": {"marshall": "Marshall Attack", "berlin": "Berlin Defense"},
    },
    "french": {
        "name": "French Defense",
        "eco": "C00-C19",
        "file": None,
        "variations": {"winawer": "Winawer", "classical": "Clássica", "advance": "Advance"},
    },
    "caro-kann": {
        "name": "Caro-Kann Defense",
        "eco": "B10-B19",
        "file": None,
        "variations": {"classical": "Clássica", "advance": "Advance", "exchange": "Troca"},
    },
    "italian": {
        "name": "Italian Game",
        "eco": "C50-C59",
        "file": None,
        "variations": {"giuoco-piano": "Giuoco Piano", "evans-gambit": "Gambito Evans"},
    },
}


# ── Public types ──────────────────────────────────────────────────────────────

@dataclass
class VariationStub:
    id: str
    name: str


@dataclass
class OpeningStub:
    id: str
    name: str
    eco: str
    variations: list[VariationStub] = field(default_factory=list)


@dataclass
class Annotation:
    after_move: int
    text: str


@dataclass
class MasterGame:
    white: str
    black: str
    year: int
    event: str
    pgn: str | None = None


@dataclass
class Variation:
    id: str
    name: str
    moves: list[str]
    plan: str
    eco: str | None = None
    annotations: list[Annotation] = field(default_factory=list)
    master_games: list[MasterGame] = field(default_factory=list)


@dataclass
class Opening:
    id: str
    name: str
    variations: list[Variation]
    eco: str | None = None


# ── Menu helpers (from registry, no JSON I/O) ─────────────────────────────────

def list_openings() -> list[OpeningStub]:
    return [
        OpeningStub(
            id=oid,
            name=data["name"],
            eco=data["eco"],
            variations=[VariationStub(id=vid, name=vname) for vid, vname in data["variations"].items()],
        )
        for oid, data in _REGISTRY.items()
    ]


def get_opening(opening_id: str) -> OpeningStub | None:
    norm = _normalize(opening_id)
    data = _REGISTRY.get(norm)
    if not data:
        return None
    return OpeningStub(
        id=norm,
        name=data["name"],
        eco=data["eco"],
        variations=[VariationStub(id=vid, name=vname) for vid, vname in data["variations"].items()],
    )


def has_study_data(opening_id: str) -> bool:
    norm = _normalize(opening_id)
    entry = _REGISTRY.get(norm)
    return bool(entry and entry["file"])


# ── Full data loader (from JSON) ──────────────────────────────────────────────

def load_variation(opening_id: str, variation_id: str) -> Variation:
    norm_op = _normalize(opening_id)
    reg = _REGISTRY.get(norm_op)
    if not reg or not reg["file"]:
        raise ValueError(f"Nenhum dado de estudo disponível para '{opening_id}'.")
    opening = _load_opening_cached(norm_op)
    norm_var = _normalize(variation_id)
    for var in opening.variations:
        if var.id == norm_var:
            return var
    raise ValueError(f"Variação '{variation_id}' não encontrada em '{opening_id}'.")


@lru_cache(maxsize=16)
def _load_opening_cached(opening_id: str) -> Opening:
    path = _DATA_DIR / _REGISTRY[opening_id]["file"]
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _parse_opening(raw)


def _parse_opening(data: dict) -> Opening:
    for req in ("id", "name", "variations"):
        if req not in data:
            raise ValueError(f"JSON inválido: campo obrigatório ausente: '{req}'")
    return Opening(
        id=data["id"],
        name=data["name"],
        eco=data.get("eco"),
        variations=[_parse_variation(v) for v in data["variations"]],
    )


def _parse_variation(data: dict) -> Variation:
    for req in ("id", "name", "moves", "plan"):
        if req not in data:
            raise ValueError(f"Variação inválida: campo obrigatório ausente: '{req}'")
    _validate_moves(data["id"], data["moves"])
    return Variation(
        id=data["id"],
        name=data["name"],
        moves=data["moves"],
        plan=data["plan"],
        eco=data.get("eco"),
        annotations=[
            Annotation(after_move=a["after_move"], text=a["text"])
            for a in data.get("annotations", [])
        ],
        master_games=[
            MasterGame(
                white=g["white"],
                black=g["black"],
                year=g["year"],
                event=g["event"],
                pgn=g.get("pgn"),
            )
            for g in data.get("master_games", [])
        ],
    )


def _validate_moves(var_id: str, moves: list[str]) -> None:
    board = chess.Board()
    for i, san in enumerate(moves):
        try:
            board.push(board.parse_san(san))
        except Exception as exc:
            raise ValueError(
                f"Variação '{var_id}' — lance #{i + 1} '{san}' é inválido: {exc}"
            ) from exc


def _normalize(s: str) -> str:
    return s.lower().replace("_", "-")
