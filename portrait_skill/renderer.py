from __future__ import annotations

from .models import Analysis, Certificate, MetricScore


def render_markdown(analysis: Analysis, certificate_choice: str = "both") -> str:
    sections = [
        "# portrait.skill 画像报告",
        "",
        "## 会话概览",
        analysis.overview,
        f"- 来源：`{analysis.transcript.source}`",
        f"- 文件：`{analysis.transcript.path}`",
        "",
        "## 维度评分",
        _render_metrics("用户协作维度", analysis.user_metrics),
        "",
        _render_metrics("AI 协作维度", analysis.assistant_metrics),
    ]
    if certificate_choice in {"user", "both"}:
        sections.extend(["", _render_certificate(analysis.user_certificate)])
    if certificate_choice in {"assistant", "both"}:
        sections.extend(["", _render_certificate(analysis.assistant_certificate)])
    return "\n".join(sections).strip() + "\n"


def _render_metrics(title: str, metrics: list[MetricScore]) -> str:
    lines = [f"### {title}"]
    for item in metrics:
        lines.append(f"- {item.name}：`{item.score}/100`，{item.rationale}")
    return "\n".join(lines)


def _render_certificate(certificate: Certificate) -> str:
    lines = [
        f"## {certificate.title}",
        f"**等级**：{certificate.level}",
        f"**总分**：`{certificate.score}/100`",
        f"**画像**：{certificate.persona.title}",
        f"**副标题**：{certificate.persona.subtitle}",
        f"**标签**：{' / '.join(certificate.persona.tags)}",
        f"**总结**：{certificate.persona.summary}",
        "",
        "### 判定依据",
    ]
    for item in certificate.evidence:
        lines.append(f"- {item}")
    lines.extend(["", "### 下一次突破任务"])
    for item in certificate.growth_plan:
        lines.append(f"- {item}")
    return "\n".join(lines)
