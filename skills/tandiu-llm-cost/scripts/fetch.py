#!/usr/bin/env python3
"""TANDIU LLM / GPU cost data (read-only). Python standard library only.

Fetches public JSON from https://www.tandiu.cn (falls back to the mainland mirror
https://tandiuai.cn), filters locally and prints compact JSON to stdout.
GET only, 10 s timeout, no files written, no other hosts contacted.

  python fetch.py prices   [--country US|CN] [--vendor X] [--query X] [--sort blended|input|output|aa|livebench] [--limit N]
  python fetch.py cheapest [--metric aa|livebench] [--min-score S | --min-pct P] [--country CN] [--limit N]
  python fetch.py index    [--group CN|US|ALL] [--since YYYY-MM-DD]
  python fetch.py gpus     [--query h20] [--china-only] [--rental-only]
  python fetch.py hardware                       # per-GPU self-hosting unit economics (CNY per 1M tokens)
  python fetch.py enterprise [--headcount 10|100|1000|10000] [--query bank]
  python fetch.py roles    [--query lawyer] [--usage light|standard|heavy]
  python fetch.py history  --model X [--since D] [--until D]   # Pro: needs env TANDIU_API_KEY
"""
import argparse, datetime, json, os, sys, urllib.parse, urllib.request

SKILL, VERSION = "tandiu-llm-cost", "0.1.0"
BASES = ("https://www.tandiu.cn", "https://tandiuai.cn")  # main site, then mainland mirror
HEADERS = {"User-Agent": f"TANDIU-Skill/{SKILL}/{VERSION}", "X-TANDIU-Client": "skill", "Accept": "application/json"}


def get(path):
    """GET a public JSON file; returns (data, base_url)."""
    err = None
    for base in BASES:
        try:
            req = urllib.request.Request(base + path, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode("utf-8")), base
        except Exception as e:  # try the mirror next
            err = e
    sys.exit(json.dumps({"error": f"TANDIU unreachable: {err}"}))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward the Pro key to another URL."""
    def redirect_request(self, *args, **kwargs):
        return None


def get_pro(path, params):
    """Pro API on the main site only; the key is read from the environment and never stored."""
    key = os.environ.get("TANDIU_API_KEY", "").strip()
    if not key:
        sys.exit(json.dumps({"error": "Pro data needs env TANDIU_API_KEY (https://www.tandiu.cn/en/api); use free commands instead"}))
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(f"{BASES[0]}{path}?{q}", headers={**HEADERS, "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.build_opener(_NoRedirect).open(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8")), BASES[0]
    except Exception as e:
        sys.exit(json.dumps({"error": f"Pro request failed: {e}"}))


def out(data, page, updated, base):
    print(json.dumps({"source": {"name": "TANDIU", "page": page, "updated": updated, "via": base},
                      "data": data}, ensure_ascii=False, indent=1))


def has(text, q):
    """Substring match; comma-separated q matches any term (e.g. "deepseek,gpt-5.6")."""
    return not q or any(t.strip().lower() in (text or "").lower() for t in q.split(",") if t.strip())


def scores():
    ev, _ = get("/data/evaluations_latest.json")
    s = {}
    for m in ev.get("matched", []):
        aa = (m.get("artificial_analysis") or {}).get("intelligence_index")
        lb = (m.get("livebench") or {}).get("overall_score")
        s[m["litellm_key"]] = {"aa_index": aa, "livebench": lb}
    return s


def model_rows(a):
    d, base = get("/data/latest.json")
    sc = scores()
    rows = []
    for r in d["rows"]:
        if a.country and (r.get("country") or "").upper() != a.country.upper():
            continue
        if not has(r.get("vendor"), a.vendor) or not has(r.get("display"), getattr(a, "query", None)):
            continue
        rows.append({"model": r["display"], "vendor": r["vendor"], "country": r["country"],
                     "input_usd_per_1m": r.get("input_usd_per_1m"), "output_usd_per_1m": r.get("output_usd_per_1m"),
                     "blended_usd_per_1m": r.get("blended_usd_per_1m"), "cache_read_usd_per_1m": r.get("cache_read_usd_per_1m"),
                     "blended_rmb_per_1m": r.get("blended_rmb_per_1m"), "context_k": r.get("context_k"),
                     **sc.get(r.get("litellm_key"), {"aa_index": None, "livebench": None}),
                     "source_url": r.get("source_url"), "verified_at": r.get("verified_at")})
    return rows, d["summary"], base


def cmd_prices(a):
    rows, summ, base = model_rows(a)
    key = {"blended": "blended_usd_per_1m", "input": "input_usd_per_1m", "output": "output_usd_per_1m",
           "aa": "aa_index", "livebench": "livebench"}[a.sort]
    desc = a.sort in ("aa", "livebench")
    num = lambda v: isinstance(v, (int, float))
    rows = sorted((r for r in rows if num(r[key])), key=lambda r: r[key], reverse=desc) + [r for r in rows if not num(r[key])]
    out({"fx_usdcny": summ.get("fx_usdcny"), "n_models": len(rows), "models": rows[:a.limit]},
        "https://www.tandiu.cn/token-market", summ.get("date"), base)


def cmd_cheapest(a):
    a.vendor = None
    rows, summ, base = model_rows(a)
    key = "aa_index" if a.metric == "aa" else "livebench"
    scored = [r for r in rows if isinstance(r[key], (int, float)) and isinstance(r["blended_usd_per_1m"], (int, float))]
    top = max((r[key] for r in scored), default=0)
    floor = a.min_score if a.min_score is not None else top * (a.min_pct or 90) / 100
    hit = sorted((r for r in scored if r[key] >= floor), key=lambda r: r["blended_usd_per_1m"])
    out({"metric": key, "threshold": round(floor, 2), "top_score": top, "models": hit[:a.limit]},
        "https://www.tandiu.cn/price-index", summ.get("date"), base)


def cmd_index(a):
    d, base = get("/data/price_index.json")
    groups = [a.group] if a.group else ["CN", "US", "ALL"]
    res = {}
    for g in groups:
        s = [p for p in d["series"][g] if not a.since or p[0] >= a.since]
        last = s[-1] if s else None
        prev = next((p for p in reversed(s) if last and p[0] <= _days_before(last[0], 30)), s[0] if s else None)
        res[g] = {"latest": last, "30d_ago": prev,
                  "change_30d_pct": round((last[1] / prev[1] - 1) * 100, 2) if last and prev and prev[1] else None,
                  "median_blended_usd_per_1m": d["median_blended_usd"].get(g), "models_listed": d["models_listed"].get(g),
                  "series_tail": s[-14:]}
    out({"unit": d.get("unit"), "base_date": d.get("base_date"), "groups": res, "frontier_aa": d.get("frontier_aa")},
        "https://www.tandiu.cn/price-index", d.get("asof"), base)


def _days_before(iso, n):
    return (datetime.date.fromisoformat(iso) - datetime.timedelta(days=n)).isoformat()


def cmd_gpus(a):
    d, base = get("/data/gpu_prices.json")
    rows = []
    for g in d["gpus"]:
        if not (has(g["id"], a.query) or has(g["name"], a.query)):
            continue
        if a.china_only and not g.get("china_available"):
            continue
        if a.rental_only and not g.get("cloud_rental"):
            continue
        rows.append({k: g.get(k) for k in ("id", "name", "vram_gb", "bandwidth_gb_s", "fp16_dense_tflops", "china_available",
                                           "price_unit", "list_price", "market_price", "cloud_rental")})
    out({"note": d.get("note"), "gpus": rows}, "https://www.tandiu.cn/compute", d.get("as_of"), base)


def cmd_hardware(a):
    d, base = get("/data/enterprise_ai_cost.json")
    out({"deploy_model": d.get("deploy_model"), "assumptions": d.get("assumptions"), "hardware": d.get("hardware")},
        "https://www.tandiu.cn/local-deploy", d.get("as_of"), base)


def cmd_enterprise(a):
    d, base = get("/data/enterprise_ai_cost.json")
    rows = []
    for p in d["profiles"]:
        if a.headcount and p["headcount"] != a.headcount:
            continue
        if a.query and not (has(p.get("industry"), a.query) or has(p.get("name"), a.query) or has(p.get("id"), a.query)):
            continue
        rows.append({k: p.get(k) for k in ("id", "name", "industry", "headcount", "ai_intensity", "monthly_input_tokens",
                                           "monthly_output_tokens", "options", "cheapest", "cheapest_self_hosted")})
    out({"currency": d.get("currency"), "deploy_model": d.get("deploy_model"), "profiles": rows},
        "https://www.tandiu.cn/enterprise-ai", d.get("as_of"), base)


def cmd_roles(a):
    d, base = get("/data/role_token_budget.json")
    rows = []
    for r in d["roles"]:
        if a.query and not (has(r["id"], a.query) or has(r["name"], a.query) or has(r.get("group"), a.query)):
            continue
        usage = {a.usage: r["usage"][a.usage]} if a.usage else r["usage"]
        rows.append({"id": r["id"], "name": r["name"], "group": r.get("group"), "monthly_salary_cny": r.get("monthly_salary_cny"),
                     "min_aa_index": r.get("min_aa_index"), "usage": usage})
    out({"currency": d.get("currency"), "method": d.get("method"), "roles": rows},
        "https://www.tandiu.cn/token-budget", d.get("as_of"), base)


def cmd_history(a):
    d, base = get_pro("/api/v1/llm-price-history", {"model": a.model, "since": a.since, "until": a.until, "limit": a.limit})
    out(d, "https://www.tandiu.cn/en/api", (d.get("asof") or d.get("as_of")) if isinstance(d, dict) else None, base)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prices"); s.add_argument("--country"); s.add_argument("--vendor"); s.add_argument("--query")
    s.add_argument("--sort", default="blended", choices=["blended", "input", "output", "aa", "livebench"]); s.add_argument("--limit", type=int, default=20)
    s = sub.add_parser("cheapest"); s.add_argument("--metric", default="aa", choices=["aa", "livebench"])
    s.add_argument("--min-score", type=float); s.add_argument("--min-pct", type=float); s.add_argument("--country"); s.add_argument("--limit", type=int, default=10)
    s = sub.add_parser("index"); s.add_argument("--group", choices=["CN", "US", "ALL"]); s.add_argument("--since")
    s = sub.add_parser("gpus"); s.add_argument("--query"); s.add_argument("--china-only", action="store_true"); s.add_argument("--rental-only", action="store_true")
    sub.add_parser("hardware")
    s = sub.add_parser("enterprise"); s.add_argument("--headcount", type=int, choices=[10, 100, 1000, 10000]); s.add_argument("--query")
    s = sub.add_parser("roles"); s.add_argument("--query"); s.add_argument("--usage", choices=["light", "standard", "heavy"])
    s = sub.add_parser("history"); s.add_argument("--model", required=True); s.add_argument("--since"); s.add_argument("--until"); s.add_argument("--limit", type=int, default=200)
    a = p.parse_args()
    globals()["cmd_" + a.cmd](a)


if __name__ == "__main__":
    main()
