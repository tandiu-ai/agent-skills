# 字段说明 · tandiu-cn-ai-procurement

所有命令输出 `{"source": {...}, "data": {...}}`。`source.updated` 是数据日期,`source.page` 是对应网页。数据每日更新(北京时间上午)。

## demands(/data/procurement_demands.json 的 verified_demands[])

| 字段 | 含义 | 单位 |
|---|---|---|
| date | 公告发布日期 | YYYY-MM-DD |
| title / project_id | 公告标题 / 项目编号 | — |
| buyer / region | 采购单位 / 地区(省或市) | — |
| budget_cny | 采购预算(公告披露值,未披露为 null) | 人民币元 |
| response_deadline | 投标/响应截止时间(公告原文) | 文本 |
| compute_tags | 算力分类标签,如 GPU、智算、服务器、大模型 | — |
| channel_label | 公告类型,如 中央公开招标、地方竞争性磋商 | — |
| source_url | 政府采购网原始公告 | — |

顶层 `total_matched` 命中条数,`matched_budget_cny` 全部命中条目的预算合计(元,不受 `--limit` 限制),`matched_with_budget` 其中披露预算的条数;deals 对应 `matched_amount_cny` / `matched_with_amount`。

`summary`:`indexed_announcements` 扫描公告总数,`compute_candidates` 算力候选,`verified_complete_demands` 核验通过条数,`disclosed_budget_cny` 披露预算合计(元)。

## deals(/data/procurement_deals.json 的 verified_deals[])

字段同上,另有 `suppliers`(中标供应商列表,每项 `name` + `amount_cny`)、`amount_cny`(成交总额,元)。

## summary(/data/procurement_summary.json)

- `demands`:`total`、`new_7d`、`count_30d`、`budget_30d_cny`、`by_category_30d`(算力硬件设备 / 算力租赁/服务 / 大模型开发服务 / 运维服务 / 其他)、`top_budget_30d`(含站内详情页 `url`)、`upcoming_deadlines`。
- `deals`:`total`、`new_7d`、`count_30d`、`amount_30d_cny`、`by_category_30d`、`top_suppliers`、`top_amount_30d`。
- `budget_to_award`:配对数与成交/预算比例中位数、P10、P90。

## deal-rate(/data/budget_deal_rate.json)

`overall` / `groups`(按类别 `category:*`、按预算规模 `band:*`)的 `n`、`median`、`mean`、`p10`、`p90`、`min`、`max`;`ratio` 为小数(0.98 = 成交价为预算的 98%)。`recent_pairs` 每对含需求与成交日期、`lead_days`、预算、成交额、两份公告链接。`history_overall` 为逐日中位数。
