# 字段说明 · tandiu-ai-funding

所有命令输出 `{"source": {...}, "data": {...}}`。`source.updated` 是数据日期,`source.page` 是对应网页。数据每日更新。

## list(/data/ai_funding.json 的 deals[])

| 字段 | 含义 | 单位 |
|---|---|---|
| date | 最早报道日期 | YYYY-MM-DD |
| company / company_en / company_zh | 公司名(原文/英文/中文) | — |
| region / country | US / CN / OTHER;ISO 国家代码 | — |
| business_en / business_zh | 主营业务一句话 | — |
| sector | 赛道,见 SKILL.md | — |
| round | 轮次,如 seed、angel、a、b、c、d、strategic、debt | — |
| status | announced 官宣 / reported 媒体报道 | — |
| amount_text | 报道原文金额 | 文本 |
| amount_usd | 折算美元(当日汇率),未披露为空 | 美元 |
| amount_cumulative | true = 多轮累计,不计入合计和排名 | — |
| valuation_text / valuation_usd | 估值原文 / 折算美元 | 美元 |
| lead_investors / investors | 领投 / 参投 | — |
| sources[] | 原始报道:title、publisher、date、url(按日期从新到旧,最多 3 条;`n_sources` 为总数) | — |
| amount_conflict / valuation_conflict | 与主值不同的其他报道金额/估值(原文+媒体) | 文本 |
| total_matched | 筛选命中总数(输出只列前 `--limit` 条) | 笔 |
| matched_disclosed_usd / matched_with_amount | 全部命中条目的披露金额合计(排除累计金额)/ 有金额的笔数 | 美元 / 笔 |

## stats

按赛道汇总:`deals` 笔数、`with_amount` 有披露金额的笔数、`disclosed_usd` 披露金额合计(美元,已排除累计金额)。
