"""Next-7-days plan: mixes new problems with reviews, weighted by weakness, interleaved."""
from __future__ import annotations

import datetime as dt
from collections import defaultdict

from .core import PATTERN_DIRS, PATTERN_NAMES, PATTERNS, ROOT, SECTIONS, Item, read_interviews

NEW_MIN, REVIEW_MIN = 45, 25  # minutes per slot, incl. notes
# A pattern unlocks once its prerequisite has this many NeetCode problems solved.
PREREQ = {"advanced-graphs": "graphs", "2-d-dp": "1-d-dp", "tries": "trees"}
PREREQ_MIN = 3
DIFF_ORDER = {"Easy": 0, "Medium": 1, "Hard": 2}


def next_interview(today: dt.date, kind: str | None = None):
    rows = [r for r in read_interviews() if r["date"] >= today.isoformat()
            and (kind is None or r["type"] == kind)]
    return min(rows, key=lambda r: r["date"]) if rows else None


def new_ratio(cfg, today, due_lc: int, dsa_minutes: int, regressions: int) -> tuple[float, list[str]]:
    ratio, why = cfg["new_ratio"], [f"base {cfg['new_ratio']:.0%} new"]
    real = next_interview(today, "real")
    if real:
        days = (dt.date.fromisoformat(real["date"]) - today).days
        if days <= 14:
            ratio, why = 0.3, [f"interview in {days}d ({real['company']}): taper to 30% new"]
        elif days <= 28:
            ratio, why = 0.5, [f"interview in {days}d ({real['company']}): 50% new"]
    need = due_lc * REVIEW_MIN
    if need > (1 - ratio) * dsa_minutes:
        ratio = max(0.3, 1 - need / dsa_minutes)
        why.append(f"{due_lc} reviews due this week: new share cut to {ratio:.0%}")
    if regressions >= 3:
        ratio = max(0.3, ratio - 0.1)
        why.append(f"{regressions} recent regressions: -10% new")
    return ratio, why


def interleave(tasks: list[dict]) -> list[dict]:
    """Round-robin across patterns so the same pattern never runs back to back."""
    by = defaultdict(list)
    for t in tasks:
        by[t["pattern"]].append(t)
    order, out = sorted(by, key=lambda p: -len(by[p])), []
    while any(by.values()):
        for p in order:
            if by[p]:
                out.append(by[p].pop(0))
    return out


def build_plan(items: dict[str, Item], cfg: dict, weak: dict, plist: list[dict], today: dt.date) -> dict:
    hours = cfg["hours_per_week"]
    dsa_minutes = hours["dsa"] * 60
    horizon = (today + dt.timedelta(days=6)).isoformat()
    due_items = [it for it in items.values() if it.srs.get("next_review") and it.srs["next_review"] <= horizon]
    due_lc = [it for it in due_items if it.type == "lc"]
    recent = (today - dt.timedelta(days=14)).isoformat()
    regressions = sum(1 for it in items.values() for a in it.srs.get("attempts", [])
                      if a.get("regression") and a["date"] >= recent)
    ratio, why = new_ratio(cfg, today, len(due_lc), dsa_minutes, regressions)

    review_slots = max(len(due_lc), int((1 - ratio) * dsa_minutes / REVIEW_MIN))
    new_slots = max(0, int((dsa_minutes - review_slots * REVIEW_MIN) / NEW_MIN))

    # Reinforcement: spare review slots go to weak patterns' not-yet-due problems.
    reviews = sorted(due_lc, key=lambda it: it.srs["next_review"])
    spare = review_slots - len(reviews)
    if spare > 0:
        ranked = sorted((k for k, v in weak.items() if v["attempted"]), key=lambda k: -weak[k]["score"])
        due_ids = {it.id for it in reviews}
        for pat in ranked:
            cands = [it for it in items.values() if it.type == "lc" and it.meta.get("pattern") == pat
                     and it.id not in due_ids and it.srs.get("status") not in ("mastered", "new")]
            cands.sort(key=lambda it: it.srs.get("next_review") or "9999")
            for it in cands[:2]:
                if spare <= 0:
                    break
                reviews.append(it)
                spare -= 1
            if spare <= 0:
                break

    # New problems: weight unlocked patterns by weakness score.
    solved_slugs = {it.meta.get("slug") for it in items.values() if it.type == "lc" and it.attempts}
    remaining, done = defaultdict(list), defaultdict(int)
    for p in plist:
        if p["slug"] not in solved_slugs:
            remaining[p["pattern"]].append(p)
        else:
            done[p["pattern"]] += 1
    for pat in remaining:  # Easy -> Medium -> Hard, list order within a difficulty
        remaining[pat].sort(key=lambda p: DIFF_ORDER.get(p["difficulty"], 1))
    touched = [i for i, (slug, _) in enumerate(PATTERNS) if weak[slug]["attempted"]]
    frontier = (max(touched) if touched else 0) + 2
    weights = {}
    for i, (slug, _) in enumerate(PATTERNS):
        locked = slug in PREREQ and done[PREREQ[slug]] < PREREQ_MIN
        if remaining[slug] and i <= max(frontier, 5) and not locked:
            weights[slug] = weak[slug]["score"] + 0.05
    alloc = defaultdict(int)
    for _ in range(new_slots):
        if not weights:
            break
        # give the next slot to the pattern with the highest weight per slot already given
        slug = max(weights, key=lambda s: weights[s] / (1 + alloc[s]))
        if alloc[slug] >= min(4, len(remaining[slug])):
            weights.pop(slug)
            continue
        alloc[slug] += 1
    new_tasks = []
    for slug, n in alloc.items():
        for p in remaining[slug][:n]:
            new_tasks.append({"kind": "new", "pattern": slug, "label": f"{p['number']}. {p['title']}",
                              "difficulty": p["difficulty"], "cmd": f"prep new lc {p['number']}"})
    review_tasks = [{"kind": "review", "pattern": it.meta.get("pattern"), "label": it.label(),
                     "difficulty": it.difficulty, "item": it, "cmd": f"prep start lc {it.meta.get('number')}",
                     "due": it.srs.get("next_review")} for it in reviews]

    days = [today + dt.timedelta(days=i) for i in range(7)]
    schedule = {d: {"new": [], "review": [], "other": []} for d in days}
    # due-dated reviews go on (or before) their date; the rest are spread evenly
    for t in review_tasks:
        d = max(today, dt.date.fromisoformat(t["due"])) if t["due"] and t["due"] <= horizon else None
        if d is None:
            d = min(days, key=lambda x: len(schedule[x]["review"]))
        schedule[d]["review"].append(t)
    for i, t in enumerate(interleave(new_tasks)):
        schedule[days[i % 7]]["new"].append(t)

    other = [it for it in due_items if it.type != "lc"]
    for i, it in enumerate(sorted(other, key=lambda it: it.srs["next_review"])):
        d = max(today, dt.date.fromisoformat(it.srs["next_review"]))
        schedule[d]["other"].append(f"Review: {it.title} ({it.type})")
    fixed = [
        (0, "System design: 45-min timed design (`prep start sd <name>`)"),
        (1, "CS fundamentals: 1 note + flashcards"),
        (2, "Online assessment: 1 timed set (`prep start oa <id>`)"),
        (3, "Behavioral: draft or rehearse 1 STAR story"),
        (4, "System design: 1 concept deep-dive"),
        (5, "Mock interview (Pramp / interviewing.io / friend)"),
        (6, "CS fundamentals: review + weekly retro (`prep build`)"),
    ]
    for offset, text in fixed:
        schedule[days[offset]]["other"].append(text)
    return {"ratio": ratio, "why": why, "review_slots": review_slots, "new_slots": new_slots,
            "alloc": dict(alloc), "schedule": schedule, "days": days, "reviews": review_tasks,
            "new": new_tasks}


def render_plan(plan: dict, items: dict[str, Item], weak: dict, today: dt.date) -> str:
    base = ROOT / SECTIONS["plan"]
    lines = [
        f"## Next 7 days: {plan['days'][0].strftime('%a %b %d')} to {plan['days'][-1].strftime('%a %b %d, %Y')}",
        "",
        f"**Mix:** {plan['ratio']:.0%} new / {1 - plan['ratio']:.0%} review "
        f"({plan['new_slots']} new slots x {NEW_MIN}m, {plan['review_slots']} review slots x {REVIEW_MIN}m).  ",
        "**Why:** " + "; ".join(plan["why"]) + ".",
        "",
    ]
    if plan["alloc"]:
        lines += ["| Pattern | New this week | Weakness | Signal |", "|---|---:|---:|---|"]
        for slug, n in sorted(plan["alloc"].items(), key=lambda kv: -weak[kv[0]]["score"]):
            w = weak[slug]
            link = f"[{PATTERN_NAMES[slug]}](../{SECTIONS['lc']}/{PATTERN_DIRS[slug]}/README.md)"
            sig = ", ".join(w["reasons"]) or ("not started" if not w["attempted"] else "steady")
            lines.append(f"| {link} | {n} | {w['score']:.2f} | {sig} |")
        lines.append("")
    lines += ["| Day | New problems | Reviews | Other |", "|---|---|---|---|"]
    for d in plan["days"]:
        s = plan["schedule"][d]
        new = "<br>".join(f"{t['label']} <sub>{t['difficulty'][0]}</sub>" for t in s["new"]) or "-"
        rev = []
        for t in s["review"]:
            it = t["item"]
            link = f"[{t['label']}](../{it.path.relative_to(ROOT).as_posix()})"
            rev.append(link + (" (overdue)" if t["due"] and t["due"] < today.isoformat() else ""))
        lines.append(f"| {d.strftime('%a %d')} | {new} | {'<br>'.join(rev) or '-'} | {'<br>'.join(s['other'])} |")
    lines += ["", "Patterns are interleaved (no two problems of the same pattern back to back) "
                  "because mixed practice transfers better than doing one pattern in a block."]
    return "\n".join(lines)
