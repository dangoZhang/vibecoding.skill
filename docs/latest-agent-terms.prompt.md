# 最新 Agent 术语注入 Prompt

词表更新时间：2026-04-11 11:14 UTC

你要做的事：
- 先读取下面这份术语输入。
- 只使用和 vibecoding、LLM agent、工具编排、跨会话协作直接相关的术语。
- 写报告、画像、等级卡、升级建议时，优先使用这份词表里的最新常见说法。
- 如果轨迹里没有出现对应行为，不要硬贴新词。
- 如果新词会让句子变虚，就回到更直接的人话。

术语输入：
- agentic coding：别名 agentic coding, long-horizon, coding tasks；解释：强调长链路、带工具、可持续推进的编码协作。；来源：OpenAI GPT-5.2-Codex model
- rules：别名 rules, project rules, user rules；解释：把长期有效的项目规则、用户偏好和 workflow 固化给 agent。；来源：Cursor Rules
- memory：别名 memory, memories, context across sessions, cross sessions；解释：把跨会话仍然有效的信息保留下来，减少重复解释。；来源：Anthropic Claude Code slash commands
- mcp：别名 mcp, model context protocol；解释：让 agent 通过标准协议接入 tools、resources、prompts。；来源：Anthropic Claude Code MCP, Anthropic Claude Code slash commands, MCP Build Server, MCP Tools, MCP Prompts
- resources：别名 resources, resource links；解释：把文件、文档、结构化上下文作为可引用资源交给 agent。；来源：OpenAI Codex use cases, OpenAI GPT-5.2-Codex model, Anthropic Claude Code MCP, Anthropic Claude Code slash commands, MCP Build Server, MCP Tools, MCP Prompts
- tools：别名 tools, tool calls, tool use, model-controlled；解释：让模型按上下文主动调用能力，而不是只做纯文本回答。；来源：OpenAI GPT-5.2-Codex model, Anthropic Claude Code MCP, Anthropic Claude Code slash commands, Cursor Rules, MCP Build Server, MCP Tools
- prompts：别名 prompts, slash commands, prompt templates；解释：把可复用的工作流和指令模板显式暴露出来。；来源：OpenAI Codex use cases, Anthropic Claude Code MCP, Anthropic Claude Code slash commands, MCP Build Server, MCP Tools, MCP Prompts
- structured outputs：别名 structured outputs, structured content；解释：要求输出保持结构化，方便后续汇总、比对和自动处理。；来源：OpenAI GPT-5.2-Codex model, MCP Tools
- context window：别名 context window, output tokens, token；解释：上下文和输出上限直接决定一次能吃下多少轨迹与证据。；来源：OpenAI GPT-5.2-Codex model, Anthropic Claude Code MCP
- handoff：别名 take over, follow-ups, compact, handoff, continue；解释：支持压缩上下文、续接任务、异步接力和回到主线。；来源：Anthropic Claude Code slash commands
