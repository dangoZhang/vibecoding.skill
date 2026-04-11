from __future__ import annotations


AI_LEVEL_THEMES = {
    "L1": {
        "name": "luogu-gray",
        "bg_from": "#1D2127",
        "bg_to": "#111418",
        "halo": "#C3CAD3",
        "accent": "#C7CDD6",
        "accent_dark": "#6D7682",
        "panel_bg": "#2A3038",
        "soft_panel": "#F2EEE6",
    },
    "L2": {
        "name": "luogu-mint",
        "bg_from": "#17251E",
        "bg_to": "#0F1713",
        "halo": "#8FD6B0",
        "accent": "#84D7A8",
        "accent_dark": "#2F7F55",
        "panel_bg": "#21372A",
        "soft_panel": "#EFF5EE",
    },
    "L3": {
        "name": "luogu-green",
        "bg_from": "#162316",
        "bg_to": "#0C140C",
        "halo": "#78D66D",
        "accent": "#66CC5C",
        "accent_dark": "#2C8A2B",
        "panel_bg": "#20351F",
        "soft_panel": "#F0F6ED",
    },
    "L4": {
        "name": "luogu-cyan",
        "bg_from": "#132229",
        "bg_to": "#0A151A",
        "halo": "#67C5E2",
        "accent": "#59BFE0",
        "accent_dark": "#207496",
        "panel_bg": "#1C323C",
        "soft_panel": "#EEF6F8",
    },
    "L5": {
        "name": "luogu-blue",
        "bg_from": "#121B2D",
        "bg_to": "#0A111C",
        "halo": "#5EA7FF",
        "accent": "#4B97FF",
        "accent_dark": "#215CB6",
        "panel_bg": "#1A2842",
        "soft_panel": "#EEF4FB",
    },
    "L6": {
        "name": "luogu-yellow",
        "bg_from": "#2B240E",
        "bg_to": "#171106",
        "halo": "#F1D06C",
        "accent": "#E9C84A",
        "accent_dark": "#A47713",
        "panel_bg": "#3A2F12",
        "soft_panel": "#FBF6E8",
    },
    "L7": {
        "name": "luogu-orange",
        "bg_from": "#2D180D",
        "bg_to": "#170D07",
        "halo": "#F0A05A",
        "accent": "#F38B3C",
        "accent_dark": "#B25417",
        "panel_bg": "#432416",
        "soft_panel": "#FCF1E9",
    },
    "L8": {
        "name": "luogu-red",
        "bg_from": "#2C1113",
        "bg_to": "#16080A",
        "halo": "#EC6E70",
        "accent": "#E65C5F",
        "accent_dark": "#B3262B",
        "panel_bg": "#441A1E",
        "soft_panel": "#FCEEEE",
    },
    "L9": {
        "name": "luogu-purple",
        "bg_from": "#231326",
        "bg_to": "#120913",
        "halo": "#B47DFF",
        "accent": "#A96BF6",
        "accent_dark": "#7037BE",
        "panel_bg": "#352048",
        "soft_panel": "#F6F0FC",
    },
    "L10": {
        "name": "luogu-black",
        "bg_from": "#161616",
        "bg_to": "#090909",
        "halo": "#F0D9A0",
        "accent": "#E3BE68",
        "accent_dark": "#8D6B21",
        "panel_bg": "#232323",
        "soft_panel": "#F7F2E8",
    },
}


def get_ai_level_theme(level: str) -> dict[str, str]:
    theme = AI_LEVEL_THEMES.get(level, AI_LEVEL_THEMES["L1"]).copy()
    accent = _normalize_hex(theme["accent"])
    bg_from = _normalize_hex(theme["bg_from"])
    bg_to = _normalize_hex(theme["bg_to"])
    panel_bg = _normalize_hex(theme["panel_bg"])

    theme["bg_mid"] = _mix_hex(bg_from, bg_to, 0.46)
    theme["hero_from"] = _mix_hex(bg_from, accent, 0.20)
    theme["hero_to"] = _mix_hex(bg_to, "#05070A", 0.36)
    theme["surface"] = _mix_hex(panel_bg, "#FFFFFF", 0.05)
    theme["surface_alt"] = _mix_hex(panel_bg, "#FFFFFF", 0.11)
    theme["surface_soft"] = _mix_hex(bg_from, "#FFFFFF", 0.14)
    theme["panel_edge"] = _mix_hex(panel_bg, "#FFFFFF", 0.18)
    theme["line"] = _mix_hex(accent, "#FFFFFF", 0.26)
    theme["line_soft"] = _mix_hex(accent, "#FFFFFF", 0.10)
    theme["accent_soft"] = _mix_hex(accent, "#FFFFFF", 0.38)
    theme["glow"] = _mix_hex(accent, "#FFFFFF", 0.58)
    theme["mist"] = _mix_hex(bg_mid := theme["bg_mid"], "#FFFFFF", 0.68)
    return theme


def _normalize_hex(value: str) -> str:
    text = value.strip()
    if not text.startswith("#"):
        raise ValueError(f"Expected hex color, got: {value}")
    if len(text) == 4:
        return "#" + "".join(char * 2 for char in text[1:])
    if len(text) != 7:
        raise ValueError(f"Unsupported hex color: {value}")
    return text.upper()


def _mix_hex(left: str, right: str, ratio: float) -> str:
    ratio = max(0.0, min(1.0, ratio))
    l_red, l_green, l_blue = _hex_to_rgb(left)
    r_red, r_green, r_blue = _hex_to_rgb(right)
    mixed = (
        round(l_red + (r_red - l_red) * ratio),
        round(l_green + (r_green - l_green) * ratio),
        round(l_blue + (r_blue - l_blue) * ratio),
    )
    return _rgb_to_hex(mixed)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    normalized = _normalize_hex(value)
    return tuple(int(normalized[index : index + 2], 16) for index in (1, 3, 5))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)
