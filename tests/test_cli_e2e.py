from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "demo_codex_session.jsonl"


class CliE2ETests(unittest.TestCase):
    def _run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, "-m", "vibecoding_skill.cli", *args],
            cwd=ROOT,
            env=merged_env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_analyze_auto_switches_to_xianxia_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._run_cli("analyze", "--path", str(DEMO), "--source", "codex", "--card-dir", tmpdir)
            self.assertTrue((Path(tmpdir) / "vibecoding-card-xianxia.svg").exists())
            self.assertTrue((Path(tmpdir) / "vibecoding-card-xianxia.png").exists())

    def test_export_emits_end_to_end_bundle_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._run_cli("export", "--path", str(DEMO), "--source", "codex", "--export-dir", tmpdir)
            root = Path(tmpdir)
            self.assertTrue((root / "README.md").exists())
            self.assertTrue((root / ".cursor" / "rules").exists())
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("assets/vibecoding-card-xianxia.png", readme)
            self.assertIn(".cursor/rules/", readme)

    def test_export_captures_model_and_renders_platform_model_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._run_cli("export", "--path", str(DEMO), "--source", "codex", "--export-dir", tmpdir)
            root = Path(tmpdir)
            snapshot = json.loads((root / "snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["transcript"]["models"], ["openai/gpt-5.4"])
            self.assertEqual(snapshot["transcript"]["providers"], ["openai"])
            svg = (root / "assets" / "vibecoding-card-xianxia.svg").read_text(encoding="utf-8")
            self.assertIn("Codex · gpt-5.4", svg)

    def test_analyze_does_not_persist_memory_without_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            result = self._run_cli(
                "analyze",
                "--path",
                str(DEMO),
                "--source",
                "codex",
                env={"VIBECODING_SKILL_HOME": home},
            )
            self.assertNotIn("## 上次评测记忆", result.stdout)
            self.assertFalse((Path(home) / "history.json").exists())

    def test_memory_opt_in_uses_distinct_bucket_per_path(self) -> None:
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as sessions:
            first = Path(sessions) / "first.jsonl"
            second = Path(sessions) / "second.jsonl"
            first.write_text(DEMO.read_text(encoding="utf-8"), encoding="utf-8")
            second.write_text(DEMO.read_text(encoding="utf-8"), encoding="utf-8")

            self._run_cli(
                "analyze",
                "--path",
                str(first),
                "--source",
                "codex",
                "--memory",
                env={"VIBECODING_SKILL_HOME": home},
            )
            result = self._run_cli(
                "analyze",
                "--path",
                str(second),
                "--source",
                "codex",
                "--memory",
                env={"VIBECODING_SKILL_HOME": home},
            )

            self.assertIn("已记住本次评测", result.stdout)
            self.assertNotIn("与上次持平", result.stdout)

    def test_distill_skill_supports_all_non_codex_sources(self) -> None:
        generic_lines = [
            json.dumps({"role": "user", "text": "目标、边界、验收写清楚。先读文件再动手。"}, ensure_ascii=False),
            json.dumps({"role": "assistant", "text": "我先读文件，再跑命令，最后给验证结果。"}, ensure_ascii=False),
        ]
        for source in ("claude", "opencode", "openclaw", "cursor", "vscode"):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as tmpdir:
                transcript = Path(tmpdir) / f"{source}.jsonl"
                output = Path(tmpdir) / f"{source}.json"
                transcript.write_text("\n".join(generic_lines) + "\n", encoding="utf-8")
                self._run_cli("distill-skill", "--path", str(transcript), "--source", source, "--json-output", str(output))
                payload = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(payload["source"], source)
                self.assertIn("prompt_rewrite_rules", payload["secondary_skill_contract"])
                self.assertIn("prompt_rewrite", payload["llm_prompts"])

    def test_doctor_reports_test_install_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "doctor.json"
            self._run_cli("doctor", "--json-output", str(output))
            payload = json.loads(output.read_text(encoding="utf-8"))
            env = payload["environment_config"]
            self.assertEqual(env["test_install_command"], "python3 -m pip install -e \".[test]\"")
            self.assertEqual(env["test_command"], "python3 -m pytest -q")
            self.assertIn("pytest", env["test_dependencies"])


if __name__ == "__main__":
    unittest.main()
