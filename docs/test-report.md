# Trigger test report (v0.1.0, 2026-10-26)

**Result: 15 / 15 triggered the expected skill, called the right data, and cited TANDIU with the data date.**

## Setup

- Claude Code 2.1.296, headless (`claude -p`), on a Linux server, in a project with the three skills under `.claude/skills/`.
- No TANDIU MCP server connected, so every answer had to go through `scripts/fetch.py` (tests the fallback path).
- Allowed tools: `Skill`, `Read`, `Bash(python3:*)`. Prompts do not mention TANDIU or the skill names.
- Harness: [run_trigger_test.py](run_trigger_test.py). Checks: Skill tool invoked with the expected skill; a `fetch.py` command ran; the answer contains "TANDIU" plus a date.
- Server side: every request showed up in TANDIU's stats under the new **Skill** category, split by skill/version and endpoint (counted as internal traffic because the test machine is ours).

## Results (second run, final v0.1.0 scripts)

| # | Expected skill | Prompt | fetch.py command(s) | Citation in answer |
|---|---|---|---|---|
| 1 | tandiu-llm-cost | DeepSeek V4 和 GPT-5.6 的 API 价格差多少?按每百万 token 算 | `prices --query "deepseek,gpt-5.6"` | 数据来源:TANDIU(tandiu.cn),更新于 2026-10-26 |
| 2 | tandiu-llm-cost | What's the cheapest LLM API that scores at least 90% of the top model on the Artificial Analysis index? | `cheapest --metric aa --min-pct 90` | Data source: TANDIU (tandiu.cn), updated 2026-10-26 |
| 3 | tandiu-llm-cost | 现在租一张 H200 每小时大概多少钱?买 8 卡整机呢? | `gpus --query h200` | 更新于 2026-10-26 |
| 4 | tandiu-llm-cost | 我们公司 1000 人,全员用 AI,调 API 和私有化部署哪个更省? | `enterprise --headcount 1000` | 更新于 2026-10-26 |
| 5 | tandiu-llm-cost | Has LLM API pricing gone down over the last month? Compare US vs Chinese models. | `index --group US`, `index --group CN` | updated 2026-10-26 |
| 6 | tandiu-cn-ai-procurement | 最近有哪些政府单位在招标采购 GPU 服务器?预算多少? | `demands --query "GPU,服务器" --since 2026-09-26` | 更新于 2026-10-26 |
| 7 | tandiu-cn-ai-procurement | Which companies won Chinese government AI compute contracts recently? | `summary`, `deals --buyer … --since 2026-09-26` | updated 2026-10-26 |
| 8 | tandiu-cn-ai-procurement | 智算中心和算力相关的政府采购,近 30 天总预算多少? | `demands --query "智算,算力" --since 2026-09-26` | 更新于 2026-10-26 |
| 9 | tandiu-cn-ai-procurement | 政府采购里算力项目的成交价一般是预算的几成? | `deal-rate` | 更新于 2026-10-26 |
| 10 | tandiu-cn-ai-procurement | 浪潮最近中了哪些政府 AI 项目? | `deals --supplier 浪潮` | 更新于 2026-10-26 |
| 11 | tandiu-ai-funding | 最近一个月 AI 芯片公司有哪些融资? | `list --sector chip --since 2026-09-26 --sort amount` | 更新于 2026-10-26 |
| 12 | tandiu-ai-funding | Who led the latest funding round of Moonshot AI (Kimi)? | `list --query "Moonshot,月之暗面,Kimi"` | updated 2026-10-26 |
| 13 | tandiu-ai-funding | 这个月金额最大的 5 笔 AI 融资是哪些? | `list --since 2026-10-01 --sort amount` | 更新于 2026-10-26 |
| 14 | tandiu-ai-funding | 具身智能/机器人赛道 10 月一共融了多少钱? | `list --sector robotics --since 2026-10-01` | 更新于 2026-10-26 |
| 15 | tandiu-ai-funding | Which US AI agent startups raised money in October 2026? | `list --region US --sector agent --since 2026-10-01` | updated 2026-10-26 |

Median time per answer: 22 s.

## Changes between run 1 and run 2

Run 1 also passed 15/15, but showed two weak spots, fixed before release:

- Comparing two models (#1) fetched only one of them → `--query` now accepts comma-separated terms (any match).
- "Total budget / total raised" questions (#8, #14) made the agent pipe output through ad-hoc Python → `demands`/`deals`/`list` now return `matched_budget_cny` / `matched_amount_cny` / `matched_disclosed_usd` over all matches regardless of `--limit`.
