from __future__ import annotations


LUOGU_LEVEL_PALETTE: dict[str, dict[str, str]] = {
    "L1": {
        "base": "#C7CDD6",
        "surface": "#1E232A",
        "surface_alt": "#2C333D",
        "glow": "#E3E8EE",
        "line": "#AEB8C4",
    },
    "L2": {
        "base": "#84D7A8",
        "surface": "#16241C",
        "surface_alt": "#203428",
        "glow": "#B7E9C9",
        "line": "#6DC792",
    },
    "L3": {
        "base": "#66CC5C",
        "surface": "#132014",
        "surface_alt": "#1D311E",
        "glow": "#9CE092",
        "line": "#53B64B",
    },
    "L4": {
        "base": "#59BFE0",
        "surface": "#10202A",
        "surface_alt": "#18313E",
        "glow": "#9FE2F5",
        "line": "#4EA9C7",
    },
    "L5": {
        "base": "#4B97FF",
        "surface": "#10192B",
        "surface_alt": "#182743",
        "glow": "#91BEFF",
        "line": "#4687E6",
    },
    "L6": {
        "base": "#E9C84A",
        "surface": "#28210D",
        "surface_alt": "#3A3013",
        "glow": "#F5DE86",
        "line": "#D5B43D",
    },
    "L7": {
        "base": "#F38B3C",
        "surface": "#29180F",
        "surface_alt": "#3B2417",
        "glow": "#F7B275",
        "line": "#DF7A2F",
    },
    "L8": {
        "base": "#E65C5F",
        "surface": "#281214",
        "surface_alt": "#3B1C20",
        "glow": "#F19698",
        "line": "#D24C50",
    },
    "L9": {
        "base": "#A96BF6",
        "surface": "#211329",
        "surface_alt": "#322042",
        "glow": "#CAA5FB",
        "line": "#9658E4",
    },
    "L10": {
        "base": "#E3BE68",
        "surface": "#1A1A18",
        "surface_alt": "#2A2823",
        "glow": "#F1DBA2",
        "line": "#CDAA56",
    },
}


def get_luogu_level_palette(level: str) -> dict[str, str]:
    return LUOGU_LEVEL_PALETTE.get(level, LUOGU_LEVEL_PALETTE["L1"]).copy()
