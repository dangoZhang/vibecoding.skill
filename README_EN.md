<div align="center">

# vibecoding.skill

Record how you work with AI, then turn it into a level, a profile, a share card, and a reusable vibecoding capability.

[中文](./README.md) · [English](./README_EN.md)

</div>

<table>
<tr>
<td width="52%" valign="top">

### A distilled vibecoding profile

`L4` `Goal-first` `Context-ready` `Direct execution` `Verifiable output`

This style starts cleanly. The user usually defines the goal, boundary, and deliverable first, then supplies the relevant paths, files, and background in one go, so the agent can pick up the task without extra back-and-forth.

Once execution starts, the rhythm leans toward shipping before explaining. If code can be changed, it gets changed. If a result can be verified, the verification is shown. The collaboration keeps moving.

- Plain language, conclusion first
- Read files, run commands, use evidence
- When things drift, add one key correction and keep going

</td>
<td width="48%" valign="top">

<img src="./assets/readme/vibecoding-card.png" alt="vibecoding.skill preview" width="100%" />

</td>
</tr>
</table>

The left side is human-readable feedback synthesized from the distilled secondary skill. The right side is the generated share card.

---

## Install

Install it into the host you actually use:

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a codex
```

OpenAI's public Codex docs describe `~/.codex/skills/<skill-name>/SKILL.md` as the native location. In this local environment, the `skills` installer targets the shared `~/.agents/skills/` directory, and Codex Desktop does load skills from there in practice. If you want the strictly documented layout, copy or symlink the repo into `~/.codex/skills/vibecoding-skill`.

Native skill targets verified here: `codex`, `claude-code`, `opencode`, `openclaw`

`cursor` is not a native `SKILL.md` target in Cursor's own docs. Cursor uses `Rules`, `AGENTS.md`, and `Memories`. The `skills` installer can still copy this repo into a shared agent-skills directory, but that is not the same as a native Cursor Rules package yet.

---

## What It Can Do

This is not a questionnaire and not self-scoring.

It reads real collaboration history and gives you four kinds of output:

- Level and profile: where you are now, what is stable, and what is weak.
- Share card: a compact visual summary you can post or send.
- Shared capability: distill your way of working so someone else can keep using it.
- Coaching: tell you what to improve next.

Good fit when you want to:

- know what level your AI collaboration has actually reached
- turn a period of work into a reusable method
- pass your way of working to a teammate
- receive someone else's way of working and continue from there

---

## What To Say

After installation, you can simply say:

```text
Look at my last two weeks and tell me my vibecoding level, then summarize my collaboration habits.
```

```text
Give me a vibecoding share card for this recent stretch.
```

```text
Export my last two weeks into a shared bundle and tell me the exact sentence the receiver should use.
```

```text
This is my teammate's exported bundle. Read the profile first, then work with me in that style.
```

```text
If I want to refine this workflow, what should I train next?
```

---

## How Sharing Works

The simple idea is: distill one person's AI collaboration style, then let someone else keep using it.

The common flow is:

1. Distill your recent work into a profile, a share card, and a shared bundle.
2. Send that bundle to another person who also uses this repo.
3. They read the profile and continue working in that style.

---

## Level Guide

| Level | Typical state |
| --- | --- |
| L1 | Still mostly ad hoc prompting with no stable method. |
| L2 | Already knows that prompt wording changes the result. |
| L3 | Can complete simple tasks with some consistency. |
| L4 | Can push familiar tasks through multi-step collaboration. |
| L5 | Starts turning repeatable wins into skills, templates, or modules. |
| L6 | Already has an agent that can take a chunk of work first. |
| L7 | Can coordinate multiple agents and tools on the same task. |
| L8 | Starts designing capability layers and longer workflows. |
| L9 | The human owns judgment and accountability; the agent owns execution and feedback. |
| L10 | The method can be copied reliably across a team or clients. |

---

<div align="center">

MIT License © [dangoZhang](https://github.com/dangoZhang)

</div>
