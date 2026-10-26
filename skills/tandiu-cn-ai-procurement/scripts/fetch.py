#!/usr/bin/env python3
"""TANDIU China government AI / compute procurement data (read-only). Python standard library only.

Fetches public JSON from https://www.tandiu.cn (falls back to the mainland mirror
https://tandiuai.cn), filters locally and prints compact JSON to stdout.
GET only, 10 s timeout, no files written, no other hosts contacted.

  python fetch.py summary                                   # 30-day totals, by category, top budgets, top suppliers
  python fetch.py demands [--query GPU] [--buyer X] [--region 北京] [--since YYYY-MM-DD] [--min-budget CNY] [--limit N]
  python fetch.py deals   [--query 智算] [--buyer X] [--supplier X] [--region X] [--since D] [--min-amount CNY] [--limit N]
  python fetch.py deal-rate                                 # award price / budget ratio, overall and by category
"""
import argparse, json, sys, urllib.request

SKILL, VERSION = "tandiu-cn-ai-procurement", "0.1.0"
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


def out(data, page, updated, base):
    print(json.dumps({"source": {"name": "TANDIU", "page": page, "updated": updated, "via": base},
                      "data": data}, ensure_ascii=False, indent=1))


def has(text, q):
    """Substring match; comma-separated q matches any term (e.g. "deepseek,gpt-5.6")."""
    return not q or any(t.strip().lower() in (text or "").lower() for t in q.split(",") if t.strip())


def common(r, a):
    if a.since and (r.get("date") or "") < a.since:
        return False
    if not (has(r.get("title"), a.query) or has(r.get("project_name"), a.query) or has(" ".join(r.get("compute_tags") or []), a.query)):
        return False
    return has(r.get("buyer"), a.buyer) and has(r.get("region"), a.region)


def cmd_summary(a):
    d, base = get("/data/procurement_summary.json")
    out({k: d.get(k) for k in ("currency", "note", "demands", "deals", "budget_to_award", "pages")},
        "https://www.tandiu.cn/demand", d.get("asof"), base)


def cmd_demands(a):
    d, base = get("/data/procurement_demands.json")
    rows = [r for r in d["verified_demands"] if common(r, a) and (not a.min_budget or (r.get("budget_cny") or 0) >= a.min_budget)]
    rows.sort(key=lambda r: r.get("date") or "", reverse=True)
    keep = ("date", "title", "buyer", "region", "budget_cny", "response_deadline", "compute_tags", "project_id", "channel_label", "source_url")
    out({"total_matched": len(rows), "matched_budget_cny": sum(r.get("budget_cny") or 0 for r in rows),
         "matched_with_budget": sum(1 for r in rows if r.get("budget_cny")), "summary": d.get("summary"), "demands": [{k: r.get(k) for k in keep} for r in rows[:a.limit]]},
        "https://www.tandiu.cn/demand", (d.get("updated_at") or "")[:10], base)


def cmd_deals(a):
    d, base = get("/data/procurement_deals.json")
    rows = []
    for r in d["verified_deals"]:
        names = " ".join(s.get("name", "") if isinstance(s, dict) else str(s) for s in (r.get("suppliers") or []))
        if common(r, a) and has(names, a.supplier) and (not a.min_amount or (r.get("amount_cny") or 0) >= a.min_amount):
            rows.append(r)
    rows.sort(key=lambda r: r.get("date") or "", reverse=True)
    keep = ("date", "title", "buyer", "region", "suppliers", "amount_cny", "compute_tags", "project_id", "channel_label", "source_url")
    out({"total_matched": len(rows), "matched_amount_cny": sum(r.get("amount_cny") or 0 for r in rows),
         "matched_with_amount": sum(1 for r in rows if r.get("amount_cny")), "summary": d.get("summary"), "deals": [{k: r.get(k) for k in keep} for r in rows[:a.limit]]},
        "https://www.tandiu.cn/procurement", (d.get("updated_at") or "")[:10], base)


def cmd_deal_rate(a):
    d, base = get("/data/budget_deal_rate.json")
    out({"n_pairs": d.get("n"), "overall": d.get("overall"), "groups": d.get("groups"), "note": d.get("note"),
         "history_overall": (d.get("history_overall") or [])[-10:], "recent_pairs": (d.get("pairs") or [])[:10]},
        "https://www.tandiu.cn/deal-rate", (d.get("updated_at") or "")[:10], base)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("summary")
    for name in ("demands", "deals"):
        s = sub.add_parser(name)
        s.add_argument("--query"); s.add_argument("--buyer"); s.add_argument("--region"); s.add_argument("--since")
        s.add_argument("--limit", type=int, default=20)
        if name == "demands":
            s.add_argument("--min-budget", type=float)
        else:
            s.add_argument("--supplier"); s.add_argument("--min-amount", type=float)
    sub.add_parser("deal-rate")
    a = p.parse_args()
    {"summary": cmd_summary, "demands": cmd_demands, "deals": cmd_deals, "deal-rate": cmd_deal_rate}[a.cmd](a)


if __name__ == "__main__":
    main()
