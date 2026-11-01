# Changelog

## v0.1.2 — 2026-11-01

- tandiu-llm-cost: `prices` / `cheapest` now include `long_context` (long-context price tier: above `threshold_tokens` the whole request is billed at that tier) and `intro_price` (introductory price end date and regular price). Previously long-context requests were under-costed, e.g. Claude Haiku 5.5 above 100K prompt tokens.

## v0.1.1 — 2026-10-26

- tandiu-ai-funding: `list` shows the newest sources first (early reports often carry a preliminary amount), plus `n_sources`, `amount_conflict` and `valuation_conflict`.

## v0.1.0 — 2026-10-26

- First release: tandiu-llm-cost, tandiu-cn-ai-procurement, tandiu-ai-funding.
- Scripts: Python stdlib, HTTPS GET only, main site → tandiuai.cn mirror fallback, attribution headers.
