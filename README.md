<div align="center">

# vibecoding.skill

把你和 AI 的协作方式，蒸成可复用的能力。

语言选择：
[中文](./README.md) · [English](./README_EN.md)

原生支持：
<br />
<img src="https://img.shields.io/badge/Codex-0B0B0F?style=for-the-badge&logo=openai&logoColor=white" alt="Codex" />
<img src="https://img.shields.io/badge/Claude_Code-1A1716?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code" />
<img src="https://img.shields.io/badge/OpenCode-111827?style=for-the-badge&logo=gnubash&logoColor=white" alt="OpenCode" />
<img src="https://img.shields.io/badge/OpenClaw-0F172A?style=for-the-badge&logo=git&logoColor=white" alt="OpenClaw" />
<br />
待补原生适配：
<img src="https://img.shields.io/badge/Cursor-1F2937?style=for-the-badge&logo=cursor&logoColor=white" alt="Cursor" />

</div>

<table>
<tr>
<td width="52%" valign="top">

### skill 信息提取的关键字和特征

`L4` `稳定期` `目标先收束` `上下文给够` `结果可验证` `证据优先`

这是用 `examples/demo_codex_session.jsonl` 重新实测生成的画像。整体看，这类 vibecoding 很像一个先把场子铺平再开工的人：任务开始前，会先把目标、边界和交付物钉住，再把路径、文件和背景一次性交代清楚，让 agent 接手时几乎不用猜。

真正开始推进后，节奏又会立刻切到务实模式。它更信文件、命令和日志里的证据，不爱空讲；能直接动手的地方就先推进，收尾时会盯住验证结果，避免停在“看起来差不多”。

给人的感觉是主线清楚，推进不拖泥带水，合作一开始就很容易进入有效工作状态。下一步如果还想更像成熟的 vibecoding 老手，重点要补的是偏了之后的修正速度，以及更长链路里的连续推进能力。

</td>
<td width="48%" valign="top">

### 宣传卡

<img src="./assets/readme/vibecoding-card.png" alt="vibecoding.skill 分享卡" width="100%" />

</td>
</tr>
</table>

## 一、能做什么

`vibecoding.skill` 直接读真实日志，不做问卷，不做自评。

它现在能做五件事：

- 读代码代理日志，从 16 个维度提取 vibecoding 能力。
- 给出等级、阶段和人话画像。
- 把能力导出成共享包，包含 `README.md`、`REPORT.md`、`PROFILE.md`、`DISTILLED_SKILL.json` 和结果 `skill`。
- 读取他人分享的导出包，先读画像，再接管对应的二级 `skill`。
- 根据当前等级和短板，给出下一轮升级建议。

风格切换也内置好了：

- 提到 `修仙` 或 `境界`，卡片和相关文案会自动切到修仙模式。
- 修仙模式下，等级会换成境界名，比如 `L4 -> 金丹`。
- 关键 AI 含义会保留在括号里，避免只剩氛围词。

16 个维度按四层组织：

- 任务定义层：目标 framing、上下文供给、约束治理、沟通压缩度
- 执行控制层：执行默认、任务拆解、工具编排、上下文承接、迭代修正、失败恢复
- 结果闭环层：验证闭环、产物落地、交接与记忆、抽象复用
- 杠杆放大量：自主推进深度、并行与工作流化

## 二、如何安装

按你实际在用的宿主安装：

### Codex

OpenAI 公开文档写的是 `~/.codex/skills/<skill-name>/SKILL.md`。当前这台机器上的 `skills` 安装器会装到共享目录 `~/.agents/skills/`，而本机 Codex Desktop 也能实际读取这个目录。

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a codex
```

如果你想严格按公开文档落盘，也可以手动复制或软链到：

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)" ~/.codex/skills/vibecoding-skill
```

### Claude Code

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a claude-code
```

### OpenCode

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a opencode
```

### OpenClaw

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a openclaw
```

### Cursor

Cursor 官方走 `Rules / AGENTS.md / Memories`，当前仓库还没提供原生 Cursor 版包装。

```bash
npx skills add https://github.com/dangoZhang/vibecoding.skill -a cursor
```

这个命令可以通过 `skills` 装进共享目录，但还不等于 Cursor 官方原生 `Rules` 规范已经适配完成。

本机 Codex 实测安装命令：

```bash
npx skills add . -a codex -g -y
```

实测安装结果：

```text
Installed 1 skill
✓ vibecoding-skill (copied)
→ ~/.agents/skills/vibecoding-skill
```

## 三、示例 prompt 和回答

下面 6 组示例，都来自本机安装到 Codex 后，对同一份输入 `examples/demo_codex_session.jsonl` 的实机调用。

### 1. 蒸馏画像

Prompt

```text
帮我看下我最近两周的 vibecoding 等级，再总结一下协作习惯。
```

实机回答

> 这段记录的 vibecoding 等级是 `L4`，阶段在 `稳定期`。按这份样本看，你已经能把常见任务稳定推进到多步完成，AI 也开始承担明确的执行位。
>
> 协作习惯很清楚：
> - 起手强。你会先把目标、约束、交付物一次性交代清楚。
> - 推进快。AI 这边接到信息后会直接动手，整体节奏偏“先执行，再汇报”。
> - 偏结果导向。你提的都是可落地输出物，没有停在泛讨论。
> - 纠偏还不够强，所以“迭代修正”和“补救适配”是当前短板。

产物路径：
- `examples/generated/demo-report.md`
  聚合分析报告，适合直接读结论。

### 2. 共享能力

Prompt

```text
把我最近两周的协作方式导出来，给我共享包和接收方该怎么用的一句话。
```

实机回答

> - 共享包：`examples/generated/demo_codex_session-share-bundle`
> - 结果 skill 调用名：`vibecoding-profile-f11a0caa`
> - 结果 skill 标题：`码奸.skill`
> - 接收方下一句：`这是同事的导出包。先读他的画像，再调用 vibecoding-profile-f11a0caa 和我一起做当前任务。`

产物路径：
- `examples/generated/demo_codex_session-share-bundle/README.md`
  给接收方看的导出包说明。
- `examples/generated/demo_codex_session-share-bundle/DISTILLED_SKILL.json`
  二级 skill 的结构化蒸馏结果。

### 3. 解压应用能力

Prompt

```text
这是同事的导出包。先读他的画像，再按这套方式和我一起做当前任务。
```

实机回答

> 我会先用 `vibecoding.skill` 做入口，再接管导出包里的结果 skill。
>
> 先读这 4 个文件，顺序固定：
> 1. `PROFILE.md`
> 2. `REPORT.md`
> 3. `DISTILLED_SKILL.json`
> 4. `SKILL.md`
>
> 识别到的结果 skill 调用名是 `vibecoding-profile-f11a0caa`，显示标题是 `码奸.skill`。后续协作默认按它执行：先收束目标、边界、验收，再直接动手；优先读文件、跑命令、落产物，不先堆方案。

### 4. 利用二级 skill 修改 code 工作中的 prompt

Prompt

```text
调用 `vibecoding-profile-f11a0caa`，把我现在这条 code 工作里的 prompt 改成更适合这套协作方式的一版。
```

实机回答

```text
按 `vibecoding.skill` 先读取并调用导出的 `vibecoding-profile-f11a0caa`，再按这套协作方式帮我修这个仓库里的 bug。先用两句话收束这次任务的目标、边界和验收标准，然后直接开始做：先读相关文件、跑必要命令、查日志，定位根因并完成修复，不要先讲大段方案。如果信息不够，先补文件、日志或命令结果，不要硬猜；如果发现偏差，只补一条最关键修正后继续推进。最后只按这三项回报：改了什么、怎么验证、还有什么没验证或仍有风险。
```

### 5. 升级建议

Prompt

```text
如果我想把这套协作方式继续打磨，下一轮先练什么？
```

实机回答

> 下一轮先练 `迭代修正力`。
>
> 具体就练这一套：
> 1. 每轮结果出来先问：`偏差最大的一点是什么？`
> 2. 只补 `一条` 最关键修正，别一次加很多要求。
> 3. 如果卡住，直接让 AI 给 `3 个缩范围方案`，只选最短路径继续。

产物路径：
- `examples/generated/demo-coach.md`
  升级建议和下一轮训练动作。

### 6. 修仙彩蛋

Prompt

```text
给我一张修仙境界风格的 vibecoding 彩蛋卡。
```

实机回答

> 检测到关键字“修仙 / 境界”，卡片已切到修仙模式。
> 这次的主卡字段会换成 `境界 / 宗门和法宝 / 出关时间`，其中 `L4` 会显示成 `金丹`。
>
> 主文件在：
> - `examples/generated/demo_codex_session-xianxia-card/vibecoding-card-xianxia.png`
> - `examples/generated/demo_codex_session-xianxia-card/vibecoding-card-xianxia.svg`
>
> 同目录还生成了：
> - `examples/generated/demo_codex_session-xianxia-card/report.md`
> - `examples/generated/demo_codex_session-xianxia-card/report.json`

实测彩蛋卡：

<img src="./examples/generated/demo_codex_session-xianxia-card/vibecoding-card-xianxia.png" alt="vibecoding.skill 修仙彩蛋卡" width="420" />

## 四、等级表

| 等级 | 境界 | 典型状态 |
| --- | --- |
| L1 | 炼气 | 还停在随手问答，缺少稳定方法。 |
| L2 | 筑基 | 知道提问方式会影响结果。 |
| L3 | 虚丹 | 能稳定完成简单任务。 |
| L4 | 金丹 | 神识强大，可同时控制多个傀儡干活（常见任务可以推进到多步完成）。 |
| L5 | 元婴 | 开始把顺手打法沉成 skill、模板或模块。 |
| L6 | 化神 | 已经有能替自己先干一段活的分身。 |
| L7 | 炼虚 | 能调多 agent、多工具协同完成任务。 |
| L8 | 合体 | 开始做能力层和长期工作流设计。 |
| L9 | 大乘 | 人负责判断和担责，agent 负责执行和回流。 |
| L10 | 渡劫 | 能把自己的方法稳定复制给团队或客户。 |

## 五、开源证书和项目结构树图

开源证书：

- [MIT License](./LICENSE)

项目结构：

```text
portrait.skill
├── README.md                      # 中文主文档，安装、示例、等级表
├── README_EN.md                   # 英文简版说明
├── SKILL.md                       # 入口 skill 规则，宿主实际读取这里
├── LICENSE                        # MIT 许可证
├── pyproject.toml                 # Python 包与 CLI 入口配置
├── assets
│   └── readme                     # README 展示用静态卡片
│       ├── vibecoding-card.png
│       ├── vibecoding-card.svg
│       ├── vibecoding-card-xianxia.png
│       └── vibecoding-card-xianxia.svg
├── docs                           # 联网刷新后的术语缓存
│   ├── latest-agent-terms.json
│   ├── latest-agent-terms.md
│   └── latest-agent-terms.prompt.md
├── examples
│   ├── demo_codex_session.jsonl   # 最小可复现实测输入
│   └── generated                  # README 里展示的真实生成结果
│       ├── demo-coach.md
│       ├── demo_codex_session-share-bundle
│       │   ├── DISTILLED_SKILL.json   # 二级 skill 结构化结果
│       │   ├── PROFILE.md             # 接收方先读的人话画像
│       │   ├── README.md              # 导出包使用说明
│       │   ├── REPORT.md              # 完整分析报告
│       │   ├── SKILL.md               # 可安装的二级 skill
│       │   ├── assets                 # 导出包自带卡片
│       │   └── snapshot.json          # 全量快照，方便二次开发
│       ├── demo_codex_session-xianxia-card
│       │   ├── report.json
│       │   ├── report.md
│       │   ├── vibecoding-card-xianxia.png
│       │   └── vibecoding-card-xianxia.svg
│       ├── demo-distilled.json
│       ├── demo-distilled.md
│       └── demo-report.md
├── tests
│   └── test_secondary_skill.py    # 二级 skill 打分与命名回归测试
└── vibecoding_skill
    ├── __init__.py
    ├── analyzer.py                # 原始评分、等级判定、能力分析
    ├── cards.py                   # 分享卡与修仙卡绘制
    ├── cli.py                     # analyze / export / coach / distill-skill 命令入口
    ├── distill.py                 # 长日志分块蒸馏与聚合
    ├── exporter.py                # 导出包写盘与 README/SKILL 生成
    ├── insights.py                # 人话画像、宣传文案、升级建议
    ├── luogu_palette.py           # 洛谷等级配色表
    ├── memory.py                  # 本地快照与前后轮对比
    ├── models.py                  # 消息、转录等数据结构
    ├── parsers.py                 # 多平台日志解析
    ├── renderer.py                # Markdown 报告渲染
    ├── secondary_skill.py         # 16 维二级 skill 蒸馏
    ├── terms.py                   # 术语刷新来源与词表
    ├── themes.py                  # 主题与视觉参数
    └── xianxia.py                 # 修仙术语与画像映射
```
