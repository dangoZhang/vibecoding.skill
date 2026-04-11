from __future__ import annotations

import json
import zipfile
from pathlib import Path

from .cards import write_cards


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
    result_skill_label = _result_skill_label(display_name)
    assets_dir = root / "assets"
    cards = write_cards(payload, assets_dir, style=card_style)

    report_path = root / "REPORT.md"
    profile_path = root / "PROFILE.md"
    skill_path = root / "SKILL.md"
    readme_path = root / "README.md"
    json_path = root / "snapshot.json"

    report_path.write_text(markdown, encoding="utf-8")
    profile_path.write_text(_render_profile(payload), encoding="utf-8")
    skill_path.write_text(_render_skill(payload, result_skill_label), encoding="utf-8")
    readme_path.write_text(_render_readme(payload, result_skill_label), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {
        "export_dir": str(root),
        "share_skill_dir": str(root),
        "result_skill_name": result_skill_label,
        "share_readme": str(readme_path),
        "share_profile": str(profile_path),
        "share_report": str(report_path),
        "share_json": str(json_path),
        "card_svg": cards["card_svg"],
        "card_png": cards["card_png"],
    }
    if archive:
        zip_path = root.parent / f"{root.name}.zip"
        _zip_dir(root, zip_path)
        result["share_zip"] = str(zip_path)
    return result


def _render_readme(payload: dict[str, object], result_skill_label: str) -> str:
    name = _display_name(payload)
    rank = _insight(payload, "rank", "L1")
    ability = _insight(payload, "ability_text", "这套协作还在试手期。")
    generated_at = str(payload.get("generated_at") or "")
    usage_line = _insight(payload, "usage_line", "")
    habit_lines = _list_insight(payload, "habit_profile_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    lines = [
        f"# {name} 的 vibecoding 导出包",
        "",
        f"这是从真实协作记录里导出的共享包，当前判断为 `{rank}`。",
        "",
        f"这份导出包会保留 {name} 和 AI 协作时最稳定的节奏，方便交给另一个也在用 vibecoding.skill 的人继续复用。",
        "",
        "## 分享哪个文件",
        "",
        "- 想让另一个也在用 vibecoding.skill 的人直接复用：分享整个目录，或压缩后的 zip。",
        "- 想让别人快速看懂这套做法：分享 `PROFILE.md`。",
        "- 想让别人看完整判断依据：分享 `REPORT.md`。",
        "- 想发群或发社交平台：分享 `assets/vibecoding-card.png`。",
        "",
        "## 这包里有什么",
        "",
        f"- `SKILL.md`：蒸馏结果 skill，本包核心入口，对应 `{result_skill_label}`。",
        "- `PROFILE.md`：压缩后的习惯画像，适合转发和快速阅读。",
        "- `REPORT.md`：完整报告，包含判断依据和突破建议。",
        "- `snapshot.json`：结构化结果，方便二次开发。",
        "- `assets/`：分享卡图片。",
        "",
        "## 这套习惯的摘要",
        "",
        f"- 等级：`{rank}`",
        f"- 判断：{ability}",
    ]
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
            f"`vibecoding.skill` 是入口 skill，`{result_skill_label}` 是这次蒸馏出来的结果 skill。",
            "",
            "1. 把整个目录或 zip 发给接收方。",
            "2. 接收方在自己的对话里把这份导出包交给 `vibecoding.skill`。",
            f"3. 让 `vibecoding.skill` 先读取并调用 `{result_skill_label}`。",
            "4. 再按这套方式继续协作。",
            "",
            "## 接收方可以直接说",
            "",
            f"- 这是同事的导出包。先读他的画像，再调用 `{result_skill_label}` 和我一起做当前任务。",
            f"- 先按这份导出包总结协作习惯，再切到 `{result_skill_label}` 开始当前任务。",
            "- 按这份画像指出我最该补的动作。",
            "- 结合这份画像，继续帮我把 AI 融入现在的工作流程。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _render_skill(payload: dict[str, object], result_skill_label: str) -> str:
    name = _display_name(payload)
    rank = _insight(payload, "rank", "L1")
    habit_lines = _list_insight(payload, "habit_profile_lines")
    mimic_lines = _list_insight(payload, "mimic_lines")
    breakthrough_lines = _list_insight(payload, "breakthrough_lines")
    coaching_lines = _list_insight(payload, "coaching_focus_lines") + _list_insight(payload, "coaching_drill_lines")
    prompt_examples = [
        f"按 {name} 这套 vibecoding 习惯和我一起推进这个任务。",
        f"先模仿 {name} 的协作方式，再开始当前项目。",
        "结合这份画像，继续帮我把 AI 融入现在的工作流程。",
        "如果这套做法里有明显短板，边做边提醒我，不要等到最后再说。",
    ]
    lines = [
        "---",
        f"name: {result_skill_label}",
        f"description: 这是从{name}的真实记录蒸馏出的结果 skill，供 vibecoding.skill 读取或直接调用，用来复用这套协作方式。",
        "---",
        "",
        f"# {result_skill_label}",
        "",
        "## 这是什么",
        "",
        f"- 这是从 {name} 的真实协作记录蒸馏出来的结果 skill。",
        "- 它不负责重新蒸馏新记录；蒸馏入口仍然是 `vibecoding.skill`。",
        f"- `vibecoding.skill` 负责读取记录、生成报告、导出结果 skill，以及在收到这份 skill 时接管并调用 `{result_skill_label}`。",
        "",
        "## Read First",
        "",
        "先读 [PROFILE.md](./PROFILE.md) 和 [REPORT.md](./REPORT.md)。",
        "",
        "## When To Use",
        "",
        f"- 当用户说“按 {result_skill_label} 和我一起做事”时，直接使用这份结果 skill。",
        "- 当用户把这份导出包交给 `vibecoding.skill` 时，应先读画像，再切到这份结果 skill。",
        "",
        "## Default Behavior",
        "",
        f"默认按这份画像里的协作节奏工作，当前参考等级是 `{rank}`。",
        "- 开局先收束目标、上下文、约束和验收。",
        "- 能直接执行就直接执行。",
        "- 保留这套习惯里的强项，主动提醒短板。",
        "- 每轮完成后回看一次：做了什么、怎么验证、下一步是什么。",
        "",
        "## Distilled Habits",
        "",
    ]
    for item in habit_lines:
        lines.append(f"- {item}")
    if mimic_lines:
        lines.extend(["", "## How To Mimic"])
        for item in mimic_lines:
            lines.append(f"- {item}")
    if breakthrough_lines or coaching_lines:
        lines.extend(["", "## How To Improve"])
        for item in breakthrough_lines + coaching_lines:
            lines.append(f"- {item}")
    lines.extend(["", "## Called By vibecoding.skill", ""])
    lines.append(f"- 当 `vibecoding.skill` 收到这份导出包时，应先读取 `PROFILE.md` 和 `REPORT.md`，再调用 `{result_skill_label}` 作为当前协作方式。")
    lines.append("- 如果当前仓库指令和这份结果 skill 冲突，以更高优先级指令为准。")
    lines.extend(["", "## Share And Reuse", ""])
    lines.append("- 这份导出包优先用于两个都在用 skills 宿主的人之间共享协作方式。")
    lines.append("- 用户想继承他人的做法时，先读 `PROFILE.md` 和 `REPORT.md`，再按里面的节奏协作。")
    lines.extend(["", "## Good Prompts", ""])
    lines.append(f"- 调用 `{result_skill_label}`，按这套协作方式和我一起做当前任务。")
    lines.append(f"- 这是同事的导出包。先读画像，再切到 `{result_skill_label}` 开始协作。")
    for item in prompt_examples:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- 如果当前用户、仓库或系统指令和这份画像冲突，以更高优先级指令为准。",
            "- 事实不够时先补信息，不要硬装得像。",
            "- 这份 skill 关注的是协作节奏复用，不要把它写成人格扮演。",
        ]
    )
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
def _result_skill_label(display_name: str) -> str:
    clean = display_name.strip() or "distilled"
    return clean if clean.endswith(".skill") else f"{clean}.skill"


def _zip_dir(root: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            archive.write(path, arcname=path.relative_to(root.parent))
