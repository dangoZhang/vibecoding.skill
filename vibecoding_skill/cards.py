from __future__ import annotations

from html import escape
from pathlib import Path
import re
import subprocess

from .parsers import default_display_name
from .themes import get_ai_level_theme


BASE_FONT_SIZE = 30
BIG_FONT_SIZE = BASE_FONT_SIZE * 3
BASE_LINE_HEIGHT = 40
BODY_WRAP_UNITS = 26.0


def write_cards(
    payload: dict[str, object],
    output_dir: str | Path,
    certificate_choice: str = "both",
    style: str = "default",
) -> dict[str, str]:
    del certificate_choice
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    basename = "vibecoding-card" if style != "xianxia" else "vibecoding-card-xianxia"
    svg_path = target_dir / f"{basename}.svg"
    png_path = target_dir / f"{basename}.png"
    svg_path.write_text(render_vibecoding_card(payload, style=style), encoding="utf-8")
    _render_png(svg_path, png_path)
    return {"card_svg": str(svg_path), "card_png": str(png_path)}


def render_vibecoding_card(payload: dict[str, object], style: str = "default") -> str:
    insights = _as_dict(payload.get("insights"))
    display_name = _truncate_text(_get_display_name(payload), 18)
    generated_at = _format_generated_at(payload.get("generated_at"))
    realm = str(insights.get("realm") or "凡人")
    rank = str(insights.get("rank") or "L1")
    ability_text = str(insights.get("card_ability_text") or insights.get("ability_text") or "仍在引气试手。")
    ability_lines = _wrap_block([ability_text], BODY_WRAP_UNITS, limit=6)
    verdict_source = _string_list(insights.get("card_verdict_lines")) if style == "xianxia" else _string_list(insights.get("standard_card_verdict_lines"))
    verdict_source = verdict_source or _string_list(insights.get("verdict_lines"))
    verdict_lines = _wrap_block(verdict_source, BODY_WRAP_UNITS, limit=3)
    breakthrough_source = _string_list(insights.get("card_breakthrough_lines")) or _string_list(insights.get("breakthrough_lines"))
    breakthrough_lines = _wrap_block([_join_prose(breakthrough_source)], BODY_WRAP_UNITS, limit=4)
    theme = get_ai_level_theme(rank)

    model_name = _primary_model(payload)
    card_x = 72
    card_y = 56
    card_w = 1056
    card_h = 1488
    content_x = 122
    content_w = 956
    header_y = 146
    slogan_y = 206
    hero_x = 122
    hero_y = 252
    hero_w = 956
    hero_h = 304
    hero_mid_x = hero_x + hero_w / 2
    label_y = hero_y + 46
    big_y = hero_y + 192

    ability_panel_y = 592
    ability_panel_h = 128 + max(0, len(ability_lines) - 1) * BASE_LINE_HEIGHT
    verdict_panel_y = ability_panel_y + ability_panel_h + 22
    verdict_panel_h = 120 + max(0, len(verdict_lines) - 1) * BASE_LINE_HEIGHT
    breakthrough_panel_y = verdict_panel_y + verdict_panel_h + 22
    breakthrough_panel_h = 120 + max(0, len(breakthrough_lines) - 1) * BASE_LINE_HEIGHT

    meta_1_y = breakthrough_panel_y + breakthrough_panel_h + 52
    meta_2_y = meta_1_y + 60
    is_xianxia = style == "xianxia"
    title = "vibecoding.skill"
    slogan = "蒸馏你与 Code Agent 的协作记录"
    hero_label = "境界 | 等级" if is_xianxia else "等级"
    hero_value = f"{realm} | {rank}" if is_xianxia else rank
    verdict_label = "判词"
    breakthrough_label = "突破方向" if is_xianxia else "下一步"
    model_label = "法器" if is_xianxia else "模型"
    user_label = "称呼" if is_xianxia else "用户"

    return f"""<svg width="1200" height="1600" viewBox="0 0 1200 1600" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="1600" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("bg_from", "#1B1B1B")))}"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("bg_to", "#101820")))}"/>
    </linearGradient>
    <radialGradient id="haloTop" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1018 182) rotate(129.484) scale(514.805 377.884)">
      <stop stop-color="{_escape(str(theme.get("halo", "#67C5E2")))}" stop-opacity="0.34"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("halo", "#67C5E2")))}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="haloBottom" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(180 1486) rotate(-34.84) scale(474.11 301.679)">
      <stop stop-color="{_escape(str(theme.get("accent", "#59BFE0")))}" stop-opacity="0.24"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("accent", "#59BFE0")))}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="hero" x1="{hero_x}" y1="{hero_y}" x2="{hero_x + hero_w}" y2="{hero_y + hero_h}" gradientUnits="userSpaceOnUse">
      <stop stop-color="#182632"/>
      <stop offset="1" stop-color="#101A23"/>
    </linearGradient>
    <filter id="shadow" x="52" y="40" width="1096" height="1528" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset dy="28"/>
      <feGaussianBlur stdDeviation="18"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.02 0 0 0 0 0.03 0 0 0 0 0.05 0 0 0 0.45 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_0_1"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_0_1" result="shape"/>
    </filter>
    <filter id="glow" x="0" y="0" width="1200" height="1600" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feGaussianBlur stdDeviation="16"/>
    </filter>
  </defs>

  <rect width="1200" height="1600" rx="48" fill="url(#bg)"/>
  <circle cx="1018" cy="182" r="364" fill="url(#haloTop)" filter="url(#glow)"/>
  <circle cx="180" cy="1486" r="286" fill="url(#haloBottom)" filter="url(#glow)"/>

  <g filter="url(#shadow)">
    <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="40" fill="#0E1620" stroke="rgba(255,255,255,0.08)" stroke-width="2"/>
  </g>
  <rect x="{card_x + 18}" y="{card_y + 18}" width="{card_w - 36}" height="8" rx="4" fill="{_escape(str(theme.get("accent", "#8EC5FF")))}"/>
  <text x="600" y="{header_y}" fill="#F4F8FB" font-size="{BASE_FONT_SIZE}" text-anchor="middle" font-family="STKaiti, KaiTi, serif" font-weight="700">{_escape(title)}</text>
  <text x="600" y="{slogan_y}" fill="#D7E3EE" font-size="{BASE_FONT_SIZE}" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" font-weight="600">{_escape(slogan)}</text>

  <rect x="{hero_x}" y="{hero_y}" width="{hero_w}" height="{hero_h}" rx="30" fill="url(#hero)" stroke="{_escape(str(theme.get("accent_dark", "#314554")))}" stroke-width="2"/>

  {_label_pill(int(hero_mid_x - 104), label_y - 32, 208, hero_label, theme)}
  <text x="{hero_mid_x}" y="{big_y}" fill="#FFFFFF" font-size="{BIG_FONT_SIZE}" text-anchor="middle" font-family="STKaiti, KaiTi, serif" font-weight="700">{_escape(hero_value)}</text>

  {_section_panel(content_x, ability_panel_y, content_w, ability_panel_h, 292, "vibecoding能力", ability_lines, theme)}
  {_section_panel(content_x, verdict_panel_y, content_w, verdict_panel_h, 176, verdict_label, verdict_lines, theme)}
  {_section_panel(content_x, breakthrough_panel_y, content_w, breakthrough_panel_h, 176, breakthrough_label, breakthrough_lines, theme)}

  {_meta_chip(184, meta_1_y - 34, 832, f"{model_label} {model_name}  |  tokens {_token_name(payload)}", theme)}
  {_meta_chip(240, meta_2_y - 34, 720, f"{user_label} {display_name}  |  生成于 {generated_at}", theme)}

</svg>
"""


def _label_pill(x: int, y: int, width: int, title: str, theme: dict[str, str]) -> str:
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="44" rx="22" fill="{_escape(str(theme.get('accent_dark', '#2F7F55')))}" stroke="rgba(255,255,255,0.72)" stroke-width="2"/>
    <text x="{x + width / 2}" y="{y + 30}" fill="#FFFFFF" font-size="{BASE_FONT_SIZE}" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">{_escape(title)}</text>
  </g>"""


def _section_panel(x: int, y: int, width: int, height: int, label_width: int, title: str, lines: list[str], theme: dict[str, str]) -> str:
    text_y = y + 104
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="28" fill="{_escape(str(theme.get('panel_bg', '#1C323C')))}" stroke="rgba(255,255,255,0.08)" stroke-width="2"/>
    {_label_pill(x + 24, y + 24, label_width, title, theme)}
    {_text_lines(lines, x=x + 28, y=text_y, font_size=BASE_FONT_SIZE, line_height=BASE_LINE_HEIGHT, fill="#F5F7FA", anchor="start", family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif", weight="500")}
  </g>"""


def _meta_chip(x: int, y: int, width: int, text: str, theme: dict[str, str]) -> str:
    del theme
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="56" rx="28" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" stroke-width="2"/>
    <text x="{x + width / 2}" y="{y + 37}" fill="#D5E0EA" font-size="{BASE_FONT_SIZE}" text-anchor="middle" font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif">{_escape(text)}</text>
  </g>"""


def _text_lines(
    lines: list[str],
    *,
    x: int,
    y: int,
    font_size: int,
    line_height: int,
    fill: str,
    anchor: str,
    family: str,
    weight: str = "400",
) -> str:
    if not lines:
        return ""
    parts = [f'<text x="{x}" y="{y}" fill="{fill}" font-size="{font_size}" text-anchor="{anchor}" font-family="{family}" font-weight="{weight}">']
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        parts.append(f'<tspan x="{x}" dy="{dy}">{_escape(line)}</tspan>')
    parts.append("</text>")
    return "".join(parts)


def _wrap_text(text: str, max_units: float, limit: int | None = None) -> list[str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []
    tokens = _tokenize_for_wrap(cleaned)
    lines: list[str] = []
    current = ""
    current_units = 0.0
    for token in tokens:
        token_units = _text_units(token)
        if token_units > max_units:
            for segment in _split_long_token(token, max_units):
                segment_units = _text_units(segment)
                if current and current_units + segment_units > max_units:
                    lines.append(current)
                    current = ""
                    current_units = 0.0
                    if limit and len(lines) >= limit:
                        break
                current += segment
                current_units += segment_units
            if limit and len(lines) >= limit:
                break
            continue
        if current and current_units + token_units > max_units:
            lines.append(current)
            current = token
            current_units = token_units
            if limit and len(lines) >= limit:
                break
            continue
        current += token
        current_units += token_units
    if current and (not limit or len(lines) < limit):
        lines.append(current)
    if limit and len(lines) > limit:
        lines = lines[:limit]
    if limit and lines and len(lines) == limit and _text_units(cleaned) > sum(_text_units(line) for line in lines):
        lines[-1] = _truncate_text(lines[-1], max(2, int(max_units) - 2))
    return lines


def _wrap_block(items: list[str], max_units: float, limit: int) -> list[str]:
    lines: list[str] = []
    for item in items:
        wrapped = _wrap_text(str(item), max_units)
        if not wrapped:
            continue
        remaining = limit - len(lines)
        if remaining <= 0:
            break
        if len(wrapped) <= remaining:
            lines.extend(wrapped)
            continue
        lines.extend(wrapped[:remaining])
        lines[-1] = _truncate_text(lines[-1], max(2, int(max_units) - 2))
        break
    return lines


def _join_prose(items: list[str]) -> str:
    cleaned = []
    for item in items:
        text = " ".join((item or "").split())
        if text:
            cleaned.append(text)
    return "".join(cleaned)


def _truncate_text(text: str, limit_units: int) -> str:
    total = 0.0
    result = []
    for char in text:
        units = _char_units(char)
        if total + units > limit_units:
            result.append("…")
            break
        result.append(char)
        total += units
    return "".join(result)


def _tokenize_for_wrap(text: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    suffix_punctuation = "，。！？；：、）》」』】)"
    while i < len(text):
        char = text[i]
        if char in "（(":
            closing = "）" if char == "（" else ")"
            end = text.find(closing, i + 1)
            if end != -1:
                segment = text[i : end + 1]
                if tokens:
                    prefix = tokens.pop()
                    while tokens and _is_single_cjk_token(prefix) and _is_single_cjk_token(tokens[-1]) and len(prefix) < 4:
                        prefix = tokens.pop() + prefix
                    tokens.append(prefix + segment)
                else:
                    tokens.append(segment)
                i = end + 1
                continue
        if char.isspace():
            i += 1
            continue
        if char in suffix_punctuation and tokens:
            tokens[-1] += char
            i += 1
            continue
        if ord(char) < 128:
            j = i + 1
            while j < len(text) and ord(text[j]) < 128 and text[j] not in "（(":
                j += 1
            tokens.append(text[i:j].rstrip())
            i = j
            continue
        tokens.append(char)
        i += 1
    return [token for token in tokens if token]


def _is_single_cjk_token(token: str) -> bool:
    return len(token) == 1 and ord(token) >= 128 and token not in "，。！？；：、）》」』】)"


def _split_long_token(token: str, max_units: float) -> list[str]:
    parts: list[str] = []
    working = token
    if token.startswith(("（", "(")) and token.endswith(("）", ")")):
        opener, closer = token[0], token[-1]
        inner = token[1:-1]
        inner_parts = _split_ascii_segment(inner, max_units - 1.2)
        for index, part in enumerate(inner_parts):
            prefix = opener if index == 0 else ""
            suffix = closer if index == len(inner_parts) - 1 else ""
            parts.append(f"{prefix}{part}{suffix}")
        return parts
    if re.fullmatch(r"[\x00-\x7F]+", token):
        return _split_ascii_segment(working, max_units)
    return _split_cjk_segment(working, max_units)


def _split_ascii_segment(text: str, max_units: float) -> list[str]:
    words = re.findall(r"\S+\s*", text)
    if not words:
        return [text]
    parts: list[str] = []
    current = ""
    current_units = 0.0
    for word in words:
        word_units = _text_units(word)
        if current and current_units + word_units > max_units:
            parts.append(current.rstrip())
            current = word
            current_units = word_units
            continue
        current += word
        current_units += word_units
    if current.strip():
        parts.append(current.rstrip())
    return parts or [text]


def _split_cjk_segment(text: str, max_units: float) -> list[str]:
    parts: list[str] = []
    current = ""
    current_units = 0.0
    for char in text:
        char_units = _char_units(char)
        if current and current_units + char_units > max_units:
            parts.append(current)
            current = char
            current_units = char_units
            continue
        current += char
        current_units += char_units
    if current:
        parts.append(current)
    return parts or [text]


def _text_units(text: str) -> float:
    return sum(_char_units(char) for char in text)


def _char_units(char: str) -> float:
    if char.isspace():
        return 0.35
    if ord(char) < 128:
        return 0.58
    return 1.0


def _primary_model(payload: dict[str, object]) -> str:
    transcript = _as_dict(payload.get("transcript"))
    models = transcript.get("models")
    if not isinstance(models, list) or not models:
        models = payload.get("models")
    if isinstance(models, list) and models:
        return _truncate_text(str(models[0]).replace("openai/", "").replace("anthropic/", ""), 24)
    return _source_platform(payload)


def _source_platform(payload: dict[str, object]) -> str:
    transcript = _as_dict(payload.get("transcript"))
    source = str(transcript.get("source") or payload.get("source") or "").lower()
    labels = {
        "codex": "Codex",
        "claude": "Claude Code",
        "opencode": "OpenCode",
        "openclaw": "OpenClaw",
        "cursor": "Cursor",
        "vscode": "VS Code",
    }
    return labels.get(source, "本地平台")


def _sample_name(payload: dict[str, object]) -> str:
    transcript = _as_dict(payload.get("transcript"))
    messages = int(transcript.get("message_count") or payload.get("total_messages") or 0)
    tool_calls = int(transcript.get("tool_calls") or payload.get("total_tool_calls") or 0)
    sessions_used = payload.get("sessions_used")
    if isinstance(sessions_used, int) and sessions_used > 1:
        return _truncate_text(f"{sessions_used} 场 · {messages} messages", 24)
    return _truncate_text(f"{messages} messages · {tool_calls} tool calls", 24)


def _token_name(payload: dict[str, object]) -> str:
    transcript = _as_dict(payload.get("transcript"))
    usage = _as_dict(transcript.get("token_usage")) or _as_dict(payload.get("token_usage"))
    total = int(usage.get("total_tokens") or 0)
    return f"{total:,}" if total else "未显"


def _get_display_name(payload: dict[str, object]) -> str:
    transcript = _as_dict(payload.get("transcript"))
    if transcript.get("display_name"):
        return str(transcript["display_name"])
    if payload.get("display_name"):
        return str(payload["display_name"])
    return default_display_name("user")


def _format_generated_at(value: object) -> str:
    text = str(value or "").strip()
    return text.replace("T", " ").replace("+08:00", "").replace("+00:00", " UTC")


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _escape(value: str) -> str:
    return escape(value, quote=True)


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _render_png(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        [
            "rsvg-convert",
            "--dpi-x",
            "300",
            "--dpi-y",
            "300",
            str(svg_path),
            "-o",
            str(png_path),
        ],
        check=True,
    )
    subprocess.run(
        [
            "sips",
            "-s",
            "dpiWidth",
            "300",
            "-s",
            "dpiHeight",
            "300",
            str(png_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
