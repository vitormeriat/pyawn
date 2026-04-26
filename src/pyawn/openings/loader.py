"""Stub opening data — hardcoded for UI validation; real JSON loader comes later."""

from dataclasses import dataclass, field

OPENINGS_DATA: dict[str, dict] = {
    "sicilian": {
        "name": "Sicilian Defense",
        "eco": "B20–B99",
        "variations": {
            "najdorf":       "Najdorf",
            "dragon":        "Dragon",
            "scheveningen":  "Scheveningen",
        },
    },
    "ruy-lopez": {
        "name": "Ruy López",
        "eco": "C60–C99",
        "variations": {
            "marshall": "Marshall Attack",
            "berlin":   "Berlin Defense",
        },
    },
    "french": {
        "name": "French Defense",
        "eco": "C00–C19",
        "variations": {
            "winawer":   "Winawer",
            "classical": "Clássica",
            "advance":   "Advance",
        },
    },
    "caro-kann": {
        "name": "Caro-Kann Defense",
        "eco": "B10–B19",
        "variations": {
            "classical": "Clássica",
            "advance":   "Advance",
            "exchange":  "Troca",
        },
    },
    "italian": {
        "name": "Italian Game",
        "eco": "C50–C59",
        "variations": {
            "giuoco-piano": "Giuoco Piano",
            "evans-gambit": "Gambito Evans",
        },
    },
}


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


def list_openings() -> list[OpeningStub]:
    return [
        OpeningStub(
            id=oid,
            name=data["name"],
            eco=data["eco"],
            variations=[
                VariationStub(id=vid, name=vname)
                for vid, vname in data["variations"].items()
            ],
        )
        for oid, data in OPENINGS_DATA.items()
    ]


def get_opening(opening_id: str) -> OpeningStub | None:
    normalized = opening_id.lower().replace("_", "-")
    data = OPENINGS_DATA.get(normalized)
    if not data:
        return None
    return OpeningStub(
        id=normalized,
        name=data["name"],
        eco=data["eco"],
        variations=[
            VariationStub(id=vid, name=vname)
            for vid, vname in data["variations"].items()
        ],
    )
