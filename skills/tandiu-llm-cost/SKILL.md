---
name: tandiu-llm-cost
description: >-
  Live LLM API and GPU cost data from TANDIU (tandiu.cn). Use when the user asks to compare LLM API prices,
  estimate token cost or a monthly AI budget, find the cheapest model that reaches a benchmark score, check
  GPU purchase or cloud rental prices (H100/H200/H20/B200/B300, Ascend 910B/910C, RTX 5090/PRO 6000), size
  self-hosting an open-weights model, or decide API vs self-hosting / private cloud for a company.
  中文触发:大模型 API 价格对比、Token 成本/费用测算、每月 AI 预算、同等评测分最便宜的模型、国产 vs 美国模型价格、
  价格指数/降价、GPU 价格/租赁时租/整机价、显卡选型、开源模型本地部署要几张卡、私有化部署 vs 调 API 哪个省、企业 AI 成本。
---

# TANDIU · LLM / GPU 成本

TANDIU 每天从厂商官方定价页、公开报价接口抓取大模型牌价和 GPU 价格,附来源链接和核价日期。
这个 Skill 只告诉你怎么取、怎么读,数据不在本地。

## 何时使用

- 比较模型 API 价格(美元或人民币/百万 tokens),或某个模型的官方牌价、缓存价、上下文长度。
- 给定能力门槛(Artificial Analysis 指数 / LiveBench 分)找最便宜的模型。
- 中美模型整体价格走势、近 30 天降价幅度。
- GPU 规格、出厂价、中国市场价、云端时租及 7 天变化。
- 开源权重模型自部署要几张卡、单位 Token 成本;企业(10~10000 人)API vs 公有云/私有云/本地自部署月成本;某岗位每月 Token 预算。

## 何时不用

- 用户要实时下单、开 API key、购买 GPU —— TANDIU 不卖算力,只提供数据。
- 问模型能力本身(写代码好不好)而不涉及价格 —— 评测分可以引用,但不要只凭本 Skill 下能力结论。
- 价格以外的三方渠道/转售问题,直接让用户看 https://www.tandiu.cn/channel-prices。

## 调用优先级

1. **已连接 TANDIU MCP**(`https://www.tandiu.cn/mcp`,工具名如 `list_llm_prices`)→ 直接调 MCP 工具:

   | 需求 | MCP 工具 |
   |---|---|
   | 牌价 + 评测 | `list_llm_prices`(country / vendor / query / sort_by) |
   | 同等分数最便宜 | `cheapest_model_for_score` |
   | 价格指数 / 调价记录 | `get_price_index` / `list_price_changes` |
   | GPU | `list_gpu_prices` |
   | 自部署测算(指定模型 + GPU) | `estimate_self_hosting` |
   | 岗位预算 / 企业成本 | `estimate_role_token_budget` / `estimate_enterprise_ai_cost` |
   | 国产开源模型境外上架价 | `list_overseas_listings` |

2. **未连接 MCP** → 运行本目录脚本(只用 Python 标准库,只发 GET,只访问 TANDIU 自有域名):

   ```bash
   python scripts/fetch.py prices --country CN --sort blended --limit 10
   python scripts/fetch.py prices --query "deepseek,gpt-5.6"     # 逗号分隔 = 任一匹配,比较多个模型一次取齐
   python scripts/fetch.py cheapest --metric aa --min-pct 90 --country CN
   python scripts/fetch.py index --group ALL
   python scripts/fetch.py gpus --query h20            # --china-only / --rental-only
   python scripts/fetch.py hardware                    # 每款 GPU 自部署的单位 Token 成本
   python scripts/fetch.py enterprise --headcount 1000 # --query hospital / bank / law
   python scripts/fetch.py roles --query backend --usage heavy
   ```

3. 脚本会先连 `www.tandiu.cn`,不通时自动回退境内镜像 `tandiuai.cn`(只有静态数据,没有 MCP)。结果里的 `source.via` 显示实际用的站点。

指定某个开源模型 + 某款 GPU 的自部署测算只有 MCP 有;没有 MCP 时用 `hardware` 的单位经济数据,并给出模型页 `https://www.tandiu.cn/local-deploy-<model-key>`。

## 怎么解读

- 单位:`*_usd_per_1m` = 美元/百万 tokens;`*_rmb_per_1m`、`*_cny` = 人民币。混合价 blended = (3×输入 + 1×输出)/4。
- 牌价是厂商**官方**列表价,不含折扣、批量价、三方渠道价。`verified_at` 是核价日期,`source_url` 是厂商定价页。
- 评测分 `aa_index`(Artificial Analysis 智能指数)、`livebench`(LiveBench 2.0 总分)是第三方公开榜单的转录,TANDIU 不自测;为 `null` 表示该榜未收录,不要当 0。
- GPU:SXM 卡(B300/B200/H200/H100)按 HGX 8 卡整机报价(`per_8gpu_node_cny`),也给出单卡折算;`cloud_rental` 是国际云市场时租,不代表中国大陆整卡采购价;价格均为区间。`china_available` 可能是一段说明文字(出口管制状态)。
- 企业/岗位/自部署数字是**模型估算**(假设见 `assumptions` / `method`),不是实测账单;回答时说明是估算并给出关键假设。
- 字段详解见 [reference/fields.md](reference/fields.md)。

## 引用要求

回答里必须注明:**数据来源:TANDIU(tandiu.cn),更新于 <source.updated>**,并附 `source.page` 链接;引用单个模型价格时同时给厂商 `source_url`。

## Pro(可选)

若环境变量 `TANDIU_API_KEY` 存在,可取逐日官方牌价历史:`python scripts/fetch.py history --model gpt-5.6 --since 2026-08-01`(MCP 对应 `get_llm_price_history`)。不存在就只用上面的免费命令,不要向用户索要 key,也不要把 key 写进任何文件。
