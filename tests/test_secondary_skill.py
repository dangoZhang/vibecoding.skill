from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from vibecoding_skill.models import Message
from vibecoding_skill.cards import build_card_data, render_vibecoding_card
from vibecoding_skill.exporter import export_bundle
from vibecoding_skill.secondary_skill import (
    build_readme_profile_panel,
    build_secondary_skill_distillation,
    result_skill_slug,
    result_skill_title_from_display,
)


class SecondarySkillDistillationTests(unittest.TestCase):
    def test_distillation_expands_to_sixteen_dimensions(self) -> None:
        messages = [
            Message(
                role="user",
                text=(
                    "目标是做一个新的 skill。边界：纯本地。验收：生成 README、JSON、导出包和结果 skill。"
                    "先读 /tmp/demo.py 和 logs/demo.log，再开始做。不要空讲，结论优先。"
                ),
            ),
            Message(
                role="assistant",
                text=(
                    "我先读文件并运行 python3 -m py_compile，然后把任务拆成三步。"
                    "会先产出 README、脚本和 JSON，并补验证结果和未验证项。"
                ),
            ),
            Message(
                role="user",
                text=(
                    "如果偏了先缩范围再继续。继续沿用上次 snapshot，最后要给同事导出包和结果 skill 接管。"
                    "把这套做法沉成可复用 workflow。"
                ),
            ),
            Message(
                role="assistant",
                text=(
                    "我会并行检查 README 和导出脚本；如果测试失败就 fallback 到最小可运行版本。"
                    "完成后给你验证日志、未验证项和下一步建议。"
                ),
            ),
        ]

        distillation = build_secondary_skill_distillation(
            messages=messages,
            display_name="码奸",
            source="codex",
            rank="L4",
            generated_at="2026-04-14 12:00",
        )

        axes = distillation["axes"]
        self.assertEqual(len(axes), 16)
        axis_map = {axis["id"]: axis for axis in axes}

        self.assertGreaterEqual(axis_map["goal_framing"]["score"], 2)
        self.assertGreaterEqual(axis_map["tool_orchestration"]["score"], 2)
        self.assertGreaterEqual(axis_map["verification_loop"]["score"], 2)
        self.assertGreaterEqual(axis_map["handoff_memory"]["score"], 1)
        self.assertGreaterEqual(axis_map["abstraction_reuse"]["score"], 1)
        self.assertGreaterEqual(axis_map["workflow_orchestration"]["score"], 1)

        panel = build_readme_profile_panel(distillation)
        self.assertTrue(panel["paragraphs"])
        self.assertTrue(panel["bullets"])
        self.assertLessEqual(len(panel["tags"]), 4)
        self.assertEqual(panel["title"], "你怎么和 AI 协作")
        self.assertIn("你", panel["paragraphs"][0])
        self.assertIn("prompt", "".join(panel["paragraphs"]))

    def test_large_corpus_uses_coverage_ratio_instead_of_raw_count(self) -> None:
        messages = []
        for _ in range(14):
            messages.append(
                Message(
                    role="user",
                    text="目标、边界、验收都写清楚。先读 /tmp/demo.py，再直接开始做并补验证结果。",
                )
            )
            messages.append(
                Message(
                    role="assistant",
                    text="我先读文件并执行，完成后给测试日志、证据和未验证项。",
                )
            )

        messages.extend(
            [
                Message(role="user", text="沿用上次 snapshot，最后补一个导出包。"),
                Message(role="assistant", text="我会基于 snapshot 收尾，并补导出包接管说明。"),
                Message(role="user", text="这轮先专注主线，不需要额外交接设计。"),
                Message(role="assistant", text="继续推进主线，优先验证和交付。"),
            ]
        )

        distillation = build_secondary_skill_distillation(
            messages=messages,
            display_name="码奸",
            source="codex",
            rank="L7",
            generated_at="2026-04-14 13:00",
        )

        axis_map = {axis["id"]: axis for axis in distillation["axes"]}
        self.assertEqual(len(messages), 32)
        self.assertEqual(axis_map["goal_framing"]["score"], 4)
        self.assertLess(axis_map["handoff_memory"]["score"], 4)
        self.assertLess(axis_map["handoff_memory"]["score"], axis_map["goal_framing"]["score"])
        self.assertLess(axis_map["handoff_memory"]["coverage_ratio"], 0.15)

    def test_result_skill_name_is_portable_ascii_slug(self) -> None:
        self.assertEqual(result_skill_title_from_display("码奸"), "码奸.skill")
        slug = result_skill_slug("码奸")
        self.assertTrue(slug.startswith("vibecoding-profile-"))
        self.assertRegex(slug, r"^[a-z0-9-]+$")
        self.assertEqual(result_skill_slug("vibecoding-skill"), "vibecoding-skill")

    def test_xianxia_card_uses_realm_and_sect_labels(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "insights": {"rank": "L4"},
            "transcript": {
                "display_name": "码奸",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "axes": [{"score": 4}] * 16,
            },
        }
        card = build_card_data(payload, style="xianxia")
        self.assertEqual(card.level_label, "境界")
        self.assertEqual(card.level, "金丹")
        self.assertEqual(card.platform_model_label, "宗门和法宝")
        self.assertIn("多个傀儡", card.summary)
        self.assertEqual(len(card.axis_scores), 16)

    def test_card_renders_constellation_panel(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "insights": {"rank": "L4"},
            "transcript": {
                "display_name": "码奸",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "axes": [{"score": value} for value in [4, 4, 1, 0, 1, 0, 2, 0, 1, 0, 4, 2, 0, 1, 0, 0]],
            },
        }
        svg = render_vibecoding_card(payload, style="default")
        self.assertIn("十六维星图 · 奎宿", svg)
        self.assertIn("亮度随 16 维得分变化", svg)
        self.assertIn("stroke-dasharray", svg)

    def test_card_can_render_english_labels(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "insights": {"rank": "L4"},
            "transcript": {
                "display_name": "Jian",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "axes": [{"score": 4}] * 16,
            },
        }
        svg = render_vibecoding_card(payload, style="default", locale="en")
        self.assertIn("Platforms and Models", svg)
        self.assertIn("16-Dimension Star Map · Kui", svg)
        self.assertIn("Brightness follows the 16 dimension scores", svg)

    def test_export_bundle_emits_cursor_rule_and_agents(self) -> None:
        payload = {
            "generated_at": "2026-04-14 13:00",
            "display_name": "码奸",
            "insights": {"rank": "L4", "ability_text": "你已经能稳定推进常见任务。"},
            "transcript": {
                "display_name": "码奸",
                "source": "codex",
                "models": ["gpt-5.4"],
            },
            "secondary_skill": {
                "secondary_skill_contract": {
                    "default_behavior": ["先收束目标、边界、验收，再直接开始做。"],
                    "guardrails": ["如果事实不够，先补文件、日志或命令结果，不要硬猜。"],
                    "prompt_examples": ["按这套 vibecoding 习惯和我一起推进这个任务。"],
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            exported = export_bundle(
                payload=payload,
                markdown="# report\n",
                output_dir=tmpdir,
            )
            agents_path = Path(exported["agents_md"])
            cursor_rule_path = Path(exported["cursor_rule"])
            self.assertTrue(agents_path.exists())
            self.assertTrue(cursor_rule_path.exists())
            self.assertIn("Default Behavior", agents_path.read_text(encoding="utf-8"))
            self.assertIn("alwaysApply: false", cursor_rule_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
