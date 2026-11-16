"""Spaced repetition: a fixed interval ladder driven by graded attempts.

State is never stored by hand: it is recomputed from data/attempts.csv on every
build, so the CSV is the single source of truth.
"""
from __future__ import annotations

import datetime as dt

from .core import Item, is_timed

OUTCOME_RANK = {"solved": 0, "hints": 1, "failed": 2}


def suggest_grade(outcome: str, minutes: float | None, target: float | None,
                  prev_best: float | None = None) -> str:
    if outcome == "failed":
        return "again"
    if outcome == "hints":
        return "hard"
    if minutes is None or not target:
        return "good"
    if minutes > target:
        return "hard"
    if prev_best is not None and minutes > prev_best * 1.25 and minutes > 0.8 * target:
        return "hard"  # slipped noticeably against your own best
    if minutes <= 0.5 * target:
        return "easy"
    return "good"


def default_grade(row: dict) -> str:
    return row.get("grade") or ("again" if row["outcome"] == "failed" else
                                "hard" if row["outcome"] == "hints" else "good")


def is_regression(row: dict, previous: list[dict], target: float | None) -> bool:
    if not previous:
        return False
    best_outcome = min(OUTCOME_RANK.get(p["outcome"], 0) for p in previous)
    if OUTCOME_RANK.get(row["outcome"], 0) > best_outcome:
        return True
    prev_times = [p["minutes"] for p in previous if is_timed(p)]
    if is_timed(row) and prev_times:
        best = min(prev_times)
        return row["minutes"] > best * 1.25 and (target is None or row["minutes"] > target)
    return False


def schedule(item: Item, cfg: dict, legacy_slot: int | None = None) -> dict:
    ladder = cfg["intervals"]
    target = item.target(cfg)
    atts = item.attempts
    override = item.meta.get("status_override")
    summary = []
    idx, streak = None, 0
    for i, a in enumerate(atts):
        g = default_grade(a)
        regression = is_regression(a, atts[:i], target)
        within = bool(is_timed(a) and target and a["outcome"] == "solved" and a["minutes"] <= target)
        if i == 0:
            idx = 1 if g == "easy" else 0
        else:
            if g == "again":
                idx = 0
            elif g == "good":
                idx = min(idx + 1, len(ladder) - 1)
            elif g == "easy":
                idx = min(idx + 2, len(ladder) - 1)
            # hard: repeat the same interval
            streak = streak + 1 if within else 0
        entry = {"date": a["date"], "minutes": a["minutes"], "outcome": a["outcome"], "grade": g,
                 "kind": "first" if i == 0 else "review"}
        if a.get("lang"):
            entry["lang"] = a["lang"]
        if a.get("source") not in ("timer", "manual"):
            entry["source"] = a.get("source")
        if a.get("phases"):
            entry["phases"] = a["phases"]
        if regression:
            entry["regression"] = True
        summary.append(entry)

    result = {"attempts": summary, "streak": streak, "interval_days": None,
              "next_review": None, "status": "new"}
    if not item.reviewable:
        result["status"] = "logged" if atts else "new"
        return result
    if override == "mastered":
        result["status"] = "mastered"
        return result
    if not atts:
        return result

    last = dt.date.fromisoformat(atts[-1]["date"])
    mastered = streak >= cfg["mastery_streak"]
    interval = ladder[-1] if mastered else ladder[idx]
    next_review = last + dt.timedelta(days=interval)
    status = "mastered" if mastered else ("learning" if len(atts) == 1 else "reviewing")

    untimed_only = not any(is_timed(a) for a in atts)
    legacy = cfg.get("legacy", {})
    if untimed_only and legacy_slot is not None and len(atts) == 1:
        start = dt.date.fromisoformat(legacy["start"])
        next_review = start + dt.timedelta(days=legacy_slot // legacy["per_day"])
        status = "legacy"

    result.update(status=status, interval_days=interval, next_review=next_review.isoformat())
    return result


def legacy_slots(items: list[Item], cfg: dict) -> dict[str, int]:
    """Spread imported, untimed history across the review queue (N per day)."""
    legacy = cfg.get("legacy")
    if not legacy:
        return {}
    cutoff = legacy["cutoff"]
    rank = {"Hard": 0, "Medium": 1, "Easy": 2}
    pool = [it for it in items if it.reviewable and len(it.attempts) == 1
            and not is_timed(it.attempts[0]) and it.attempts[0]["date"] < cutoff
            and it.meta.get("status_override") != "mastered"]
    pool.sort(key=lambda it: (0 if "neetcode150" in (it.meta.get("lists") or []) else 1,
                              rank.get(it.difficulty, 3), it.meta.get("number", 0)))
    return {it.id: i for i, it in enumerate(pool)}


def schedule_all(items: dict[str, Item], cfg: dict) -> None:
    slots = legacy_slots(list(items.values()), cfg)
    for it in items.values():
        it.srs = schedule(it, cfg, slots.get(it.id))


def due(items: dict[str, Item], on: dt.date) -> tuple[list[Item], list[Item]]:
    today_list, overdue = [], []
    for it in items.values():
        nr = it.srs.get("next_review")
        if not nr:
            continue
        d = dt.date.fromisoformat(nr)
        if d == on:
            today_list.append(it)
        elif d < on:
            overdue.append(it)
    overdue.sort(key=lambda it: it.srs["next_review"])
    today_list.sort(key=lambda it: it.id)
    return today_list, overdue
