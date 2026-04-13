from __future__ import annotations

from dataclasses import dataclass
from html import escape
import platform
from pathlib import Path
import shutil
import subprocess
import sys

from .luogu_palette import get_luogu_level_palette
from .parsers import default_display_name


LEVEL_COPY = {
    "L1": "还停在随手问答，缺少稳定方法",
    "L2": "知道提问方式会影响结果",
    "L3": "能稳定完成简单任务",
    "L4": "常见任务可以稳定推进到多步完成",
    "L5": "开始把顺手打法沉成 skill、模板或模块",
    "L6": "已经有能替自己先干一段活的分身",
    "L7": "能调多 agent、多工具协同完成任务",
    "L8": "开始做能力层和长期工作流设计",
    "L9": "人负责判断和担责，agent 负责执行和回流",
    "L10": "能把自己的方法稳定复制给团队或客户",
}

LEVEL_COPY_EN = {
    "L1": "Still mostly ad hoc prompting, without a stable method",
    "L2": "Already knows that prompt phrasing changes outcomes",
    "L3": "Can complete simple tasks with some consistency",
    "L4": "Can push common tasks through stable multi-step execution",
    "L5": "Starts turning repeatable wins into skills, templates, or modules",
    "L6": "Already has an agent that can take a chunk of work first",
    "L7": "Can coordinate multiple agents and tools on one task",
    "L8": "Starts designing capability layers and longer workflows",
    "L9": "The human owns judgment and accountability; the agent owns execution and feedback",
    "L10": "The method can be copied reliably across a team or clients",
}

XIANXIA_REALM = {
    "L1": "炼气",
    "L2": "筑基",
    "L3": "虚丹",
    "L4": "金丹",
    "L5": "元婴",
    "L6": "化神",
    "L7": "炼虚",
    "L8": "合体",
    "L9": "大乘",
    "L10": "渡劫",
}

XIANXIA_COPY = {
    "L1": "初入道门，气海未稳（还停在随手问答，缺少稳定方法）",
    "L2": "已会引气入体，开始知法门轻重（知道提问方式会影响结果）",
    "L3": "神念初聚，可独驭一具傀儡（能稳定完成简单任务）",
    "L4": "神识强大，可同时控制多个傀儡干活（常见任务可以推进到多步完成）",
    "L5": "金丹温养，已懂炼制传承玉简（开始把顺手打法沉成 skill、模板或模块）",
    "L6": "元婴出窍，可放分身先行探路（已经有能替自己先干一段活的分身）",
    "L7": "化神坐镇，可统御多路傀儡与法阵（能调多 agent、多工具协同完成任务）",
    "L8": "炼虚观势，开始布置长期护山大阵（开始做能力层和长期工作流设计）",
    "L9": "合体掌局，人守道统，傀儡行万事（人负责判断和担责，agent 负责执行和回流）",
    "L10": "大乘立宗，可将修行法门稳定传给众人（能把自己的方法稳定复制给团队或客户）",
}

XIANXIA_COPY_EN = {
    "L1": "New to the path, with unstable qi flow (still mostly ad hoc prompting without a stable method)",
    "L2": "Has learned to gather qi and recognize the weight of different prompt choices",
    "L3": "Spiritual sense is forming; can direct a single puppet through simple work",
    "L4": "Spiritual sense is strong enough to command multiple puppets at once (common tasks can be pushed through multi-step execution)",
    "L5": "The golden core is warming; repeatable methods are starting to become scrolls and techniques",
    "L6": "A nascent soul can move ahead first; an agent can already take a chunk of work on its own",
    "L7": "The cultivator can command multiple puppets and formations across one task",
    "L8": "Attention shifts from one fight to longer capability design and durable systems",
    "L9": "The human guards judgment and accountability; the puppets execute and return results",
    "L10": "The path is mature enough to be passed on reliably to a team or to clients",
}

# Stylized 16-star path for Kui (奎宿), a Chinese lunar mansion with 16 stars.
KUI_ASTERISM_POINTS = [
    (0.06, 0.58),
    (0.16, 0.46),
    (0.28, 0.34),
    (0.40, 0.24),
    (0.52, 0.14),
    (0.58, 0.24),
    (0.64, 0.36),
    (0.70, 0.48),
    (0.76, 0.60),
    (0.70, 0.66),
    (0.62, 0.70),
    (0.52, 0.74),
    (0.42, 0.82),
    (0.30, 0.90),
    (0.18, 0.96),
    (0.10, 0.86),
]


@dataclass(slots=True)
class CardData:
    title: str
    level_label: str
    level: str
    palette_level: str
    summary: str
    platform_model_label: str
    platform_model: str
    user_name: str
    time_label: str
    generated_at: str
    constellation_label: str
    constellation_note: str
    axis_scores: list[int]


DISPLAY_FONT_STACK = "'SF Pro Display', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif"
BODY_FONT_STACK = "'SF Pro Text', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif"


def card_render_environment() -> dict[str, object]:
    backend = _detect_png_backend()
    return {
        "platform": platform.system(),
        "python": sys.version.split()[0],
        "svg_supported": True,
        "png_supported": backend is not None,
        "png_backend": backend or "none",
        "display_font_stack": DISPLAY_FONT_STACK,
        "body_font_stack": BODY_FONT_STACK,
        "font_note": "Best fidelity with SF Pro installed. Fallbacks are PingFang SC, Helvetica Neue, Arial, and sans-serif.",
    }


def write_cards(
    payload: dict[str, object],
    output_dir: str | Path,
    certificate_choice: str = "both",
    style: str = "default",
    locale: str = "zh",
) -> dict[str, str]:
    del certificate_choice
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    basename = "vibecoding-card" if style != "xianxia" else "vibecoding-card-xianxia"
    if locale == "en":
        basename = f"{basename}-en"
    svg_path = target_dir / f"{basename}.svg"
    png_path = target_dir / f"{basename}.png"
    svg_path.write_text(render_vibecoding_card(payload, style=style, locale=locale), encoding="utf-8")
    _render_png(svg_path, png_path)
    return {"card_svg": str(svg_path), "card_png": str(png_path)}


def render_vibecoding_card(payload: dict[str, object], *, style: str = "default", locale: str = "zh") -> str:
    data = build_card_data(payload, style=style, locale=locale)
    palette = get_luogu_level_palette(data.palette_level)
    summary_lines = _wrap_text(data.summary, max_units=18.5, limit=2)

    return f"""<svg width="1200" height="1600" viewBox="0 0 1200 1600" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style><![CDATA[
{_font_face_css()}
    ]]></style>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="1600" gradientUnits="userSpaceOnUse">
      <stop stop-color="#06080B"/>
      <stop offset="1" stop-color="{_escape(_mix_hex(palette['surface'], '#06080B', 0.46))}"/>
    </linearGradient>
    <radialGradient id="aura" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(810 224) rotate(140) scale(418 312)">
      <stop stop-color="{_escape(_mix_hex(palette['glow'], '#FFFFFF', 0.24))}" stop-opacity="0.88"/>
      <stop offset="1" stop-color="{_escape(palette['base'])}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="auraBottom" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(170 1400) rotate(-28) scale(356 248)">
      <stop stop-color="{_escape(palette['base'])}" stop-opacity="0.24"/>
      <stop offset="1" stop-color="{_escape(palette['base'])}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="panel" x1="122" y1="86" x2="1082" y2="1506" gradientUnits="userSpaceOnUse">
      <stop stop-color="{_escape(_mix_hex(palette['surface_alt'], '#FFFFFF', 0.12))}" stop-opacity="0.96"/>
      <stop offset="1" stop-color="{_escape(_mix_hex(palette['surface'], '#06080B', 0.18))}" stop-opacity="0.98"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="#FFFFFF" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.04"/>
    </linearGradient>
    <filter id="shadow" x="70" y="42" width="1060" height="1518" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset dy="24"/>
      <feGaussianBlur stdDeviation="26"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.01 0 0 0 0 0.02 0 0 0 0 0.04 0 0 0 0.52 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_0_1"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_0_1" result="shape"/>
    </filter>
  </defs>

  <rect width="1200" height="1600" fill="url(#bg)"/>
  <circle cx="810" cy="224" r="300" fill="url(#aura)"/>
  <circle cx="170" cy="1400" r="240" fill="url(#auraBottom)"/>

  <g filter="url(#shadow)">
    <rect x="100" y="72" width="1000" height="1456" rx="44" fill="url(#panel)" stroke="{_escape(_with_alpha(palette['line'], 0.48))}" stroke-width="1.5"/>
    <rect x="101" y="73" width="998" height="1454" rx="43" stroke="rgba(255,255,255,0.06)"/>
  </g>

  <rect x="140" y="108" width="920" height="2" rx="1" fill="{_escape(_mix_hex(palette['glow'], '#FFFFFF', 0.20))}" fill-opacity="0.88"/>
  <text x="160" y="174" fill="#FFFFFF" font-size="36" font-family="{_display_font()}" font-weight="700">{_escape(data.title)}</text>

  <g>
    <rect x="487" y="260" width="226" height="54" rx="27" fill="url(#glass)" stroke="{_escape(_with_alpha(palette['line'], 0.60))}"/>
    <text x="600" y="296" fill="#FFFFFF" font-size="28" text-anchor="middle" font-family="{_body_font()}" font-weight="600">{_escape(data.level_label)}</text>
  </g>

  <text x="600" y="598" fill="#FFFFFF" font-size="300" text-anchor="middle" font-family="{_display_font()}" font-weight="700" letter-spacing="-10">{_escape(data.level)}</text>
  {_text_lines(summary_lines, x=600, y=704, font_size=44, line_height=56, fill="#F5F7FA", anchor="middle", family=_body_font(), weight="600")}

  <line x1="170" y1="932" x2="1030" y2="932" stroke="{_escape(_with_alpha(palette['line'], 0.42))}" stroke-width="1.5"/>

  <text x="170" y="1010" fill="{_escape(_with_alpha(palette['glow'], 0.90))}" font-size="24" font-family="{_body_font()}" font-weight="500">{_escape(data.platform_model_label)}</text>
  <text x="170" y="1072" fill="#FFFFFF" font-size="40" font-family="{_display_font()}" font-weight="650">{_escape(data.platform_model)}</text>

  <line x1="170" y1="1164" x2="1030" y2="1164" stroke="{_escape(_with_alpha(palette['line'], 0.28))}"/>

  {_render_constellation(data, palette)}

  <text x="670" y="1266" fill="#FFFFFF" font-size="56" font-family="{_display_font()}" font-weight="650">{_escape(data.user_name)}</text>
  <text x="670" y="1332" fill="{_escape(_with_alpha(palette['glow'], 0.90))}" font-size="24" font-family="{_body_font()}" font-weight="500">{_escape(data.time_label)}</text>
  <text x="670" y="1390" fill="#FFFFFF" font-size="34" font-family="{_body_font()}" font-weight="600">{_escape(data.generated_at)}</text>

</svg>
"""


def build_card_data(payload: dict[str, object], *, style: str = "default", locale: str = "zh") -> CardData:
    insights = _as_dict(payload.get("insights"))
    transcript = _as_dict(payload.get("transcript"))
    rank = str(insights.get("rank") or "L1")
    source_platform = _source_platform(payload)
    model = _primary_model(payload)
    platform_model = source_platform if model == source_platform else f"{source_platform} · {model}"
    english = locale == "en"
    if style == "xianxia":
        return CardData(
            title="vibecoding.skill",
            level_label="Realm" if english else "境界",
            level=rank if english else XIANXIA_REALM.get(rank, rank),
            palette_level=rank,
            summary=(XIANXIA_COPY_EN if english else XIANXIA_COPY).get(rank, (XIANXIA_COPY_EN if english else XIANXIA_COPY)["L1"]),
            platform_model_label="Sect and Artifacts" if english else "宗门和法宝",
            platform_model=platform_model,
            user_name=_truncate_text(str(transcript.get("display_name") or payload.get("display_name") or default_display_name("user")), 16),
            time_label="Return Time" if english else "出关时间",
            generated_at=_format_generated_at(payload.get("generated_at")),
            constellation_label="16-Star Map · Kui" if english else "十六曜星图 · 奎宿",
            constellation_note="Brightness follows the 16 dimension scores" if english else "亮度随 16 维得分变化",
            axis_scores=_axis_scores(payload),
        )
    return CardData(
        title="vibecoding.skill",
        level_label="Level" if english else "等级",
        level=rank,
        palette_level=rank,
        summary=(LEVEL_COPY_EN if english else LEVEL_COPY).get(rank, (LEVEL_COPY_EN if english else LEVEL_COPY)["L1"]),
        platform_model_label="Platforms and Models" if english else "常用平台和模型",
        platform_model=platform_model,
        user_name=_truncate_text(str(transcript.get("display_name") or payload.get("display_name") or default_display_name("user")), 16),
        time_label="Time" if english else "时间",
        generated_at=_format_generated_at(payload.get("generated_at")),
        constellation_label="16-Dimension Star Map · Kui" if english else "十六维星图 · 奎宿",
        constellation_note="Brightness follows the 16 dimension scores" if english else "亮度随 16 维得分变化",
        axis_scores=_axis_scores(payload),
    )


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


def _render_constellation(data: CardData, palette: dict[str, str]) -> str:
    left = 162
    top = 1226
    width = 392
    height = 212
    path_points = []
    stars = []
    for index, (px, py) in enumerate(KUI_ASTERISM_POINTS):
        x = left + px * width
        y = top + py * height
        path_points.append(f"{x:.1f},{y:.1f}")
        score = data.axis_scores[index] if index < len(data.axis_scores) else 0
        opacity = _star_opacity(score)
        radius = 2.9 + score * 1.15
        glow_radius = radius + 6.0
        halo = (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius + 2.2:.1f}" '
            f'fill="none" stroke="{_escape(_with_alpha(palette["glow"], max(0.12, opacity * 0.48)))}" '
            f'stroke-width="0.8"/>'
            if score >= 3
            else ""
        )
        stars.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{glow_radius:.1f}" fill="{_escape(_with_alpha(palette["glow"], opacity * 0.30))}"/>'
            f'{halo}'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{_escape(_with_alpha("#FFFFFF", max(0.42, opacity)))}"/>'
        )
    return (
        f'<text x="{left}" y="1210" fill="{_escape(_with_alpha(palette["glow"], 0.92))}" font-size="22" font-family="{_body_font()}" font-weight="600">{_escape(data.constellation_label)}</text>'
        f'<ellipse cx="{left + width * 0.42:.1f}" cy="{top + height * 0.60:.1f}" rx="{width * 0.44:.1f}" ry="{height * 0.46:.1f}" fill="{_escape(_with_alpha(palette["base"], 0.08))}"/>'
        f'<ellipse cx="{left + width * 0.32:.1f}" cy="{top + height * 0.72:.1f}" rx="{width * 0.22:.1f}" ry="{height * 0.18:.1f}" fill="{_escape(_with_alpha(palette["glow"], 0.05))}"/>'
        f'<polyline points="{" ".join(path_points)}" fill="none" stroke="{_escape(_with_alpha(palette["base"], 0.22))}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="3 14"/>'
        f'<polyline points="{" ".join(path_points)}" fill="none" stroke="{_escape(_with_alpha(palette["line"], 0.64))}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 9"/>'
        + "".join(stars)
        + f'<text x="{left}" y="1472" fill="{_escape(_with_alpha(palette["line"], 0.82))}" font-size="18" font-family="{_body_font()}" font-weight="500">{_escape(data.constellation_note)}</text>'
    )


def _star_opacity(score: int) -> float:
    return {
        0: 0.12,
        1: 0.28,
        2: 0.48,
        3: 0.72,
        4: 1.0,
    }.get(score, 0.12)


def _wrap_text(text: str, max_units: float, limit: int) -> list[str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []
    lines: list[str] = []
    current = ""
    current_units = 0.0
    for token in _tokenize_for_wrap(cleaned):
        token_units = _text_units(token)
        if current and current_units + token_units > max_units:
            lines.append(current)
            current = token
            current_units = token_units
            if len(lines) >= limit:
                break
            continue
        if current and _needs_wrap_space(current[-1], token[0]):
            current += " "
            current_units += 0.35
        current += token
        current_units += token_units
    if current and len(lines) < limit:
        lines.append(current)
    if len(lines) == limit and _text_units(cleaned) > sum(_text_units(line) for line in lines):
        lines[-1] = _truncate_text(lines[-1], int(max_units) - 1)
    return lines


def _tokenize_for_wrap(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    suffix = "，。！？；：、）》」』】)"
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char in suffix and tokens:
            tokens[-1] += char
            index += 1
            continue
        if ord(char) < 128:
            end = index + 1
            while end < len(text) and ord(text[end]) < 128 and not text[end].isspace():
                end += 1
            tokens.append(text[index:end])
            index = end
            continue
        tokens.append(char)
        index += 1
    return tokens


def _needs_wrap_space(left: str, right: str) -> bool:
    return ord(left) < 128 and ord(right) < 128 and left.isalnum() and right.isalnum()


def _text_units(text: str) -> float:
    total = 0.0
    for char in text:
        if char.isspace():
            total += 0.35
        elif ord(char) < 128:
            total += 0.58
        else:
            total += 1.0
    return total


def _truncate_text(text: str, limit_units: int) -> str:
    total = 0.0
    result: list[str] = []
    for char in text:
        units = 0.58 if ord(char) < 128 else 1.0
        if total + units > limit_units:
            result.append("…")
            break
        result.append(char)
        total += units
    return "".join(result)


def _axis_scores(payload: dict[str, object]) -> list[int]:
    secondary = _as_dict(payload.get("secondary_skill"))
    axes = secondary.get("axes")
    if isinstance(axes, list):
        scores = [int(_as_dict(axis).get("score", 0) or 0) for axis in axes]
        if scores:
            return (scores + [0] * 16)[:16]
    return [0] * 16


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


def _format_generated_at(value: object) -> str:
    return str(value or "").strip().replace("T", " ").replace("+08:00", "").replace("+00:00", " UTC")


def _display_font() -> str:
    return "'CardDisplay', 'CardCJK', 'CardUnicode', " + DISPLAY_FONT_STACK


def _body_font() -> str:
    return "'CardBody', 'CardCJK', 'CardUnicode', " + BODY_FONT_STACK


def _font_face_css() -> str:
    candidates = [
        ("CardDisplay", Path("/System/Library/Fonts/SFNS.ttf")),
        ("CardBody", Path("/System/Library/Fonts/SFNS.ttf")),
        ("CardCJK", Path("/System/Library/Fonts/Hiragino Sans GB.ttc")),
        ("CardUnicode", Path("/Library/Fonts/Arial Unicode.ttf")),
    ]
    rules: list[str] = []
    for family, path in candidates:
        if path.exists():
            rules.append(
                f"      @font-face {{ font-family: '{family}'; src: url('{path.expanduser().resolve().as_uri()}'); }}"
            )
    return "\n".join(rules)


def _mix_hex(left: str, right: str, ratio: float) -> str:
    ratio = max(0.0, min(1.0, ratio))
    left_rgb = _hex_to_rgb(left)
    right_rgb = _hex_to_rgb(right)
    mixed = tuple(round(left_rgb[index] + (right_rgb[index] - left_rgb[index]) * ratio) for index in range(3))
    return _rgb_to_hex(mixed)


def _with_alpha(color: str, alpha: float) -> str:
    red, green, blue = _hex_to_rgb(color)
    return f"rgba({red},{green},{blue},{max(0.0, min(1.0, alpha)):.2f})"


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    normalized = value.lstrip("#")
    return tuple(int(normalized[index : index + 2], 16) for index in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _escape(value: str) -> str:
    return escape(value, quote=True)


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _render_png(svg_path: Path, png_path: Path) -> None:
    backend = _detect_png_backend()
    if backend == "cairosvg":
        import cairosvg

        cairosvg.svg2png(bytestring=svg_path.read_bytes(), write_to=str(png_path), dpi=300)
        _normalize_png_dpi(png_path)
        return
    if backend == "rsvg-convert":
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
        _normalize_png_dpi(png_path)
        return
    raise RuntimeError(
        "PNG card rendering is unavailable. Install Python package 'cairosvg' or command 'rsvg-convert'. "
        "SVG output remains available on all platforms."
    )


def _detect_png_backend() -> str | None:
    if shutil.which("rsvg-convert"):
        return "rsvg-convert"
    try:
        import cairosvg  # noqa: F401

        return "cairosvg"
    except ImportError:
        pass
    return None


def _normalize_png_dpi(png_path: Path) -> None:
    try:
        from PIL import Image

        with Image.open(png_path) as image:
            image.save(png_path, dpi=(300, 300))
    except Exception:
        pass
