"""`prep build`: refresh entry frontmatter, folder indexes, charts and the root dashboard."""
from __future__ import annotations

import datetime as dt
import json
from collections import Counter, defaultdict
from pathlib import Path

from . import charts, metrics
from .core import (DATA, FUND_AREAS, OA_PLATFORMS, PATTERN_DIRS, PATTERN_NAMES, PATTERNS, ROOT,
                   SECTIONS, Item, fmt_min, is_timed, load_config, load_items, load_problem_list,
                   md_link, parse_phases, read_frontmatter, read_interviews, rel, replace_block,
                   write_entry, write_text, today as get_today)
from .plan import build_plan, next_interview, render_plan
from .srs import due, schedule_all

PATTERN_HINTS = {
    "arrays-hashing": "Count, group or look up in O(1). Signals: *duplicates, anagram, frequency, seen before*.",
    "two-pointers": "Sorted input or symmetric checks; move pointers inward/outward. Signals: *pair sum, palindrome, in-place*.",
    "sliding-window": "Contiguous subarray/substring with a constraint; grow right, shrink left. Signals: *longest/shortest substring, at most k*.",
    "stack": "Nested or 'next greater' structure; monotonic stack for spans. Signals: *parentheses, next warmer, histogram*.",
    "binary-search": "Monotonic predicate over an index or answer space. Signals: *sorted, rotated, minimum speed/capacity*.",
    "linked-list": "Pointer rewiring, fast/slow pointers, dummy heads. Signals: *cycle, middle, reverse, merge*.",
    "trees": "Recursive DFS returning info upward, or BFS by level. Signals: *depth, path, ancestor, level order, BST*.",
    "tries": "Prefix lookups over many words. Signals: *prefix, autocomplete, word search on board*.",
    "heap-priority-queue": "Repeatedly take the min/max; top-k; two heaps for medians. Signals: *k-th, closest, stream*.",
    "backtracking": "Build candidates incrementally and undo. Signals: *all subsets/permutations/combinations, board search*.",
    "graphs": "BFS/DFS over grids or adjacency lists, topological sort, union-find. Signals: *islands, prerequisites, connected*.",
    "advanced-graphs": "Weighted shortest paths (Dijkstra/Bellman-Ford), MST (Prim/Kruskal), Eulerian paths.",
    "1-d-dp": "State depends on a few previous states. Signals: *ways to, min cost, max profit, can you reach*.",
    "2-d-dp": "Two indices (two strings, grid, item x capacity). Signals: *edit distance, LCS, knapsack, paths in grid*.",
    "greedy": "A locally best choice is provably safe. Signals: *max subarray, jump, intervals sorted by end*.",
    "intervals": "Sort by start (or end), then merge/sweep. Signals: *overlap, meeting rooms, insert interval*.",
    "math-geometry": "Matrix manipulation, number tricks, overflow care. Signals: *rotate, spiral, power, digits*.",
    "bit-manipulation": "XOR cancels, masks, shifts. Signals: *single number, count bits, without + operator*.",
}
STATUS_LABEL = {"new": "new", "learning": "learning", "reviewing": "reviewing", "mastered": "**mastered**",
                "legacy": "legacy (untimed)", "logged": "logged"}
OUTCOME_LABEL = {"solved": "solved", "hints": "needed hints", "failed": "failed"}


def nav(base: Path, extra: list[tuple[str, Path]] = ()) -> str:
    links = [md_link("Home", ROOT / "README.md", base)]
    links += [md_link(t, p, base) for t, p in extra]
    return " · ".join(links)


def best(it: Item):
    times = [a["minutes"] for a in it.attempts if is_timed(a)]
    return min(times) if times else None


def last_attempt(it: Item):
    return it.attempts[-1] if it.attempts else None


# ---------------------------------------------------------------- entries

def attempts_table(it: Item, cfg: dict) -> str:
    target = it.target(cfg)
    s = it.srs
    if not it.attempts:
        return "_No attempts yet. Start one with_ `prep start " + start_args(it) + "`."
    extra = {"lc": "Lang", "sd": "Phases (min)"}.get(it.type)
    cols = ["#", "Date", "Kind", "Time", "Target", "Outcome", "Grade"] + ([extra] if extra else [])
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for i, a in enumerate(s["attempts"], 1):
        flag = " (slower)" if a.get("regression") else ""
        src = f" <sub>{a['source']}</sub>" if a.get("source") else ""
        within = ""
        if a["minutes"] is not None and target:
            within = " (in time)" if a["minutes"] <= target else " (over)"
        row = [str(i), a["date"], a["kind"], fmt_min(a["minutes"]) + within + src, fmt_min(target),
               OUTCOME_LABEL[a["outcome"]] + flag, a["grade"]]
        if it.type == "lc":
            row.append(a.get("lang", "-"))
        elif it.type == "sd":
            ph = parse_phases(a.get("phases", ""))
            row.append(", ".join(f"{k} {v:.0f}" for k, v in ph.items()) or "-")
        lines.append("| " + " | ".join(row) + " |")
    tail = f"\n**Status:** {STATUS_LABEL.get(s['status'], s['status'])}"
    if s.get("next_review"):
        tail += f" · **Next review:** {s['next_review']}"
        if s.get("interval_days"):
            tail += f" (interval {s['interval_days']}d)"
    if it.reviewable:
        tail += f" · **In-target streak:** {s['streak']}/{cfg['mastery_streak']}"
    return "\n".join(lines) + "\n" + tail


LANG_NAMES = {"python": ("Python", "python"), "java": ("Java", "java"), "cpp": ("C++", "cpp")}


def solutions_block(it: Item, cfg: dict) -> str:
    """Collapsible code blocks, one per language file that sits next to the note."""
    parts = []
    for lang, ext in cfg["langs"].items():
        f = it.path.with_suffix(ext)
        if not f.exists():
            continue
        name, fence = LANG_NAMES[lang]
        code = f.read_text(encoding="utf-8").rstrip()
        parts.append(f"<details>\n<summary><b>{name}</b> (spoiler) · <code>{f.name}</code></summary>\n\n"
                     f"```{fence}\n{code}\n```\n\n</details>")
    if not parts:
        return f"_No solution file yet: `prep new lc {it.meta.get('number')} --lang python`._"
    return "\n\n".join(parts)


def start_args(it: Item) -> str:
    if it.type == "lc":
        return f"lc {it.meta.get('number')}"
    return it.id


def update_entry(it: Item, cfg: dict) -> bool:
    meta = dict(it.meta)
    for k in ("status", "next_review", "interval_days", "streak", "attempts"):
        meta.pop(k, None)
    s = it.srs
    if it.type == "mock":
        return write_entry(it.path, meta, it.body)
    meta["status"] = s["status"]
    if it.reviewable:
        meta["next_review"] = s["next_review"]
        meta["interval_days"] = s["interval_days"]
        meta["streak"] = s["streak"]
    meta["attempts"] = [{k: v for k, v in a.items() if v is not None} for a in s["attempts"]]
    body = replace_block(it.body, "attempts", attempts_table(it, cfg))
    if it.type == "lc":
        body = replace_block(body, "solutions", solutions_block(it, cfg))
    return write_entry(it.path, meta, body)


# ---------------------------------------------------------------- generic index tables

def lc_rows(items: list[Item], base: Path, cfg: dict) -> list[str]:
    rows = ["| # | Problem | Diff | Status | Tries | Best | Target | Next review | Key insight |",
            "|---:|---|---|---|---:|---:|---:|---|---|"]
    for it in sorted(items, key=lambda it: it.meta.get("number", 0)):
        langs = ", ".join(it.meta.get("langs") or [])
        sample = " <sub>sample</sub>" if it.meta.get("sample") else ""
        rows.append(f"| {it.meta.get('number')} | {md_link(it.title, it.path, base)}{sample}"
                    f"<br><sub>{langs}</sub> | {it.difficulty} | {STATUS_LABEL.get(it.srs['status'])} | "
                    f"{len(it.attempts)} | {fmt_min(best(it))} | {fmt_min(it.target(cfg))} | "
                    f"{it.srs.get('next_review') or '-'} | {it.meta.get('key_insight') or ''} |")
    return rows


def generic_rows(items: list[Item], base: Path, cfg: dict, cols: str = "default") -> list[str]:
    if cols == "oa":
        rows = ["| Date | Assessment | Limit | Time used | Score | Outcome |", "|---|---|---:|---:|---|---|"]
        for it in sorted(items, key=lambda it: it.meta.get("date", ""), reverse=True):
            la = last_attempt(it)
            rows.append(f"| {it.meta.get('date', '')} | {md_link(it.title, it.path, base)} | "
                        f"{fmt_min(it.target(cfg))} | {fmt_min(la['minutes']) if la else '-'} | "
                        f"{it.meta.get('score', '-')} | {OUTCOME_LABEL.get(la['outcome'], '-') if la else '-'} |")
        return rows
    if cols == "mock":
        rows = ["| Date | Mock | Type | Interviewer | Result | Open action items |", "|---|---|---|---|---|---:|"]
        for it in sorted(items, key=lambda it: it.meta.get("date", ""), reverse=True):
            open_items = it.body.count("- [ ]")
            rows.append(f"| {it.meta.get('date', '')} | {md_link(it.title, it.path, base)} | "
                        f"{it.meta.get('format', '')} | {it.meta.get('interviewer', '')} | "
                        f"{it.meta.get('result', '')} | {open_items} |")
        return rows
    if cols == "star":
        rows = ["| Story | Themes | Status | Tries | Best | Next review |", "|---|---|---|---:|---:|---|"]
    else:
        rows = ["| Entry | Tags | Status | Tries | Best | Next review |", "|---|---|---|---:|---:|---|"]
    for it in sorted(items, key=lambda it: it.title):
        tag_col = ", ".join(it.meta.get("themes") or []) if cols == "star" else ", ".join(it.tags[:4])
        sample = " <sub>sample</sub>" if it.meta.get("sample") else ""
        rows.append(f"| {md_link(it.title, it.path, base)}{sample} | {tag_col} | "
                    f"{STATUS_LABEL.get(it.srs['status'])} | {len(it.attempts)} | {fmt_min(best(it))} | "
                    f"{it.srs.get('next_review') or '-'} |")
    return rows


def in_dir(items: dict[str, Item], folder: Path) -> list[Item]:
    folder = folder.resolve()
    return [it for it in items.values() if folder in it.path.resolve().parents]


def empty_note(rows: list[str], what: str, cmd: str) -> str:
    if len(rows) > 2:
        return "\n".join(rows)
    return f"_No {what} yet. Create one with_ `{cmd}`."


def update_block_file(path: Path, name: str, content: str) -> bool:
    text = path.read_text(encoding="utf-8")
    return write_text(path, replace_block(text, name, content))


# ---------------------------------------------------------------- sections

def build_patterns(items, cfg, plist, weak):
    changed = 0
    lc_root = ROOT / SECTIONS["lc"]
    by_pattern = defaultdict(list)
    for it in items.values():
        if it.type == "lc":
            by_pattern[it.meta.get("pattern")].append(it)
    plist_by = defaultdict(list)
    for p in plist:
        plist_by[p["pattern"]].append(p)
    solved_slugs = {it.meta.get("slug") for it in items.values() if it.type == "lc" and it.attempts}
    for i, (slug, name) in enumerate(PATTERNS):
        folder = lc_root / PATTERN_DIRS[slug]
        prev_link = next_link = ""
        if i > 0:
            ps = PATTERNS[i - 1][0]
            prev_link = md_link("< " + PATTERN_NAMES[ps], lc_root / PATTERN_DIRS[ps] / "README.md", folder)
        if i < len(PATTERNS) - 1:
            ns = PATTERNS[i + 1][0]
            next_link = md_link(PATTERN_NAMES[ns] + " >", lc_root / PATTERN_DIRS[ns] / "README.md", folder)
        mine = by_pattern.get(slug, [])
        list_total = len(plist_by[slug])
        list_done = sum(1 for p in plist_by[slug] if p["slug"] in solved_slugs)
        w = weak[slug]
        lines = [
            f"# {name}",
            "",
            nav(folder, [("DSA", lc_root / "README.md"), ("Study plan", ROOT / SECTIONS["plan"] / "README.md")])
            + (f" · {prev_link}" if prev_link else "") + (f" · {next_link}" if next_link else ""),
            "",
            f"> {PATTERN_HINTS[slug]}",
            "",
            f"**NeetCode 150:** {list_done}/{list_total} · **Entries here:** {len(mine)} · "
            f"**Weakness score:** {w['score']:.2f}" + (f" ({', '.join(w['reasons'])})" if w["reasons"] else ""),
            "",
            "## Problems",
            "",
        ]
        rows = lc_rows(mine, folder, cfg)
        lines.append(empty_note(rows, "problems in this pattern", "prep new lc <number>"))
        todo = [p for p in plist_by[slug] if p["slug"] not in solved_slugs]
        if todo:
            lines += ["", "<details>", f"<summary>NeetCode 150 still to do ({len(todo)})</summary>", "",
                      "| # | Problem | Diff | Start with |", "|---:|---|---|---|"]
            for p in todo:
                prem = " (premium)" if p.get("premium") == "1" else ""
                lines.append(f"| {p['number']} | [{p['title']}](https://leetcode.com/problems/{p['slug']}/){prem} | "
                             f"{p['difficulty']} | `prep new lc {p['number']}` |")
            lines += ["", "</details>"]
        lines += ["", "<sub>Generated by `prep build`. Do not edit by hand.</sub>", ""]
        changed += write_text(folder / "README.md", "\n".join(lines))
    # section index
    prog = metrics.pattern_progress(items, plist)
    speed = metrics.speed_table(items, cfg, key=lambda it: it.meta.get("pattern"))
    rows = ["| # | Pattern | Entries | NeetCode 150 | Median time | Within target | Weakness |",
            "|---:|---|---:|---|---:|---:|---:|"]
    for i, (slug, name) in enumerate(PATTERNS, 1):
        p, s, w = prog[slug], speed.get(slug), weak[slug]
        bar = progress_bar(p["solved_list"], p["total"])
        rows.append(f"| {i:02d} | {md_link(name, lc_root / PATTERN_DIRS[slug] / 'README.md', lc_root)} | "
                    f"{p['solved']} | {bar} {p['solved_list']}/{p['total']} | "
                    f"{fmt_min(s['median']) if s else '-'} | {f'{s['within']:.0%}' if s else '-'} | "
                    f"{w['score']:.2f} |")
    changed += update_block_file(lc_root / "README.md", "index", "\n".join(rows))
    return changed


def progress_bar(done: int, total: int, width: int = 10) -> str:
    if not total:
        return ""
    filled = round(width * done / total)
    return "`" + "#" * filled + "." * (width - filled) + "`"


def build_sections(items, cfg):
    changed = 0
    sd = ROOT / SECTIONS["sd"]
    for sub, what, cmd in (("concepts", "concept notes", "prep new concept <name>"),
                           ("questions", "design questions", "prep new sd <name>"),
                           ("ood", "object-oriented designs", "prep new ood <name>")):
        folder = sd / sub
        rows = generic_rows(in_dir(items, folder), folder, cfg)
        changed += update_block_file(folder / "README.md", "index", empty_note(rows, what, cmd))
    n, phases = metrics.sd_phase_stats(items, cfg)
    rows = ["| Section | Entries | Due now |", "|---|---:|---:|"]
    t = get_today().isoformat()
    for sub, label in (("concepts", "Concepts"), ("questions", "Design questions"), ("ood", "Object-oriented design")):
        its = in_dir(items, sd / sub)
        d = sum(1 for it in its if it.srs.get("next_review") and it.srs["next_review"] <= t)
        rows.append(f"| {md_link(label, sd / sub / 'README.md', sd)} | {len(its)} | {d} |")
    rows += ["", phase_table(cfg, n, phases)]
    changed += update_block_file(sd / "README.md", "index", "\n".join(rows))

    oa = ROOT / SECTIONS["oa"]
    for plat in OA_PLATFORMS:
        folder = oa / plat
        rows = generic_rows(in_dir(items, folder), folder, cfg, "oa")
        changed += update_block_file(folder / "README.md", "index",
                                     empty_note(rows, "attempts on this platform", f"prep new oa {plat} <name>"))
    rows = generic_rows(in_dir(items, oa), oa, cfg, "oa")
    plat_rows = ["| Platform | Attempts |", "|---|---:|"] + [
        f"| {md_link(name, oa / p / 'README.md', oa)} | {len(in_dir(items, oa / p))} |" for p, name in OA_PLATFORMS.items()]
    changed += update_block_file(oa / "README.md", "index", "\n".join(plat_rows) + "\n\n### All attempts\n\n"
                                 + empty_note(rows, "OA attempts", "prep new oa <platform> <name>"))

    beh = ROOT / SECTIONS["star"]
    stories = in_dir(items, beh / "stories")
    rows = generic_rows(stories, beh, cfg, "star")
    themes = json.loads((DATA / "behavioral-themes.json").read_text(encoding="utf-8"))
    cover = ["| Theme | Common questions | Stories |", "|---|---|---|"]
    for th in themes:
        linked = [md_link(s.title, s.path, beh) for s in stories if th["slug"] in (s.meta.get("themes") or [])]
        cover.append(f"| **{th['name']}** | {'<br>'.join(th['questions'][:2])} | "
                     f"{', '.join(linked) or '**gap**: write one'} |")
    changed += update_block_file(beh / "README.md", "index",
                                 empty_note(rows, "stories", "prep new star <slug> \"Title\"")
                                 + "\n\n### Theme coverage\n\n" + "\n".join(cover))

    fund = ROOT / SECTIONS["fund"]
    area_rows = ["| Area | Notes | Due now |", "|---|---:|---:|"]
    for area, name in FUND_AREAS.items():
        folder = fund / area
        its = in_dir(items, folder)
        d = sum(1 for it in its if it.srs.get("next_review") and it.srs["next_review"] <= t)
        extra = sorted(p for p in folder.glob("*.md") if p.name != "README.md" and not read_frontmatter(p)[0].get("id"))
        rows = generic_rows(its, folder, cfg)
        content = empty_note(rows, "notes", f"prep new note {area} <name>")
        if extra:
            content += "\n\n**Reference sheets:** " + " · ".join(md_link(p.stem, p, folder) for p in extra)
        changed += update_block_file(folder / "README.md", "index", content)
        area_rows.append(f"| {md_link(name, folder / 'README.md', fund)} | {len(its) + len(extra)} | {d} |")
    changed += update_block_file(fund / "README.md", "index", "\n".join(area_rows))

    mock = ROOT / SECTIONS["mock"]
    mocks = in_dir(items, mock)
    rows = generic_rows(mocks, mock, cfg, "mock")
    upcoming = [r for r in read_interviews() if r["date"] >= t]
    up = ["| Date | What | Type | Notes |", "|---|---|---|---|"] + [
        f"| {r['date']} | {r['company']} | {r['type']} | {r.get('notes', '')} |" for r in sorted(upcoming, key=lambda r: r["date"])]
    actions = []
    for m in sorted(mocks, key=lambda it: it.meta.get("date", ""), reverse=True):
        for line in m.body.splitlines():
            if line.strip().startswith("- [ ]"):
                actions.append(f"{line.strip()} <sub>({md_link(m.meta.get('date', ''), m.path, mock)})</sub>")
    content = "### Upcoming\n\n" + ("\n".join(up) if len(up) > 2 else "_Nothing scheduled. Add with_ `prep interview add <date> \"<what>\" --type mock`.")
    content += "\n\n### Log\n\n" + empty_note(rows, "mocks", "prep new mock <platform> <format>")
    content += "\n\n### Open action items\n\n" + ("\n".join(actions) if actions else "_None._")
    changed += update_block_file(mock / "README.md", "index", content)
    return changed


def phase_table(cfg, n, phases) -> str:
    if not n:
        return "_No timed designs yet._"
    rows = [f"**Phase timing** (avg of {n} timed design{'s' if n != 1 else ''})", "",
            "| Phase | Target | Avg | Delta |", "|---|---:|---:|---:|"]
    for p, tgt in cfg["sd_phases"]:
        v = phases.get(p)
        rows.append(f"| {p} | {tgt}m | {fmt_min(v)} | {f'{v - tgt:+.1f}m' if v is not None else '-'} |")
    return "\n".join(rows)


# ---------------------------------------------------------------- root dashboard

def due_table(items_list: list[Item], base: Path, today: dt.date, limit: int = 8) -> str:
    if not items_list:
        return "_Nothing._"
    rows = ["| Item | Type | Due | Last result |", "|---|---|---|---|"]
    for it in items_list[:limit]:
        la = last_attempt(it)
        last = f"{OUTCOME_LABEL[la['outcome']]}, {fmt_min(la['minutes'])}" if la else "-"
        days = (today - dt.date.fromisoformat(it.srs["next_review"])).days
        when = "today" if days == 0 else f"{days}d late"
        rows.append(f"| {md_link(it.label(), it.path, base)} | {it.type} | {when} | {last} |")
    if len(items_list) > limit:
        rows.append(f"| _+{len(items_list) - limit} more:_ `prep due` | | | |")
    return "\n".join(rows)


def badge(label: str, value: str, color: str) -> str:
    enc = lambda s: s.replace("%", "%25").replace("-", "--").replace("_", "__").replace(" ", "_").replace("/", "%2F")
    return f"![{label}](https://img.shields.io/badge/{enc(label)}-{enc(value)}-{color}?style=flat-square)"


def build_dashboard(items, cfg, plist, weak, today) -> str:
    base = ROOT
    lc = [it for it in items.values() if it.type == "lc"]
    solved = [it for it in lc if any(a["outcome"] == "solved" for a in it.attempts)]
    by_diff = Counter(it.difficulty for it in solved)
    list_slugs = {p["slug"] for p in plist}
    nc = sum(1 for it in solved if it.meta.get("slug") in list_slugs)
    due_today, overdue = due(items, today)
    ov = metrics.overall(items, cfg)
    speed = metrics.speed_table(items, cfg, key=lambda it: it.difficulty)
    nxt_mock = next_interview(today, "mock")
    nxt_real = next_interview(today, "real")
    mastered = sum(1 for it in items.values() if it.srs.get("status") == "mastered")

    out = []
    out.append(" ".join([
        badge("solved", str(len(solved)), "2a78d6"),
        badge("NeetCode 150", f"{nc}/150", "6250d6"),
        badge("due today", str(len(due_today) + len(overdue)), "eb6834" if overdue else "1baf7a"),
        badge("within target", f"{ov['within']:.0%}" if ov else "n/a", "1baf7a"),
        badge("updated", today.isoformat(), "52514e"),
    ]))
    out.append("")
    mock_txt = f"{nxt_mock['date']}: {nxt_mock['company']}" if nxt_mock else "none scheduled"
    real_txt = f"{nxt_real['date']}: {nxt_real['company']}" if nxt_real else "none yet"
    avg_txt = f"{ov['avg_ratio']:.2f}x target ({ov['n']} timed)" if ov else "no timed attempts"
    out += [
        "| Solved | Easy / Med / Hard | NeetCode 150 | Due today | Overdue | Avg time vs target | Next mock | Next interview |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
        f"| **{len(solved)}** | {by_diff['Easy']} / {by_diff['Medium']} / {by_diff['Hard']} | "
        f"{progress_bar(nc, 150)} {nc} | **{len(due_today)}** | {len(overdue)} | {avg_txt} | {mock_txt} | {real_txt} |",
        "",
    ]
    # weak areas
    wk = metrics.weakest(weak)
    sl = metrics.slowest(items, cfg)
    out += ["### Focus next", ""]
    if wk:
        for slug, w in wk:
            link = md_link(w["name"], ROOT / SECTIONS["lc"] / PATTERN_DIRS[slug] / "README.md", base)
            out.append(f"1. **{link}** (score {w['score']:.2f}): {', '.join(w['reasons']) or 'low coverage / stale'}")
    else:
        out.append("_Log a few attempts to see weak areas._")
    if sl:
        out.append("")
        out.append("**Slowest patterns (median time / target):** " + " · ".join(
            f"{PATTERN_NAMES.get(k, k)} {v['ratio_med']:.2f}x" for k, v in sl))
    out.append("")
    # due
    out += [f"### Due today ({len(due_today)})", "", due_table(due_today, base, today), "",
            f"### Overdue ({len(overdue)})", "", due_table(overdue, base, today), ""]
    # speed
    out += ["### Speed", "",
            "| Difficulty | Target | Attempts | Average | Median | Within target | First try avg | Review avg |",
            "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for d in metrics.DIFFS:
        s = speed.get(d)
        tgt = cfg["targets"][d]
        if s:
            out.append(f"| {d} | {tgt}m | {s['n']} | {fmt_min(s['avg'])} | {fmt_min(s['median'])} | "
                       f"{s['within']:.0%} | {fmt_min(s['first_avg'])} | {fmt_min(s['review_avg'])} |")
        else:
            out.append(f"| {d} | {tgt}m | 0 | - | - | - | - | - |")
    weeks = metrics.weekly(items, cfg, today, 8)
    last4 = weeks[-4:]
    out += ["", "| Last 4 weeks | " + " | ".join(w["week"].strftime("%b %d") for w in last4) + " |",
            "|---|" + "---:|" * len(last4),
            "| New solved | " + " | ".join(str(sum(w["new"].values())) for w in last4) + " |",
            "| Reviews | " + " | ".join(str(w["reviews"]) for w in last4) + " |",
            "| Avg time | " + " | ".join(fmt_min(w["avg_min"]) for w in last4) + " |",
            "| Median time / target | " + " | ".join(f"{w['ratio_all']:.2f}x" if w["ratio_all"] else "-" for w in last4) + " |",
            "| Within target | " + " | ".join(f"{w['within']:.0%}" if w["within"] is not None else "-" for w in last4) + " |",
            "",
            "<p><img src=\"assets/charts/time-trend.svg\" alt=\"Solve time vs target by week\" width=\"49%\"> "
            "<img src=\"assets/charts/solved-per-week.svg\" alt=\"New problems solved per week\" width=\"49%\"></p>",
            "<p><img src=\"assets/charts/first-vs-review.svg\" alt=\"First attempt vs review time by pattern\" width=\"49%\"></p>",
            ""]
    # patterns
    prog = metrics.pattern_progress(items, plist)
    pspeed = metrics.speed_table(items, cfg, key=lambda it: it.meta.get("pattern"))
    out += ["<details>", "<summary><b>Breakdown by pattern</b></summary>", "",
            "| Pattern | Solved | NeetCode 150 | Avg | Median | Within target | First / review | Weakness |",
            "|---|---:|---|---:|---:|---:|---|---:|"]
    for slug, name in PATTERNS:
        p, s = prog[slug], pspeed.get(slug)
        fr = f"{fmt_min(s['first_avg'])} / {fmt_min(s['review_avg'])}" if s else "-"
        out.append(f"| {md_link(name, ROOT / SECTIONS['lc'] / PATTERN_DIRS[slug] / 'README.md', base)} | "
                   f"{p['solved']} | {progress_bar(p['solved_list'], p['total'])} {p['solved_list']}/{p['total']} | "
                   f"{fmt_min(s['avg']) if s else '-'} | {fmt_min(s['median']) if s else '-'} | "
                   f"{f'{s['within']:.0%}' if s else '-'} | {fr} | {weak[slug]['score']:.2f} |")
    n, phases = metrics.sd_phase_stats(items, cfg)
    other = Counter(it.type for it in items.values())
    out += ["", "</details>", "", "<details>", "<summary><b>System design, OA, behavioral, mocks</b></summary>", "",
            f"Design questions: **{other['sd']}** · Concept notes: **{other['concept']}** · "
            f"OA attempts: **{other['oa']}** · STAR stories: **{other['star']}** · Mocks logged: **{other['mock']}** · "
            f"Mastered items: **{mastered}**", "", phase_table(cfg, n, phases), "", "</details>"]
    if any(it.meta.get("sample") for it in items.values()):
        out += ["", "<sub>Includes entries tagged <code>sample</code> that show the format. "
                    "Remove them with <code>prep samples remove</code>.</sub>"]
    return "\n".join(out)


def repo_map(items) -> str:
    def count(folder):
        return len(in_dir(items, ROOT / folder))
    lines = ["```text", "interview-prep/"]
    entries = [
        (SECTIONS["lc"], f"LeetCode by pattern ({count(SECTIONS['lc'])} problems)"),
        (SECTIONS["sd"], f"concepts/, questions/, ood/ ({count(SECTIONS['sd'])} entries)"),
        (SECTIONS["oa"], f"timed OAs by platform ({count(SECTIONS['oa'])})"),
        (SECTIONS["star"], f"STAR stories by theme ({count(SECTIONS['star'])})"),
        (SECTIONS["fund"], "OS, networking, databases, concurrency, web, languages"),
        (SECTIONS["mock"], f"mock log + action items ({count(SECTIONS['mock'])})"),
        (SECTIONS["plan"], "roadmap, spaced repetition, weekly plan"),
        ("templates", "one template per entry type"),
        ("scripts", "the `prep` CLI"),
        ("data", "attempts.csv, config, problem lists, items.json"),
    ]
    for i, (folder, desc) in enumerate(entries):
        branch = "└──" if i == len(entries) - 1 else "├──"
        lines.append(f"{branch} {folder + '/':<24} {desc}")
    lines.append("```")
    links = [
        "| Section | Jump to |", "|---|---|",
        f"| [01 · DSA / LeetCode]({SECTIONS['lc']}/README.md) | " + " · ".join(
            f"[{name}]({SECTIONS['lc']}/{PATTERN_DIRS[s]}/README.md)" for s, name in PATTERNS) + " |",
        f"| [02 · System design]({SECTIONS['sd']}/README.md) | [Concepts]({SECTIONS['sd']}/concepts/README.md) · "
        f"[Questions]({SECTIONS['sd']}/questions/README.md) · [OO design]({SECTIONS['sd']}/ood/README.md) |",
        f"| [03 · Online assessments]({SECTIONS['oa']}/README.md) | " + " · ".join(
            f"[{n}]({SECTIONS['oa']}/{p}/README.md)" for p, n in OA_PLATFORMS.items()) + " |",
        f"| [04 · Behavioral]({SECTIONS['star']}/README.md) | [Stories]({SECTIONS['star']}/README.md#stories) · "
        f"[Theme coverage]({SECTIONS['star']}/README.md#theme-coverage) |",
        f"| [05 · CS fundamentals]({SECTIONS['fund']}/README.md) | " + " · ".join(
            f"[{n}]({SECTIONS['fund']}/{a}/README.md)" for a, n in FUND_AREAS.items()) + " |",
        f"| [06 · Mock interviews]({SECTIONS['mock']}/README.md) | [Upcoming]({SECTIONS['mock']}/README.md#upcoming) · "
        f"[Action items]({SECTIONS['mock']}/README.md#open-action-items) |",
        f"| [07 · Study plan]({SECTIONS['plan']}/README.md) | [Roadmap]({SECTIONS['plan']}/roadmap.md) · "
        f"[Spaced repetition]({SECTIONS['plan']}/spaced-repetition.md) · [This week]({SECTIONS['plan']}/weekly-plan.md) |",
        "| Tooling | [Templates](templates/README.md) · [CLI](scripts/README.md) · [Data](data/README.md) |",
    ]
    return "\n".join(lines + [""] + links)


# ---------------------------------------------------------------- main

def build(quiet: bool = False) -> int:
    cfg = load_config()
    today = get_today()
    items = load_items()
    schedule_all(items, cfg)
    plist = load_problem_list(cfg.get("problem_list", "neetcode150"))
    weak = metrics.weakness(items, cfg, plist, today)
    changed = 0
    for it in items.values():
        changed += update_entry(it, cfg)
    changed += build_patterns(items, cfg, plist, weak)
    changed += build_sections(items, cfg)

    weeks = metrics.weekly(items, cfg, today, 8)
    pspeed = metrics.speed_table(items, cfg, key=lambda it: it.meta.get("pattern"))
    fvr = sorted(((PATTERN_NAMES.get(k, k), v["first_avg"], v["review_avg"]) for k, v in pspeed.items()
                  if v["first_avg"] and v["review_avg"]), key=lambda r: -(r[1] + r[2]))
    charts_dir = ROOT / "assets" / "charts"
    changed += write_text(charts_dir / "time-trend.svg", charts.time_trend(weeks))
    changed += write_text(charts_dir / "solved-per-week.svg", charts.solved_per_week(weeks))
    changed += write_text(charts_dir / "first-vs-review.svg", charts.first_vs_review(fvr))

    plan = build_plan(items, cfg, weak, plist, today)
    changed += update_block_file(ROOT / SECTIONS["plan"] / "weekly-plan.md", "plan", render_plan(plan, items, weak, today))
    due_today, overdue = due(items, today)
    changed += update_block_file(ROOT / SECTIONS["plan"] / "README.md", "status",
                                 f"**Today ({today.isoformat()}):** {len(due_today)} due, {len(overdue)} overdue. "
                                 f"This week: {plan['new_slots']} new + {plan['review_slots']} review slots "
                                 f"({plan['ratio']:.0%} new). See [weekly-plan.md](weekly-plan.md).")
    changed += update_block_file(ROOT / "README.md", "dashboard", build_dashboard(items, cfg, plist, weak, today))
    changed += update_block_file(ROOT / "README.md", "map", repo_map(items))

    snapshot = {
        "generated": today.isoformat(),
        "items": [{"id": it.id, "type": it.type, "title": it.title, "path": rel(it.path),
                   "difficulty": it.difficulty, "pattern": it.meta.get("pattern"), "tags": it.tags,
                   "status": it.srs["status"], "next_review": it.srs.get("next_review"),
                   "attempts": len(it.attempts), "best_minutes": best(it)}
                  for it in sorted(items.values(), key=lambda it: it.id)],
        "weakness": {k: round(v["score"], 3) for k, v in weak.items()},
    }
    changed += write_text(DATA / "items.json", json.dumps(snapshot, indent=1) + "\n")
    if not quiet:
        print(f"build: {len(items)} items, {len(due_today)} due today, {len(overdue)} overdue, {changed} files updated")
    return changed
