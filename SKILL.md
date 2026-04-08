---
name: portrait.skill
description: Read Codex, Claude Code, or OpenCode transcript files, extract user-AI collaboration patterns, issue cultivation or AI capability portraits, and guide the next breakthrough cycle.
---

# portrait.skill

## What It Does

`portrait.skill` reads agent runtime transcripts, scores collaboration quality, and issues two optional output tracks:

- User cultivation portrait
- AI collaboration capability certificate

It can also produce a next-cycle breakthrough plan so the user can return after another work period and recertify.

## When To Use

Use this skill when the user wants to:

- analyze a Codex / Claude Code / OpenCode conversation file
- understand how they collaborate with AI
- get a gamified but evidence-based portrait or certificate
- improve collaboration quality over the next cycle
- compare multiple logs over time

## Operating Flow

1. Ask for the transcript path, or auto-detect the latest local file.
2. Ask which certificate they want: `user`, `assistant`, or `both`.
3. Parse the transcript and summarize:
   - user request style
   - context quality
   - iteration pattern
   - verification behavior
   - tool usage
   - recovery / adaptation
4. Issue the certificate in markdown with:
   - level
   - 画像
   - evidence
   - next breakthrough tasks
5. If the user wants growth guidance, turn the weakest dimensions into a 1-cycle training plan.

## Local Defaults

- Codex: `~/.codex/archived_sessions/`, `~/.codex/sessions/`
- Claude Code: `~/.claude/projects/`
- OpenCode: `~/.local/share/opencode/project/`, `~/Library/Application Support/opencode/project/`

## CLI

```bash
python3 -m portrait_skill.cli scan
python3 -m portrait_skill.cli analyze --source codex --certificate both
python3 -m portrait_skill.cli analyze --path ~/.codex/archived_sessions/rollout-xxx.jsonl --certificate user
```

## Output Contract

Keep the final answer concise and evidence-based. Prefer this structure:

1. one-paragraph overview
2. certificate section
3. 2 to 3 breakthrough tasks

Avoid empty hype. Every level claim must cite transcript evidence.
