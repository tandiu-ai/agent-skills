#!/usr/bin/env python3
"""TANDIU AI funding rounds (read-only). Python standard library only.

Fetches public JSON from https://www.tandiu.cn (falls back to the mainland mirror
https://tandiuai.cn), filters locally and prints compact JSON to stdout.
GET only, 10 s timeout, no files written, no other hosts contacted.

  python fetch.py list  [--region US|CN|OTHER] [--sector chip] [--query Moonshot] [--since YYYY-MM-DD]
                        [--min-usd 100000000] [--sort date|amount] [--limit N]
  python fetch.py stats [--region CN] [--since YYYY-MM-DD]      # count and disclosed USD by sector
Sectors: foundation_model ai_app agent chip compute robotics autonomous infra_tools vertical other
"""
import argparse, json, sys, urllib.request
from collections import defaultdict

SKILL, VERSION = "tandiu-ai-funding", "0.1.1"
BASES = ("https://www.tandiu.cn", "https://tandiuai.cn")  # main site, then mainland mirror
HEADERS = {"User-Agent": f"TANDIU-Skill/{SKILL}/{VERSION}", "X-TANDIU-Client": "skill", "Accept": "application/json"}
SECTORS = ["foundation_model", "ai_app", "agent", "chip", "compute", "robotics", "autonomous", "infra_tools", "vertical", "other"]


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


def out(data, page, updated, base):
    print(json.dumps({"source": {"name": "TANDIU", "page": page, "updated": updated, "via": base},
                      "data": data}, ensure_ascii=False, indent=1))


def has(text, q):
    """Substring match; comma-separated q matches any term (e.g. "deepseek,gpt-5.6")."""
    return not q or any(t.strip().lower() in (text or "").lower() for t in q.split(",") if t.strip())


def deals(a):
    d, base = get("/data/ai_funding.json")
    rows = []
    for r in d["deals"]:
        if a.region and r.get("region") != a.region.upper():
            continue
        if getattr(a, "sector", None) and r.get("sector") != a.sector:
            continue
        if a.since and (r.get("date") or "") < a.since:
            continue
        q = getattr(a, "query", None)
        if q:
            text = " ".join(str(x) for x in [r.get("company"), r.get("company_en"), r.get("company_zh"), r.get("product"),
                                              *(r.get("aliases") or []), *(r.get("lead_investors") or []), *(r.get("investors") or []),
                                              *(r.get("lead_investors_en") or []), *(r.get("investors_en") or [])] if x)
            if not has(text, q):
                continue
        if getattr(a, "min_usd", None) and (r.get("amount_usd") or 0) < a.min_usd:
            continue
        rows.append(r)
    return rows, d, base


def slim(r):
    keep = ("date", "company", "company_en", "company_zh", "region", "country", "business_en", "business_zh", "sector", "round",
            "status", "amount_text", "amount_usd", "amount_cumulative", "valuation_text", "valuation_usd",
            "amount_conflict", "valuation_conflict", "lead_investors", "investors", "website")
    s = {k: r.get(k) for k in keep if r.get(k) not in (None, "", [])}
    src = sorted(r.get("sources") or [], key=lambda x: x.get("date") or "", reverse=True)
    s["n_sources"] = len(src)
    # newest reports first: early reports of a round often carry a preliminary amount
    s["sources"] = [{k: x.get(k) for k in ("title", "publisher", "date", "url")} for x in src[:3]]
    return s


def cmd_list(a):
    rows, d, base = deals(a)
    if a.sort == "amount":
        rows.sort(key=lambda r: r.get("amount_usd") or 0, reverse=True)
    else:
        rows.sort(key=lambda r: r.get("date") or "", reverse=True)
    single = [r for r in rows if r.get("amount_usd") and not r.get("amount_cumulative")]
    out({"definition": d.get("definition"), "total_matched": len(rows), "matched_disclosed_usd": round(sum(r["amount_usd"] for r in single)),
         "matched_with_amount": len(single), "deals": [slim(r) for r in rows[:a.limit]]},
        "https://www.tandiu.cn/funding", (d.get("updated_at") or "")[:10], base)


def cmd_stats(a):
    rows, d, base = deals(a)
    agg = defaultdict(lambda: {"deals": 0, "with_amount": 0, "disclosed_usd": 0.0})
    for r in rows:
        g = agg[r.get("sector") or "other"]
        g["deals"] += 1
        # cumulative multi-round totals are not single rounds; keep them out of sums
        if r.get("amount_usd") and not r.get("amount_cumulative"):
            g["with_amount"] += 1
            g["disclosed_usd"] += r["amount_usd"]
    by = sorted(({"sector": k, **v, "disclosed_usd": round(v["disclosed_usd"])} for k, v in agg.items()), key=lambda x: -x["disclosed_usd"])
    out({"total_deals": len(rows), "by_sector": by, "note": "disclosed_usd sums only rounds with a stated amount; cumulative totals excluded"},
        "https://www.tandiu.cn/funding", (d.get("updated_at") or "")[:10], base)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("--region", choices=["US", "CN", "OTHER", "us", "cn", "other"]); s.add_argument("--sector", choices=SECTORS)
    s.add_argument("--query"); s.add_argument("--since"); s.add_argument("--min-usd", type=float)
    s.add_argument("--sort", default="date", choices=["date", "amount"]); s.add_argument("--limit", type=int, default=20)
    s = sub.add_parser("stats")
    s.add_argument("--region", choices=["US", "CN", "OTHER", "us", "cn", "other"]); s.add_argument("--since")
    a = p.parse_args()
    {"list": cmd_list, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
