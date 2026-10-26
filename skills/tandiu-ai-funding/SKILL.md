---
name: tandiu-ai-funding
description: >-
  AI company funding rounds from TANDIU (tandiu.cn), mainly US and China, merged and de-duplicated across news
  outlets with source links. Use when the user asks who raised money in AI, recent funding rounds or valuations of
  an AI / LLM / agent / AI chip / GPU cloud / robotics / autonomous driving company, which investors backed whom,
  the largest AI rounds this month, or funding totals by sector or region.
  中文触发:AI 融资、大模型公司融资/估值、AI 芯片融资、算力/智算公司融资、具身智能/机器人融资、Agent 创业公司融资、
  某公司最新一轮融资、谁领投、某机构投了哪些 AI 公司、本月最大融资、中美 AI 投融资对比、按赛道统计融资额。
---

# TANDIU · AI 投融资

TANDIU 每天从多家媒体抓取 AI 公司融资新闻,抽取公司、轮次、金额、估值、投资方,多源合并去重,并核查旧闻翻炒。
金额只取报道原文。这个 Skill 只告诉你怎么取、怎么读,数据不在本地。

## 何时使用

- 查某家 AI 公司的融资记录、最新估值、领投方。
- 某机构投了哪些 AI 公司(`--query` 也匹配投资方名称)。
- 某时间段、某地区、某赛道(芯片、算力、大模型、Agent、机器人……)的融资列表或金额排行。
- 按赛道汇总融资笔数和披露金额。

## 何时不用

- 上市公司股价、二级市场交易、并购估值建模 —— 不在收录范围。
- 投资建议 —— 只陈述公开报道的事实,不做判断。
- 中国企业工商登记信息 —— 不提供。

## 调用优先级

1. **已连接 TANDIU MCP** → 调 `list_ai_funding`(region / sector / query / since / min_amount_usd / sort_by / limit)。
2. **未连接 MCP** → 运行本目录脚本(只用 Python 标准库,只发 GET,只访问 TANDIU 自有域名):

   ```bash
   python scripts/fetch.py list --since 2026-10-01 --sort amount --limit 10
   python scripts/fetch.py list --region CN --sector chip
   python scripts/fetch.py list --query "Sequoia"          # 公司、产品或投资方
   python scripts/fetch.py stats --region US --since 2026-10-01
   ```

3. 脚本先连 `www.tandiu.cn`,不通时自动回退境内镜像 `tandiuai.cn`。结果里的 `source.via` 显示实际用的站点。

赛道 `sector`:foundation_model(基础大模型)、ai_app(AI 应用)、agent、chip(芯片)、compute(算力/云)、robotics(机器人/具身)、autonomous(自动驾驶)、infra_tools(AI 基础设施工具)、vertical(行业 AI)、other。

## 怎么解读

- `date` 是最早报道日期,不一定是交割日;`status`:announced(公司官宣)/ reported(媒体报道,未官宣)。
- `amount_text` 是报道原文金额,`amount_usd` 按当日汇率折算的美元;未披露为空,不要估算。
- `amount_cumulative: true` 表示报道只给了多轮**累计**金额,不是单轮,不能计入合计或排名(`stats` 已排除)。
- `list` 输出的 `matched_disclosed_usd` 是全部命中条目(不受 `--limit` 限制、已排除累计金额)的披露金额合计,问"一共融了多少"直接用它。
- `--query` 逗号分隔为任一匹配(`--query "Moonshot,月之暗面"`),同时匹配投资方,搜机构名可能命中名字相近的其他机构,回答前核对 `lead_investors` / `investors`。
- 字段详解见 [reference/fields.md](reference/fields.md)。

## 引用要求

回答里必须注明:**数据来源:TANDIU(tandiu.cn),更新于 <source.updated>**,附 `source.page` 链接;
提到具体融资时附该条 `sources[].url` 中至少一条原始报道。

## Pro

本 Skill 只用免费数据,不需要也不读取任何 API key。
