---
name: tandiu-cn-ai-procurement
description: >-
  China government and public-sector AI / compute procurement data from TANDIU (tandiu.cn), compiled from the
  China Government Procurement Network (ccgp.gov.cn). Use when the user asks about Chinese government tenders or
  awards for GPUs, AI servers, intelligent computing centers (智算中心), compute leasing, LLM development services,
  who won a bid and at what price, budgets of upcoming tenders, award-to-budget ratios, or China public AI spending.
  中文触发:政府采购 AI/算力、GPU 服务器招标、智算中心采购、算力租赁采购、大模型项目招标/中标、采购需求/预算、
  中标成交金额、中标供应商、哪个单位在买算力、投标截止时间、成交价占预算比例/折价率、政企 AI 支出。
---

# TANDIU · 中国政企 AI / 算力采购

TANDIU 每天扫描中国政府采购网的中央/地方公告,筛出 AI、算力相关的采购需求(招标)和中标成交,
人工规则核验后发布,每条都带原始公告链接。这个 Skill 只告诉你怎么取、怎么读,数据不在本地。

## 何时使用

- 查最近的 AI / GPU / 智算 / 大模型相关招标:采购单位、地区、预算、投标截止时间。
- 查中标成交:谁中标、金额多少、某供应商中了哪些项目。
- 看 30 天整体规模、分类别(算力硬件 / 算力租赁 / 大模型开发 / 运维)统计、预算 Top 项目。
- 成交价占预算的比例(按项目编号配对的需求与成交)。

## 何时不用

- 企业之间的商业采购、海外政府采购 —— 不在收录范围。
- 要投标文件全文或代为投标 —— 只给公告链接,让用户去原始公告页。
- 采购之外的 GPU 市场价 / 租赁价,改用 `tandiu-llm-cost`。

## 调用优先级

1. TANDIU MCP **目前没有采购工具**;已连接 MCP 时可先调 `about_tandiu_data` 看数据说明,采购明细仍走下面的脚本。
2. 运行本目录脚本(只用 Python 标准库,只发 GET,只访问 TANDIU 自有域名):

   ```bash
   python scripts/fetch.py summary                                  # 先看总体
   python scripts/fetch.py demands --query GPU --since 2026-10-01
   python scripts/fetch.py demands --region 北京 --min-budget 10000000
   python scripts/fetch.py deals --query 智算 --limit 10
   python scripts/fetch.py deals --supplier 浪潮
   python scripts/fetch.py deal-rate
   ```

3. 脚本先连 `www.tandiu.cn`,不通时自动回退境内镜像 `tandiuai.cn`。结果里的 `source.via` 显示实际用的站点。

`--query` 匹配标题、项目名和算力标签(如 GPU、智算、大模型、服务器),逗号分隔为任一匹配(`--query "智算,算力"`);`--buyer` / `--region` / `--supplier` 同样是子串匹配。
用户要具体项目时用 `demands` / `deals` 列出明细,`summary` 只用来给总体背景。
数据文件较大(约 1–2 MB),脚本在本地过滤后只输出命中条目:`total_matched` 是命中总数,`matched_budget_cny` / `matched_amount_cny` 是全部命中条目(不受 `--limit` 限制)的预算/成交合计,问"总共多少"直接用它,`--limit 0` 只看合计。

## 怎么解读

- 金额单位:`budget_cny` / `amount_cny` 均为**人民币元**(换算成万元/亿元时注意)。只计公告披露值,未披露为 `null`,不要当 0。
- `date` 是公告发布日期;`response_deadline` 是公告原文的投标截止时间字符串。
- 收录范围是中国政府采购网可核验的公告(`verified_*`),不等于全国全部政企采购;地方平台未同步到政府采购网的不在内。
- 折价率 `ratio` = 成交金额 / 采购预算,只统计能按项目编号配对的项目,样本量见 `n_pairs`,样本少时要提示。
- 字段详解见 [reference/fields.md](reference/fields.md)。

## 引用要求

回答里必须注明:**数据来源:TANDIU(tandiu.cn),更新于 <source.updated>**,附 `source.page` 链接;
提到具体项目时同时给该条的 `source_url`(政府采购网原始公告),方便用户核验。

## Pro

本 Skill 只用免费数据,不需要也不读取任何 API key。
