"""Speed metrics, weekly trends and the per-pattern weakness score."""
from __future__ import annotations

import datetime as dt
import statistics as st
from collections import defaultdict

from .core import PATTERNS, Item, is_timed
from .srs import is_regression

DIFFS = ("Easy", "Medium", "Hard")


def week_start(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def timed_rows(items: dict[str, Item], cfg: dict, type_: str = "lc"):
    """Yield (item, attempt, index, ratio) for timed attempts."""
    for it in items.values():
        if it.type != type_:
            continue
        target = it.target(cfg)
        for i, a in enumerate(it.attempts):
            if is_timed(a):
                yield it, a, i, (a["minutes"] / target if target else None)


def _avg(xs):
    return sum(xs) / len(xs) if xs else None


def _med(xs):
    return st.median(xs) if xs else None


def speed_table(items, cfg, key):
    """Group timed LC attempts by key(item) -> stats dict."""
    groups = defaultdict(list)
    for it, a, i, ratio in timed_rows(items, cfg):
        groups[key(it)].append((it, a, i, ratio))
    out = {}
    for k, rows in groups.items():
        mins = [a["minutes"] for _, a, _, _ in rows]
        first = [a["minutes"] for _, a, i, _ in rows if i == 0]
        review = [a["minutes"] for _, a, i, _ in rows if i > 0]
        within = [1 for it, a, _, _ in rows if a["outcome"] == "solved" and a["minutes"] <= it.target(cfg)]
        out[k] = {
            "n": len(rows), "avg": _avg(mins), "median": _med(mins),
            "within": len(within) / len(rows),
            "first_avg": _avg(first), "review_avg": _avg(review),
            "ratio_med": _med([r for *_, r in rows if r is not None]),
        }
    return out


def overall(items, cfg):
    rows = list(timed_rows(items, cfg))
    if not rows:
        return None
    within = [1 for it, a, _, _ in rows if a["outcome"] == "solved" and a["minutes"] <= it.target(cfg)]
    return {"n": len(rows), "within": len(within) / len(rows),
            "avg_ratio": _avg([r for *_, r in rows]),
            "avg": _avg([a["minutes"] for _, a, _, _ in rows])}


def weekly(items, cfg, today: dt.date, weeks: int = 8):
    """Per-week stats for the last `weeks` weeks (oldest first)."""
    start = week_start(today) - dt.timedelta(weeks=weeks - 1)
    buckets = [start + dt.timedelta(weeks=i) for i in range(weeks)]
    data = {w: {"ratios": defaultdict(list), "mins": defaultdict(list), "within": [],
                "new": defaultdict(int), "reviews": 0} for w in buckets}
    for it in items.values():
        if it.type != "lc":
            continue
        target = it.target(cfg)
        for i, a in enumerate(it.attempts):
            w = week_start(dt.date.fromisoformat(a["date"]))
            if w not in data:
                continue
            if i == 0 and a["outcome"] != "failed":
                data[w]["new"][it.difficulty] += 1
            elif i > 0:
                data[w]["reviews"] += 1
            if is_timed(a):
                data[w]["ratios"][it.difficulty].append(a["minutes"] / target)
                data[w]["mins"][it.difficulty].append(a["minutes"])
                data[w]["within"].append(a["outcome"] == "solved" and a["minutes"] <= target)
    out = []
    for w in buckets:
        d = data[w]
        all_r = [r for rs in d["ratios"].values() for r in rs]
        all_m = [m for ms in d["mins"].values() for m in ms]
        out.append({
            "week": w,
            "ratio": {k: _med(v) for k, v in d["ratios"].items()},
            "ratio_all": _med(all_r),
            "avg_min": _avg(all_m),
            "within": (sum(d["within"]) / len(d["within"])) if d["within"] else None,
            "timed": len(all_m),
            "new": dict(d["new"]),
            "reviews": d["reviews"],
        })
    return out


def pattern_progress(items, plist):
    """Solved counts per pattern, against the problem list."""
    total = defaultdict(int)
    for p in plist:
        total[p["pattern"]] += 1
    solved, solved_list = defaultdict(int), defaultdict(int)
    list_slugs = {p["slug"] for p in plist}
    for it in items.values():
        if it.type != "lc" or not any(a["outcome"] == "solved" for a in it.attempts):
            continue
        pat = it.meta.get("pattern")
        solved[pat] += 1
        if it.meta.get("slug") in list_slugs:
            solved_list[pat] += 1
    return {slug: {"total": total[slug], "solved": solved[slug], "solved_list": solved_list[slug]}
            for slug, _ in PATTERNS}


def weakness(items, cfg, plist, today: dt.date, window_days: int = 42):
    """Score 0..1 per pattern; higher = needs more attention.

    Components (weights in brackets):
      fail   [0.30]  failed = 1, needed hints = 0.5, over the recent window
      slow   [0.25]  median time / target, mapped 0.7x -> 0, 1.5x -> 1
      regress[0.25]  share of reviews that were slower/worse than earlier attempts
      stale  [0.10]  days since last practice / 21
      gap    [0.10]  unsolved share of the pattern in the problem list
    """
    prog = pattern_progress(items, plist)
    cutoff = (today - dt.timedelta(days=window_days)).isoformat()
    per = defaultdict(lambda: {"fails": [], "ratios": [], "regress": [], "last": None})
    for it in items.values():
        if it.type != "lc":
            continue
        p = per[it.meta.get("pattern")]
        target = it.target(cfg)
        for i, a in enumerate(it.attempts):
            p["last"] = max(p["last"] or a["date"], a["date"])
            if a["date"] < cutoff:
                continue
            p["fails"].append({"failed": 1, "hints": 0.5}.get(a["outcome"], 0))
            if is_timed(a):
                p["ratios"].append(a["minutes"] / target)
            if i > 0:
                p["regress"].append(1 if is_regression(a, it.attempts[:i], target) else 0)
    out = {}
    for slug, name in PATTERNS:
        p = per.get(slug, {"fails": [], "ratios": [], "regress": [], "last": None})
        fail = _avg(p["fails"]) or 0
        ratio = _med(p["ratios"])
        slow = min(max(((ratio or 0) - 0.7) / 0.8, 0), 1) if ratio else 0
        regress = _avg(p["regress"]) or 0
        days = (today - dt.date.fromisoformat(p["last"])).days if p["last"] else 99
        stale = min(days / 21, 1)
        pr = prog[slug]
        gap = 1 - pr["solved_list"] / pr["total"] if pr["total"] else 0
        score = 0.30 * fail + 0.25 * slow + 0.25 * regress + 0.10 * stale + 0.10 * gap
        reasons = []
        if fail >= 0.3:
            reasons.append(f"{fail:.0%} fail/hint rate")
        if ratio and ratio > 1:
            reasons.append(f"median {ratio:.1f}x target")
        if regress >= 0.3:
            reasons.append(f"{regress:.0%} of reviews regressed")
        if days >= 21 and p["last"]:
            reasons.append(f"untouched {days}d")
        out[slug] = {"name": name, "score": score, "ratio": ratio, "fail": fail, "regress": regress,
                     "days": days, "attempted": bool(p["ratios"] or p["fails"]),
                     "reasons": reasons, "n_timed": len(p["ratios"])}
    return out


def weakest(weak: dict, n: int = 3):
    tried = [(k, v) for k, v in weak.items() if v["attempted"]]
    return sorted(tried, key=lambda kv: -kv[1]["score"])[:n]


def slowest(items, cfg, n: int = 3, min_attempts: int = 2):
    table = speed_table(items, cfg, key=lambda it: it.meta.get("pattern"))
    rows = [(k, v) for k, v in table.items() if v["n"] >= min_attempts and v["ratio_med"]]
    return sorted(rows, key=lambda kv: -kv[1]["ratio_med"])[:n]


def sd_phase_stats(items, cfg):
    phases = [p for p, _ in cfg["sd_phases"]]
    acc = defaultdict(list)
    n = 0
    from .core import parse_phases
    for it in items.values():
        if it.type != "sd":
            continue
        for a in it.attempts:
            ph = parse_phases(a.get("phases", ""))
            if ph:
                n += 1
                for p in phases:
                    if p in ph:
                        acc[p].append(ph[p])
    return n, {p: _avg(acc[p]) for p in phases}
