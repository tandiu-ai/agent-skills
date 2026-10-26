# 字段说明 · tandiu-llm-cost

所有命令输出 `{"source": {...}, "data": {...}}`。`source.updated` 是数据日期(北京时间),`source.page` 是对应网页,`source.via` 是实际访问的站点。

## prices / cheapest(来源 /data/latest.json + /data/evaluations_latest.json,每日更新)

| 字段 | 含义 | 单位 |
|---|---|---|
| model / vendor / country | 模型显示名、厂商、厂商所在国(US/CN/…) | — |
| input_usd_per_1m / output_usd_per_1m | 官方输入/输出牌价 | 美元/百万 tokens |
| blended_usd_per_1m | 混合价 = (3×输入+1×输出)/4 | 美元/百万 tokens |
| cache_read_usd_per_1m | 缓存命中读取价;空字符串 = 厂商未公布 | 美元/百万 tokens |
| blended_rmb_per_1m | 混合价人民币(按 `fx_usdcny` 换算,国产模型为原价) | 元/百万 tokens |
| context_k | 上下文长度 | 千 tokens |
| aa_index | Artificial Analysis Intelligence Index | 分 |
| livebench | LiveBench 2.0 总分 | 分 |
| source_url / verified_at | 厂商定价页 / 核价日期 | — |
| threshold / top_score(cheapest) | 本次筛选门槛 / 该指标最高分 | 分 |

## index(/data/price_index.json,每日)

链式价格指数,基期 `base_date`=100。`latest` / `30d_ago` 为 `[日期, 指数]`;`change_30d_pct` 为 30 天变化百分比;`median_blended_usd_per_1m` 为该组模型混合价中位数;`frontier_aa` 为价格—能力前沿上的模型。

## gpus(/data/gpu_prices.json,时租每日、整卡报价每周)

| 字段 | 含义 |
|---|---|
| vram_gb / bandwidth_gb_s / fp16_dense_tflops | 显存 GB / 显存带宽 GB/s / FP16 稠密算力 TFLOPS(RTX 系列为折算值) |
| price_unit | 报价单位;SXM 卡为 "8-GPU HGX node" |
| list_price | 出厂/渠道公开价,`per_card_cny` 与 `per_8gpu_node_cny` 都是 [低, 高] 区间,含 `as_of`、`source`、`note` |
| market_price | 近期公开报道的中国市场实际价,同上结构 |
| cloud_rental | 国际云市场时租 `cny_per_gpu_hour` / `usd_per_gpu_hour` 区间,`change_vs_7d_ago` 为 7 天变化(小数,0.14=+14%) |
| china_available | true/false,或出口管制状态说明 |

## hardware(/data/enterprise_ai_cost.json 的 hardware[],每日)

每款 GPU 跑 `deploy_model`(默认开源模型)的单位经济:`cards_per_replica` 每副本卡数、`est_output_tok_s` 估算输出吞吐、`replica_hardware_cny` 硬件价、`local_monthly_cny` 本地月成本、`cny_per_1m_tokens_workhours_full` / `_24x7_full` / `_cloud_on_demand` 不同使用方式下的每百万 tokens 成本(元)。

## enterprise(profiles[])

12 个企业样本(10/100/1000/10000 人 × 3 行业,id 如 `law_firm_10`、`hospital_1000`、`bank_10000`)。`options[]` 每项为一种方案:`api_opt`(按岗位选模型 API)、`api_same`(同一开源模型官方 API)、`public`(公有云按需)、`private`(私有云包年)、`local`(本地自购),`monthly_cny` 为月成本(元)。`cheapest` / `cheapest_self_hosted` 指出最省方案。

## roles(roles[])

32 个岗位,`usage.light|standard|heavy` 含每日调用次数、平均输入/输出 tokens、月度 tokens,`optimal`(满足能力门槛的最优模型)与 `domestic`(国产最优)的 `monthly_cost_cny`。数字为示例性估算,假设见 `method`。

## history(Pro,/api/v1/llm-price-history)

需环境变量 `TANDIU_API_KEY`。逐日官方牌价(USD+RMB/百万 tokens)及来源 URL,2026-07 起。
