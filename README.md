# TANDIU Agent Skills

[中文](#中文) · [English](#english)

Agent Skills (SKILL.md standard) that let Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and other agents pull live data from **[TANDIU](https://www.tandiu.cn)** — an AI infrastructure data platform — when a question needs it.

Skills are thin instructions: when to use, how to call, how to read the result. All data comes live from TANDIU's MCP server or public JSON; nothing is bundled here.

| Skill | Use it for |
|---|---|
| [tandiu-llm-cost](skills/tandiu-llm-cost/SKILL.md) | LLM API price comparison, token cost and monthly budget, cheapest model at a benchmark score, GPU purchase / cloud rental prices, self-hosting vs API for a company |
| [tandiu-cn-ai-procurement](skills/tandiu-cn-ai-procurement/SKILL.md) | China government AI / compute tenders and awards (GPUs, AI servers, intelligent computing centers, LLM services): budgets, winners, award-to-budget ratio |
| [tandiu-ai-funding](skills/tandiu-ai-funding/SKILL.md) | AI funding rounds (mainly US and China): company, round, amount, valuation, investors, source links |

---

## English

### Install

**Claude Code** (plugin marketplace):

```
/plugin marketplace add tandiu-ai/agent-skills
/plugin install tandiu-data@tandiu-agent-skills
```

**Any agent supporting Agent Skills** (Codex, Cursor, Copilot, Gemini CLI, OpenCode, …) via the [skills](https://skills.sh) CLI:

```bash
npx skills add tandiu-ai/agent-skills
```

**Manual**: copy the folders under `skills/` into your agent's skills directory — `.agents/skills/` (project, cross-agent), `~/.claude/skills/` (Claude Code) or `~/.codex/skills/` (Codex).

Optional but recommended: also connect the TANDIU MCP server (`https://www.tandiu.cn/mcp`, Streamable HTTP, no auth) — the skills prefer MCP tools when available. See [tandiu-ai/tandiu-mcp](https://github.com/tandiu-ai/tandiu-mcp).

### How it works

1. If the TANDIU MCP server is connected, the agent calls its tools (`list_llm_prices`, `list_ai_funding`, …).
2. Otherwise it runs `scripts/fetch.py` (Python standard library only, HTTPS GET, 10 s timeout) against `https://www.tandiu.cn/data/*.json`.
3. If the main site is unreachable it falls back to the mainland China mirror `https://tandiuai.cn`.

Every answer should cite: *Source: TANDIU (tandiu.cn), updated &lt;date&gt;*.

### Safety

Scripts only send GET requests to `www.tandiu.cn` / `tandiuai.cn`, never run shell commands, never write files and contain no keys. Requests identify themselves with `User-Agent: TANDIU-Skill/<skill>/<version>` and `X-TANDIU-Client: skill` so TANDIU can count skill usage; no personal data is sent. See [docs/security-check.md](docs/security-check.md).

### TANDIU Pro (optional)

If the environment variable `TANDIU_API_KEY` is set, `tandiu-llm-cost` can also query daily official price history (`fetch.py history`). Without it, only free data is used. Never put the key in a file. Pro: https://www.tandiu.cn/en/api

---

## 中文

把 TANDIU(钽铥,tandiu.cn)的数据能力封装成符合 SKILL.md 标准的 Agent Skills。Claude Code、Codex、Cursor、Copilot、Gemini CLI 等 Agent 遇到相关问题时会自动调用 TANDIU 的实时数据。

Skill 只是说明书(何时用、怎么调、怎么解读),数据全部实时来自 TANDIU 的 MCP 服务或公开 JSON,仓库里不含数据。

| Skill | 用途 |
|---|---|
| tandiu-llm-cost | 大模型 API 价格对比、Token 成本与月度预算、同等评测分最便宜的模型、GPU 价格与云端时租、企业自部署 vs API 选型 |
| tandiu-cn-ai-procurement | 中国政府采购网 AI / 算力采购需求与中标成交:预算、中标方、成交价占预算比例 |
| tandiu-ai-funding | AI 公司投融资(中美为主):轮次、金额、估值、投资方、原文链接 |

### 安装

- **Claude Code**:`/plugin marketplace add tandiu-ai/agent-skills`,再 `/plugin install tandiu-data@tandiu-agent-skills`。
- **其他支持 Agent Skills 的工具**:`npx skills add tandiu-ai/agent-skills`。
- **手动**:把 `skills/` 下的目录复制到 `.agents/skills/`(项目内、通用)、`~/.claude/skills/` 或 `~/.codex/skills/`。

建议同时接入 TANDIU MCP(`https://www.tandiu.cn/mcp`,无需认证),Skill 会优先用 MCP 工具。

### 调用顺序

已连接 MCP → 调 MCP 工具;未连接 → 运行 `scripts/fetch.py`(仅 Python 标准库、仅 GET、10 秒超时);主站不可达 → 自动回退境内镜像 `tandiuai.cn`。回答需注明「数据来源:TANDIU(tandiu.cn),更新于 <日期>」。

### 安全

脚本只向 `www.tandiu.cn` / `tandiuai.cn` 发 GET,不执行 shell、不写文件、不含任何密钥。请求带 `User-Agent: TANDIU-Skill/<skill>/<version>` 和 `X-TANDIU-Client: skill` 用于统计 Skill 调用量,不发送任何个人信息。

### Pro(可选)

设置环境变量 `TANDIU_API_KEY` 后,`tandiu-llm-cost` 可查询逐日官方牌价历史;未设置时只用免费数据。不要把 key 写进任何文件。

---

## License

Skill text and scripts: [MIT](LICENSE). Data returned by TANDIU is governed by the [TANDIU data terms](DATA-TERMS.md) / [Terms of Service](https://www.tandiu.cn/en/terms).

Skill 文本与脚本采用 MIT 许可;TANDIU 返回的数据适用 [数据使用条款](DATA-TERMS.md)。
