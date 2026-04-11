from __future__ import annotations

from html import escape
from pathlib import Path
import re
import subprocess

from .parsers import default_display_name
from .themes import get_ai_level_theme


BASE_FONT_SIZE = 30
BIG_FONT_SIZE = 220
BASE_LINE_HEIGHT = 40
BODY_WRAP_UNITS = 24.0


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
    card_language = str(insights.get("card_language") or "zh")
    display_name = _truncate_text(_get_display_name(payload, card_language), 18)
    generated_at = _format_generated_at(payload.get("generated_at"))
    realm = str(insights.get("realm") or "凡人")
    rank = str(insights.get("rank") or "L1")
    ability_key = "card_ability_text_en" if card_language == "en" else "card_ability_text"
    ability_text = str(insights.get(ability_key) or insights.get("card_ability_text") or insights.get("ability_text") or "仍在引气试手。")
    ability_lines = _wrap_block([ability_text], 32.0, limit=6)
    verdict_key = "card_verdict_lines_en" if style == "xianxia" and card_language == "en" else (
        "card_verdict_lines" if style == "xianxia" else ("standard_card_verdict_lines_en" if card_language == "en" else "standard_card_verdict_lines")
    )
    verdict_source = _string_list(insights.get(verdict_key))
    verdict_source = verdict_source or _string_list(insights.get("card_verdict_lines_en" if card_language == "en" else "card_verdict_lines"))
    verdict_source = verdict_source or _string_list(insights.get("verdict_lines"))
    verdict_lines = _wrap_block(verdict_source, 15.5, limit=6)
    breakthrough_source = _string_list(insights.get("card_breakthrough_lines_en" if card_language == "en" else "card_breakthrough_lines")) or _string_list(insights.get("breakthrough_lines"))
    breakthrough_lines = _wrap_block([_join_prose(breakthrough_source)], 15.5, limit=7)
    theme = get_ai_level_theme(rank)

    model_name = _primary_model(payload)
    is_xianxia = style == "xianxia"
    title = "vibecoding.skill"
    slogan = "Distill your Code Agent history" if card_language == "en" else "蒸馏你的 Code Agent 记录"
    hero_label = "Realm | Level" if is_xianxia and card_language == "en" else ("境界 | 等级" if is_xianxia else ("Level" if card_language == "en" else "等级"))
    hero_value = f"{realm} · {rank}" if is_xianxia else rank
    hero_value_size = 126 if is_xianxia else BIG_FONT_SIZE
    verdict_label = "Verdict" if card_language == "en" else "判词"
    breakthrough_label = "Path forward" if is_xianxia and card_language == "en" else ("Next step" if card_language == "en" else ("突破方向" if is_xianxia else "下一步"))
    model_label = "Model" if card_language == "en" else ("法器" if is_xianxia else "模型")
    user_label = "Name" if card_language == "en" else ("称呼" if is_xianxia else "用户")
    usage_text = _token_name(payload)
    source_label = "Sample" if card_language == "en" else "样本"
    platform_label = "Host" if card_language == "en" else "宿主"
    ability_label = "Core read" if card_language == "en" else "核心判断"
    ability_panel_label = "Ability profile" if card_language == "en" else "能力摘要"
    hero_meta_title = "Recent trace" if card_language == "en" else "真实协作"
    header_meta = "REAL CODE AGENT HISTORY" if card_language == "en" else "REAL CODE AGENT HISTORY"
    time_label = "Time" if card_language == "en" else "时间"
    hero_note = "Based on your recent real collaboration trace." if card_language == "en" else "基于你最近一段真实协作记录。"
    sample_name = _sample_name(payload)
    platform_name = _source_platform(payload)
    display_family = _display_font(card_language)
    body_family = _body_font(card_language)
    mono_family = "SFMono-Regular, ui-monospace, Menlo, Monaco, Consolas, monospace"

    card_x = 60
    card_y = 60
    card_w = 1080
    card_h = 1480
    header_x = card_x + 58
    hero_x = card_x + 48
    hero_y = card_y + 146
    hero_w = card_w - 96
    hero_h = 670
    hero_rank_x = hero_x + 56
    hero_rank_y = hero_y + 266
    hero_meta_x = hero_x + 618
    hero_meta_y = hero_y + 118
    hero_divider_y = hero_y + 388
    hero_summary_x = hero_x + 56
    hero_summary_y = hero_divider_y + 58
    hero_text_y = hero_divider_y + 128

    section_y = hero_y + hero_h + 34
    section_gap = 28
    section_w = (hero_w - section_gap) / 2
    section_h = 360
    left_section_x = hero_x
    right_section_x = hero_x + section_w + section_gap

    footer_y = section_y + section_h + 40

    return f"""<svg width="1200" height="1600" viewBox="0 0 1200 1600" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="1600" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("bg_from", "#1B1B1B")))}"/>
      <stop offset="0.48" stop-color="{_escape(str(theme.get("bg_mid", "#14202A")))}"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("bg_to", "#101820")))}"/>
    </linearGradient>
    <radialGradient id="haloTop" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(1014 226) rotate(132.8) scale(552 418)">
      <stop stop-color="{_escape(str(theme.get("glow", "#A5E3FF")))}" stop-opacity="0.42"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("glow", "#A5E3FF")))}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="haloBottom" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(188 1454) rotate(-28) scale(478 288)">
      <stop stop-color="{_escape(str(theme.get("accent_soft", "#83D7F1")))}" stop-opacity="0.28"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("accent_soft", "#83D7F1")))}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="rankGlow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({hero_rank_x + 104} {hero_y + 206}) rotate(44) scale(228 194)">
      <stop stop-color="{_escape(str(theme.get("accent", "#59BFE0")))}" stop-opacity="0.34"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("accent", "#59BFE0")))}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="frame" x1="{card_x}" y1="{card_y}" x2="{card_x + card_w}" y2="{card_y + card_h}" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("surface_soft", "#223342")))}" stop-opacity="0.82"/>
      <stop offset="1" stop-color="#0A1118" stop-opacity="0.96"/>
    </linearGradient>
    <linearGradient id="hero" x1="{hero_x}" y1="{hero_y}" x2="{hero_x + hero_w}" y2="{hero_y + hero_h}" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("hero_from", "#1E2F40")))}" stop-opacity="0.98"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("hero_to", "#0C131B")))}"/>
    </linearGradient>
    <linearGradient id="sectionAccent" x1="{right_section_x}" y1="{section_y}" x2="{right_section_x + section_w}" y2="{section_y + section_h}" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(str(theme.get("surface_alt", "#294052")))}" stop-opacity="0.90"/>
      <stop offset="1" stop-color="{_escape(str(theme.get("surface", "#182431")))}" stop-opacity="0.92"/>
    </linearGradient>
    <filter id="shadow" x="24" y="24" width="1152" height="1552" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset dy="28"/>
      <feGaussianBlur stdDeviation="22"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.01 0 0 0 0 0.03 0 0 0 0 0.05 0 0 0 0.46 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_0_1"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_0_1" result="shape"/>
    </filter>
    <filter id="glow" x="0" y="0" width="1200" height="1600" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <filter id="softBlur" x="-80" y="-80" width="1360" height="1760" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feGaussianBlur stdDeviation="32"/>
    </filter>
  </defs>

  <rect width="1200" height="1600" rx="52" fill="url(#bg)"/>
  <circle cx="1018" cy="182" r="364" fill="url(#haloTop)" filter="url(#glow)"/>
  <circle cx="180" cy="1486" r="286" fill="url(#haloBottom)" filter="url(#glow)"/>
  <path d="M-40 1188C140 1128 268 1156 434 1248C616 1348 792 1380 1240 1266V1600H-40V1188Z" fill="{_escape(str(theme.get("surface_soft", "#223342")))}" fill-opacity="0.12"/>

  <g filter="url(#shadow)">
    <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="42" fill="url(#frame)" stroke="{_escape(str(theme.get("line_soft", "#31546A")))}" stroke-opacity="0.56" stroke-width="1.5"/>
  </g>
  <rect x="{card_x + 30}" y="{card_y + 26}" width="{card_w - 60}" height="3" rx="1.5" fill="{_escape(str(theme.get("accent_soft", "#8EDBFF")))}" fill-opacity="0.9"/>
  <text x="{header_x}" y="{card_y + 84}" fill="#F6FBFF" font-size="16" letter-spacing="4" text-anchor="start" font-family="{mono_family}" font-weight="500">{_escape(header_meta)}</text>
  <text x="{header_x}" y="{card_y + 132}" fill="#FFFFFF" font-size="36" text-anchor="start" font-family="{display_family}" font-weight="700">{_escape(title)}</text>
  <text x="{header_x}" y="{card_y + 176}" fill="{_escape(str(theme.get("mist", "#D6E4EC")))}" font-size="24" text-anchor="start" font-family="{body_family}" font-weight="500">{_escape(slogan)}</text>
  <line x1="{card_x + 54}" y1="{card_y + 210}" x2="{card_x + card_w - 54}" y2="{card_y + 210}" stroke="{_escape(str(theme.get("line_soft", "#31546A")))}" stroke-opacity="0.8"/>

    <g>
    <rect x="{hero_x}" y="{hero_y}" width="{hero_w}" height="{hero_h}" rx="34" fill="url(#hero)" stroke="{_escape(str(theme.get("line", "#6FBAD8")))}" stroke-opacity="0.42" stroke-width="1.5"/>
    <rect x="{hero_x + 18}" y="{hero_y + 18}" width="{hero_w - 36}" height="{hero_h - 36}" rx="28" stroke="#FFFFFF" stroke-opacity="0.06"/>
    <ellipse cx="{hero_rank_x + 124}" cy="{hero_y + 178}" rx="168" ry="136" fill="url(#rankGlow)" filter="url(#softBlur)"/>
    {_eyebrow(hero_x + 56, hero_y + 54, 170, hero_label, theme, body_family)}
    <text x="{hero_rank_x}" y="{hero_rank_y}" fill="#FFFFFF" font-size="{hero_value_size}" text-anchor="start" font-family="{display_family}" font-weight="700" letter-spacing="-6">{_escape(hero_value)}</text>
    <text x="{hero_rank_x}" y="{hero_y + 360}" fill="{_escape(str(theme.get("mist", "#D6E4EC")))}" font-size="24" text-anchor="start" font-family="{body_family}" font-weight="500">{_escape(hero_note)}</text>
    <text x="{hero_meta_x}" y="{hero_meta_y}" fill="{_escape(str(theme.get("accent_soft", "#8EDBFF")))}" font-size="18" text-anchor="start" font-family="{mono_family}" font-weight="600" letter-spacing="3">{_escape(ability_label.upper())}</text>
    <text x="{hero_meta_x}" y="{hero_meta_y + 56}" fill="#FFFFFF" font-size="44" text-anchor="start" font-family="{display_family}" font-weight="650">{_escape(hero_meta_title)}</text>
    {_stat_pill(hero_meta_x, hero_y + 222, 292, source_label, sample_name, theme, body_family, mono_family)}
    {_stat_pill(hero_meta_x, hero_y + 318, 198, platform_label, platform_name, theme, body_family, mono_family)}
    <line x1="{hero_x + 40}" y1="{hero_divider_y}" x2="{hero_x + hero_w - 40}" y2="{hero_divider_y}" stroke="{_escape(str(theme.get("line_soft", "#31546A")))}" stroke-opacity="0.92"/>
    <text x="{hero_summary_x}" y="{hero_summary_y}" fill="#FFFFFF" font-size="40" text-anchor="start" font-family="{display_family}" font-weight="650">{_escape(ability_panel_label)}</text>
    {_text_lines(ability_lines, x=hero_summary_x, y=hero_text_y, font_size=30, line_height=42, fill="#F3F8FC", anchor="start", family=body_family, weight="500")}
  </g>

  {_section_panel(left_section_x, section_y, int(section_w), section_h, verdict_label, verdict_lines, theme, body_family, display_family, mono_family)}
  {_section_panel(right_section_x, section_y, int(section_w), section_h, breakthrough_label, breakthrough_lines, theme, body_family, display_family, mono_family, accent=True)}

  <line x1="{card_x + 54}" y1="{footer_y - 18}" x2="{card_x + card_w - 54}" y2="{footer_y - 18}" stroke="{_escape(str(theme.get("line_soft", "#31546A")))}" stroke-opacity="0.72"/>
  <text x="{header_x}" y="{footer_y + 18}" fill="#F4F8FB" font-size="24" text-anchor="start" font-family="{body_family}" font-weight="600">{_escape(f"{model_label} {model_name}  |  tokens {usage_text}")}</text>
  <text x="{header_x}" y="{footer_y + 62}" fill="{_escape(str(theme.get("mist", "#D6E4EC")))}" font-size="24" text-anchor="start" font-family="{body_family}" font-weight="500">{_escape(f"{user_label} {display_name}  |  {time_label} {generated_at}")}</text>

</svg>
"""


def _eyebrow(x: int, y: int, width: int, title: str, theme: dict[str, str], family: str) -> str:
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="40" rx="20" fill="{_escape(str(theme.get('surface_alt', '#253A4B')))}" fill-opacity="0.92" stroke="{_escape(str(theme.get('line', '#6FBAD8')))}" stroke-opacity="0.56"/>
    <text x="{x + width / 2}" y="{y + 27}" fill="#FFFFFF" font-size="22" text-anchor="middle" font-family="{family}" font-weight="600">{_escape(title)}</text>
  </g>"""


def _stat_pill(
    x: int,
    y: int,
    width: int,
    label: str,
    value: str,
    theme: dict[str, str],
    family: str,
    mono_family: str,
) -> str:
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="82" rx="24" fill="{_escape(str(theme.get('surface', '#15212C')))}" fill-opacity="0.88" stroke="#FFFFFF" stroke-opacity="0.08"/>
    <text x="{x + 20}" y="{y + 28}" fill="{_escape(str(theme.get('mist', '#D6E4EC')))}" font-size="15" letter-spacing="2.4" text-anchor="start" font-family="{mono_family}" font-weight="500">{_escape(label.upper())}</text>
    <text x="{x + 20}" y="{y + 60}" fill="#FFFFFF" font-size="24" text-anchor="start" font-family="{family}" font-weight="600">{_escape(value)}</text>
  </g>"""


def _section_panel(
    x: float,
    y: int,
    width: int,
    height: int,
    title: str,
    lines: list[str],
    theme: dict[str, str],
    body_family: str,
    display_family: str,
    mono_family: str,
    accent: bool = False,
) -> str:
    fill = "url(#sectionAccent)" if accent else _escape(str(theme.get("surface", "#15212C")))
    fill_opacity = "" if accent else ' fill-opacity="0.88"'
    text_y = y + 126
    decorative_line = f'<line x1="{x + 24}" y1="{y + 86}" x2="{x + width - 24}" y2="{y + 86}" stroke="{_escape(str(theme.get("line_soft", "#31546A")))}" stroke-opacity="0.72"/>' if accent else ""
    accent_word = "NEXT" if accent else "READ"
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="32" fill="{fill}"{fill_opacity} stroke="{_escape(str(theme.get('line_soft', '#31546A')))}" stroke-opacity="0.7"/>
    <text x="{x + 24}" y="{y + 38}" fill="{_escape(str(theme.get('accent_soft', '#8EDBFF')))}" font-size="17" letter-spacing="2.6" text-anchor="start" font-family="{mono_family}" font-weight="600">{accent_word}</text>
    <text x="{x + 24}" y="{y + 72}" fill="#FFFFFF" font-size="38" text-anchor="start" font-family="{display_family}" font-weight="650">{_escape(title)}</text>
    {decorative_line}
    {_text_lines(lines, x=int(x + 24), y=text_y, font_size=26, line_height=38, fill="#F5F9FC", anchor="start", family=body_family, weight="500")}
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


def _display_font(card_language: str) -> str:
    if card_language == "en":
        return "SF Pro Display, Helvetica Neue, Arial, sans-serif"
    return "SF Pro Display, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"


def _body_font(card_language: str) -> str:
    if card_language == "en":
        return "SF Pro Text, Helvetica Neue, Arial, sans-serif"
    return "PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"


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


def _get_display_name(payload: dict[str, object], language: str = "zh") -> str:
    transcript = _as_dict(payload.get("transcript"))
    if transcript.get("display_name"):
        return str(transcript["display_name"])
    if payload.get("display_name"):
        return str(payload["display_name"])
    if language == "en":
        return "User"
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
