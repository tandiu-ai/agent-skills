#!/usr/bin/env python3
"""Trigger test for TANDIU skills: run each prompt through `claude -p` in a project that has the three skills
under .claude/skills/, and record whether the expected skill fired, which fetch.py command ran, and whether the
answer cites TANDIU with a date. Usage: run_trigger_test.py <project_dir> <out.json>
"""
import json, os, re, subprocess, sys, time

CLAUDE = os.path.expanduser("~/.local/bin/claude")
CASES = [
    ("tandiu-llm-cost", "DeepSeek V4 和 GPT-5.6 的 API 价格差多少?按每百万 token 算"),
    ("tandiu-llm-cost", "What's the cheapest LLM API that scores at least 90% of the top model on the Artificial Analysis index?"),
    ("tandiu-llm-cost", "现在租一张 H200 每小时大概多少钱?买 8 卡整机呢?"),
    ("tandiu-llm-cost", "我们公司 1000 人,全员用 AI,调 API 和私有化部署哪个更省?"),
    ("tandiu-llm-cost", "Has LLM API pricing gone down over the last month? Compare US vs Chinese models."),
    ("tandiu-cn-ai-procurement", "最近有哪些政府单位在招标采购 GPU 服务器?预算多少?"),
    ("tandiu-cn-ai-procurement", "Which companies won Chinese government AI compute contracts recently?"),
    ("tandiu-cn-ai-procurement", "智算中心和算力相关的政府采购,近 30 天总预算多少?"),
    ("tandiu-cn-ai-procurement", "政府采购里算力项目的成交价一般是预算的几成?"),
    ("tandiu-cn-ai-procurement", "浪潮最近中了哪些政府 AI 项目?"),
    ("tandiu-ai-funding", "最近一个月 AI 芯片公司有哪些融资?"),
    ("tandiu-ai-funding", "Who led the latest funding round of Moonshot AI (Kimi)?"),
    ("tandiu-ai-funding", "这个月金额最大的 5 笔 AI 融资是哪些?"),
    ("tandiu-ai-funding", "具身智能/机器人赛道 10 月一共融了多少钱?"),
    ("tandiu-ai-funding", "Which US AI agent startups raised money in October 2026?"),
]


def run(prompt, cwd):
    t0 = time.time()
    p = subprocess.run([CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose",
                        "--allowedTools", "Skill", "Read", "Bash(python3:*)", "Bash(python:*)", "--max-budget-usd", "1.5"],
                       cwd=cwd, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
    skills, cmds, tools, result = [], [], [], ""
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    tools.append(c["name"])
                    inp = c.get("input") or {}
                    if c["name"] == "Skill":
                        skills.append(inp.get("skill") or inp.get("command") or json.dumps(inp))
                    if c["name"] == "Bash":
                        cmds.append(inp.get("command", "")[:200])
        if ev.get("type") == "result":
            result = ev.get("result") or ""
    return {"skills": skills, "fetch_cmds": [c for c in cmds if "fetch.py" in c], "tools": tools, "result": result,
            "seconds": round(time.time() - t0), "rc": p.returncode, "stderr": p.stderr[-300:]}


def main():
    cwd, out = sys.argv[1], sys.argv[2]
    rows = []
    for want, prompt in CASES:
        r = run(prompt, cwd)
        r.update(expected=want, prompt=prompt,
                 triggered=any(want in s for s in r["skills"]),
                 called=any(want in c for c in r["fetch_cmds"]) or bool(r["fetch_cmds"]),
                 cited=bool(re.search(r"TANDIU", r["result"])) and bool(re.search(r"20\d\d-\d\d-\d\d|更新于|updated", r["result"], re.I)))
        rows.append(r)
        print(f"{want:<26} trig={r['triggered']} call={r['called']} cite={r['cited']} {r['seconds']}s  {prompt[:40]}", flush=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
