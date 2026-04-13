from __future__ import annotations

import json
import zipfile
from pathlib import Path

from .cards import write_cards
from .secondary_skill import (
    build_readme_profile_panel,
    render_secondary_skill_markdown,
    result_skill_slug,
    result_skill_title_from_display,
)


def export_bundle(
    *,
    payload: dict[str, object],
    markdown: str,
    output_dir: str | Path,
    card_style: str = "default",
    archive: bool = False,
    slug: str | None = None,
) -> dict[str, str]:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    display_name = _display_name(payload)
    result_skill_name = result_skill_slug(slug or display_name)
    result_skill_title = result_skill_title_from_display(display_name)
    assets_dir = root / "assets"
    cards = write_cards(payload, assets_dir, style=card_style)
    card_png_name = Path(cards["card_png"]).name

    report_path = root / "REPORT.md"
    profile_path = root / "PROFILE.md"
    skill_path = root / "SKILL.md"
    readme_path = root / "README.md"
    team_guide_path = root / "TEAM_GUIDE.md"
    starters_path = root / "PROMPT_STARTERS.md"
    json_path = root / "snapshot.json"
    secondary_path = root / "DISTILLED_SKILL.json"
    cursor_rules_dir = root / ".cursor" / "rules"
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)
    cursor_rule_path = cursor_rules_dir / f"{result_skill_name}.mdc"

    report_path.write_text(markdown, encoding="utf-8")
    profile_path.write_text(_render_profile(payload), encoding="utf-8")
    skill_path.write_text(_render_skill(payload, result_skill_name), encoding="utf-8")
    readme_path.write_text(_render_readme(payload, result_skill_name, result_skill_title, card_png_name), encoding="utf-8")
    team_guide_path.write_text(_render_team_guide(payload, result_skill_name), encoding="utf-8")
    starters_path.write_text(_render_prompt_starters(payload, result_skill_name), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    secondary_path.write_text(json.dumps(_secondary_skill(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    cursor_rule_path.write_text(_render_cursor_rule(payload, result_skill_name), encoding="utf-8")

    result = {
        "export_dir": str(root),
        "share_skill_dir": str(root),
        "result_skill_name": result_skill_name,
        "result_skill_title": result_skill_title,
        "share_readme": str(readme_path),
        "share_profile": str(profile_path),
        "share_report": str(report_path),
        "team_guide": str(team_guide_path),
        "prompt_starters": str(starters_path),
        "share_json": str(json_path),
        "distilled_skill_json": str(secondary_path),
        "cursor_rule": str(cursor_rule_path),
        "card_svg": cards["card_svg"],
        "card_png": cards["card_png"],
    }
    if archive:
        zip_path = root.parent / f"{root.name}.zip"
        _zip_dir(root, zip_path)
        result["share_zip"] = str(zip_path)
    return result


def _render_readme(payload: dict[str, object], result_skill_name: str, result_skill_title: str, card_png_name: str) -> str:
    name = _display_name(payload)
    rank = _insight(payload, "rank", "L1")
    ability = _insight(payload, "ability_text", "这套协作还在试手期。")
    generated_at = str(payload.get("generated_at") or "")
    usage_line = _insight(payload, "usage_line", "")
    habit_lines = _list_insight(payload, "habit_profile_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    panel = build_readme_profile_panel(payload)
    lines = [
        f"# {name} 的 vibecoding 导出包",
        "",
        f"这是从真实协作记录里导出的共享包，当前判断为 `{rank}`。",
        "",
        f"这份导出包会保留 {name} 和 AI 协作时最稳定的节奏，方便交给另一个也在用 vibecoding.skill 的人继续复用。",
        "",
        "<table>",
        "<tr>",
        '<td width="54%" valign="top">',
        "",
        f"### {panel.get('title', '这套 vibecoding 像什么')}",
        "",
    ]
    for tag in panel.get("tags", []):
        lines.append(f"`{tag}` ")
    if panel.get("tags"):
        lines.append("")
    for paragraph in panel.get("paragraphs", []):
        lines.extend([paragraph, ""])
    for bullet in panel.get("bullets", []):
        lines.append(f"- {bullet}")
    lines.extend(
        [
            "",
            "</td>",
            '<td width="46%" valign="top">',
            "",
            f'<img src="./assets/{card_png_name}" alt="vibecoding 分享卡" width="100%" />',
            "",
            "</td>",
            "</tr>",
            "</table>",
            "",
            "## 分享哪个文件",
            "",
            "- 想让另一个也在用 vibecoding.skill 的人直接复用：分享整个目录，或压缩后的 zip。",
            "- 想让别人快速看懂这套做法：分享 `PROFILE.md`。",
            "- 想让别人看完整判断依据：分享 `REPORT.md`。",
            f"- 想发群或发社交平台：分享 `assets/{card_png_name}`。",
            "",
            "## 这包里有什么",
            "",
            f"- `SKILL.md`：蒸馏结果 skill，本包核心入口。调用名是 `{result_skill_name}`，显示标题是 `{result_skill_title}`。",
            f"- `.cursor/rules/{result_skill_name}.mdc`：给 Cursor 原生读取。",
            "- `PROFILE.md`：压缩后的习惯画像，适合转发和快速阅读。",
            "- `REPORT.md`：完整报告，包含判断依据和突破建议。",
            "- `TEAM_GUIDE.md`：给不熟 AI 的同事看的上手说明，直接告诉他怎么提需求、怎么看结果。",
            "- `PROMPT_STARTERS.md`：几组可直接复制的起手模板，覆盖修 bug、读仓库、写文档、review、排障。",
            "- `snapshot.json`：结构化结果，方便二次开发。",
            "- `DISTILLED_SKILL.json`：16 维蒸馏主判结果，内含语义分桶证据和供 LLM 做二次综合的 prompt。",
            "- `assets/`：分享卡图片。",
            "",
            "## 这套习惯的摘要",
            "",
            "- 画像来源：先做 16 维蒸馏，报告、README、共享页和导出包都只从这份主判结果派生。",
            f"- 等级：`{rank}`",
            f"- 判断：{ability}",
        ]
    )
    if usage_line:
        lines.append(f"- 取样规模：`{usage_line}`")
    if generated_at:
        lines.append(f"- 导出时间：`{generated_at}`")
    if habit_lines:
        lines.extend(["", "## 这套 vibecoding 习惯", ""])
        for item in habit_lines:
            lines.append(f"- {item}")
    if breakthrough_lines:
        lines.extend(["", "## 下一步怎么把 AI 接得更深", ""])
        for item in breakthrough_lines[:3]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 接收方怎么用",
            "",
            "更顺手的场景是双方都已经在自己的宿主里装了 `vibecoding.skill`。",
            f"`vibecoding.skill` 是入口 skill，这次蒸馏出的结果 skill 调用名是 `{result_skill_name}`。",
            "",
            "1. 把整个目录或 zip 发给接收方。",
            "2. 接收方在自己的对话里把这份导出包交给 `vibecoding.skill`。",
            f"3. 让 `vibecoding.skill` 先读取并调用 `{result_skill_name}`。",
            "4. 再按这套方式继续协作。",
            "",
            "## 接收方可以直接说",
            "",
            f"- 这是同事的导出包。先读他的画像，再调用 `{result_skill_name}` 和我一起做当前任务。",
            f"- 先按这份导出包总结协作习惯，再切到 `{result_skill_name}` 开始当前任务。",
            "- 按这份画像指出我最该补的动作。",
            "- 结合这份画像，继续帮我把 AI 融入现在的工作流程。",
            "- 如果你不熟 AI，先看 `TEAM_GUIDE.md`，再从 `PROMPT_STARTERS.md` 里复制一个模板开始。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _render_skill(payload: dict[str, object], result_skill_name: str) -> str:
    secondary = _secondary_skill(payload)
    lines = [
        "---",
        f"name: {result_skill_name}",
        f"description: 这是从{_display_name(payload)}的真实记录蒸馏出的结果 skill，供 vibecoding.skill 读取或直接调用，用来复用这套协作方式。",
        "---",
        "",
        render_secondary_skill_markdown(secondary).strip(),
        "",
        "## Called By vibecoding.skill",
        "",
        f"- 当 `vibecoding.skill` 收到这份导出包时，应先读取 `PROFILE.md`、`REPORT.md`、`DISTILLED_SKILL.json`，再调用 `{result_skill_name}`。",
        "- 如果当前仓库指令和这份结果 skill 冲突，以更高优先级指令为准。",
    ]
    return "\n".join(lines).strip() + "\n"


def _render_cursor_rule(payload: dict[str, object], result_skill_name: str) -> str:
    secondary = _secondary_skill(payload)
    contract = secondary.get("secondary_skill_contract") if isinstance(secondary, dict) else {}
    if not isinstance(contract, dict):
        contract = {}
    lines = [
        "---",
        f"description: Use {result_skill_name} as a native Cursor project rule for this distilled vibecoding style.",
        "alwaysApply: false",
        "---",
        "",
        f"# {result_skill_name}",
        "",
        "按这份导出包里的 vibecoding 习惯推进任务，不做人设扮演。",
        "",
        "## Default Behavior",
        "",
    ]
    for item in contract.get("default_behavior", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Guardrails", ""])
    for item in contract.get("guardrails", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Prompt Examples", ""])
    for item in contract.get("prompt_examples", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Prompt Rewrite", ""])
    for item in contract.get("prompt_rewrite_rules", []):
        lines.append(f"- {item}")
    for item in contract.get("prompt_rewrite_examples", []):
        lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _render_profile(payload: dict[str, object]) -> str:
    name = _display_name(payload)
    rank = _insight(payload, "rank", "L1")
    stage = _insight(payload, "stage", "试手期")
    ability = _insight(payload, "ability_text", "还在试手。")
    usage_line = _insight(payload, "usage_line", "")
    generated_at = str(payload.get("generated_at") or "")
    habit_lines = _list_insight(payload, "habit_profile_lines")
    mimic_lines = _list_insight(payload, "mimic_lines")
    verdict_lines = _list_insight(payload, "verdict_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    modern_lines = _list_insight(payload, "modern_signal_lines")
    user_summary = _list_insight(payload, "user_summary_lines")
    assistant_summary = _list_insight(payload, "assistant_summary_lines")
    model_name = _primary_model(payload)

    lines = [
        f"# {name} 的 vibecoding 画像",
        "",
        f"- 等级：`{rank}`",
        f"- 阶段：`{stage}`",
        f"- 主用模型：`{model_name}`",
        f"- 能力摘要：{ability}",
    ]
    if usage_line:
        lines.append(f"- 取样规模：`{usage_line}`")
    if generated_at:
        lines.append(f"- 生成时间：`{generated_at}`")
    if habit_lines:
        lines.extend(["", "## 这套习惯是什么"])
        for item in habit_lines:
            lines.append(f"- {item}")
    if user_summary or assistant_summary:
        lines.extend(["", "## 关键观察"])
        for item in user_summary + assistant_summary:
            lines.append(f"- {item}")
    if verdict_lines:
        lines.extend(["", "## 判词"])
        for item in verdict_lines:
            lines.append(f"- {item}")
    if mimic_lines:
        lines.extend(["", "## 如果想模仿这套做法"])
        for item in mimic_lines:
            lines.append(f"- {item}")
    if breakthrough_lines:
        lines.extend(["", "## 如果想继续升级"])
        for item in breakthrough_lines:
            lines.append(f"- {item}")
    if modern_lines:
        lines.extend(["", "## 现代协作信号"])
        for item in modern_lines:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _render_team_guide(payload: dict[str, object], result_skill_name: str) -> str:
    name = _display_name(payload)
    habit_lines = _list_insight(payload, "habit_profile_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    coaching_lines = _list_insight(payload, "coaching_prompt_lines")
    lines = [
        f"# {name} 团队使用说明",
        "",
        "这份说明是给不熟 AI 或刚开始用 AI Agent 的同事看的。",
        "目标只有一个：让 AI 更快进入团队节奏，而不是把问题说得更花。",
        "",
        "## 先记住这 4 条",
        "",
        "- 提需求时先说清：目标、边界、输出物、验收。",
        "- 有路径、文件、日志、报错就直接贴，不要让 AI 猜。",
        "- 让 AI 先做，再让它回报，不要先听大段空方案。",
        "- 收尾固定追问：改了什么、怎么验证、还有什么没验。",
        "",
        "## 团队默认节奏",
        "",
    ]
    for item in habit_lines[:3]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 什么任务适合直接交给 AI Agent",
            "",
            "- 修 bug、读仓库、梳理文档、跑测试、看日志、做首轮 review。",
            "- 有明确边界和可验证结果的任务，最适合直接让 AI 先推进一段。",
            "",
            "## 什么任务要人盯住",
            "",
            "- 生产发布、权限变更、不可逆数据操作、法律/财务/医疗类高风险输出。",
            "- 这类任务可以让 AI 先做草稿或检查，但最后决定必须由人确认。",
            "",
            "## 不会用 AI 的同事可以直接复制",
            "",
            f"- 先按 `{result_skill_name}` 这套方式帮我做这件事。目标是____。边界是____。输出物是____。验收标准是____。",
            "- 先读我给你的文件/日志，再开始做。做完后只告诉我：改了什么、怎么验证、还有什么风险。",
        ]
    )
    if coaching_lines or breakthrough_lines:
        lines.extend(["", "## 下一步最值得训练", ""])
        for item in breakthrough_lines[:2] + coaching_lines[:2]:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _render_prompt_starters(payload: dict[str, object], result_skill_name: str) -> str:
    lines = [
        "# Prompt Starters",
        "",
        f"下面这些模板都默认按 `{result_skill_name}` 这套 vibecoding 习惯推进。",
        "",
        "## 修 bug",
        "",
        "```text",
        f"调用 `{result_skill_name}`，帮我修这个仓库里的 bug。目标是恢复____。边界是____不能动。输出物是代码改动和必要文档。验收是____。先读相关文件、跑必要命令、查日志，再直接开始做。最后只按三项回报：改了什么、怎么验证、还有什么没验或有风险。",
        "```",
        "",
        "## 读仓库",
        "",
        "```text",
        f"调用 `{result_skill_name}`，先快速读这个仓库。目标是搞清____。边界是不改代码。输出物是一页结构化总结。验收是我能看懂主模块、关键数据流和风险点。优先读 README、入口文件、核心模块和测试，再给我结论。",
        "```",
        "",
        "## 写文档",
        "",
        "```text",
        f"调用 `{result_skill_name}`，帮我补这份文档。目标是让同事能直接上手____。边界是只补文档，不改业务逻辑。输出物是可提交的 README / SOP。验收是新同事看完能照着做。先读现有文档和相关代码，再开始写。",
        "```",
        "",
        "## 代码 Review",
        "",
        "```text",
        f"调用 `{result_skill_name}`，review 这次改动。重点看技术问题、行为回归、风险和缺失测试。先给 findings，按严重程度排序，再给简短总结。不要泛泛夸好，优先指出真正会出问题的地方。",
        "```",
        "",
        "## 排障 / 看日志",
        "",
        "```text",
        f"调用 `{result_skill_name}`，帮我排这个故障。目标是定位根因并给最短修复路径。边界是先不要大改。输出物是根因、证据、修复建议。验收是能解释为什么出错、如何复现、如何验证修复。先看日志、配置、最近改动，再继续推进。",
        "```",
    ]
    return "\n".join(lines).strip() + "\n"


def _insight(payload: dict[str, object], key: str, default: str) -> str:
    insights = payload.get("insights")
    if isinstance(insights, dict):
        value = insights.get(key)
        if isinstance(value, str) and value:
            return value
    return default


def _list_insight(payload: dict[str, object], key: str) -> list[str]:
    insights = payload.get("insights")
    if not isinstance(insights, dict):
        return []
    value = insights.get(key)
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _display_name(payload: dict[str, object]) -> str:
    for key in ("display_name",):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        value = transcript.get("display_name")
        if isinstance(value, str) and value:
            return value
    return "码奸"


def _secondary_skill(payload: dict[str, object]) -> dict[str, object]:
    value = payload.get("secondary_skill")
    return value if isinstance(value, dict) else {}


def _primary_model(payload: dict[str, object]) -> str:
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        models = transcript.get("models")
        if isinstance(models, list) and models:
            return str(models[0])
    models = payload.get("models")
    if isinstance(models, list) and models:
        top = models[0]
        if isinstance(top, dict):
            return str(top.get("name") or top.get("model") or "未知模型")
        if isinstance(top, str):
            return top
    return "未知模型"
def _zip_dir(root: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            archive.write(path, arcname=path.relative_to(root.parent))
