"""prep: the interview-prep command line.

Run `prep <command> -h` for options. Common flow:
    prep new lc 146            create the note + solution file (title, folder and tags filled in)
    prep start lc 146          start the timer
    prep stop                  log time + outcome, reschedule, rebuild the dashboard
    prep due                   what to review today
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

from . import timer
from .core import (ATTEMPTS_PATH, INTERVIEWS_PATH, ROOT, fmt_min, iter_markdown, load_config, load_items,
                   read_attempts, read_frontmatter, rel, rewrite_attempts, today, write_entry)


def _items_scheduled():
    from .srs import schedule_all
    items = load_items()
    schedule_all(items, load_config())
    return items


# ---------------------------------------------------------------- commands

def cmd_new(a):
    from .entries import create_lc, create_simple
    kind = a.type
    if kind == "lc":
        if not a.name.isdigit():
            raise SystemExit("usage: prep new lc <number> [\"Title\"]")
        existing = [p for p in (ROOT / "01-dsa-leetcode").glob(f"*/{int(a.name):04d}-*.md")]
        path = create_lc(int(a.name), a.title, lang=a.lang, pattern=a.pattern, difficulty=a.difficulty)
        meta, _ = read_frontmatter(path)
        print(f"{'Updated' if existing else 'Created'} {rel(path)}  [{meta.get('difficulty')}, {meta.get('pattern')}, tags: {', '.join(meta.get('tags', []))}]")
        for lang in meta.get("langs", []):
            print(f"  solution: {rel(path.with_suffix(load_config()['langs'][lang]))}")
        print(f"Next: prep start lc {int(a.name)}")
    else:
        opts = {"limit": a.limit, "format": a.format, "title_given": bool(a.title)}
        name, title = a.name, a.title
        if kind == "oa":
            opts["platform"], name = a.name, (a.title or "assessment")
            title = a.extra
        if kind == "note":
            opts["area"], name = a.name, a.title
            title = a.extra
            if not name:
                raise SystemExit("usage: prep new note <area> <name> [\"Title\"]")
        if kind == "mock":
            opts["format"] = a.title or a.format or "coding"
            title, opts["title_given"] = a.extra, bool(a.extra)
        path = create_simple(kind, name, title, **opts)
        print(f"Created {rel(path)}")
        if kind not in ("mock",):
            meta, _ = read_frontmatter(path)
            print(f"Next: prep start {meta['id']}")
    if not a.no_build:
        from .build import build
        build(quiet=True)


def cmd_start(a):
    timer.start(a.ref, a.lang)


def cmd_stop(a):
    timer.stop(a.outcome, a.grade, a.lang, a.note or "", a.yes)


def cmd_log(a):
    from .entries import resolve
    item = resolve(a.ref)
    phases = []
    if a.phases:
        for part in a.phases.split(","):
            k, v = part.split("=")
            phases.append([k.strip(), float(v)])
    if a.date:
        dt.date.fromisoformat(a.date)
    timer.record(item, a.minutes, outcome=a.outcome, grade=a.grade, lang=a.lang, date=a.date,
                 source="manual", phases=phases, note=a.note or "", assume=a.yes)


def cmd_due(a):
    from .srs import due
    items = _items_scheduled()
    t = today()
    due_today, overdue = due(items, t)
    def show(title, rows):
        print(f"\n{title} ({len(rows)})")
        for it in rows:
            last = it.attempts[-1] if it.attempts else None
            lr = f"{last['outcome']}, {fmt_min(last['minutes'])}" if last else "-"
            cmd = f"prep start lc {it.meta['number']}" if it.type == "lc" else f"prep start {it.id}"
            print(f"  {it.srs['next_review']}  {it.type:<7} {it.label()[:44]:<44} last: {lr:<16} {cmd}")
    show("Overdue", overdue)
    show(f"Due today {t.isoformat()}", due_today)
    if a.days:
        end = (t + dt.timedelta(days=a.days)).isoformat()
        upcoming = sorted((it for it in items.values() if it.srs.get("next_review")
                           and t.isoformat() < it.srs["next_review"] <= end), key=lambda it: it.srs["next_review"])
        show(f"Next {a.days} days", upcoming)


def cmd_find(a):
    items = _items_scheduled()
    from .core import PATTERN_NAMES
    norm = lambda t: re.sub(r"[-_/&]+", " ", t.lower())
    q = norm(" ".join(a.query)).strip()
    hits = []
    for it in items.values():
        hay = " ".join(str(x) for x in [it.id, it.title, it.meta.get("slug", ""), it.meta.get("number", ""),
                                         it.meta.get("pattern", ""), it.difficulty, it.type,
                                         PATTERN_NAMES.get(it.meta.get("pattern"), ""),
                                         " ".join(it.tags), " ".join(it.meta.get("themes") or [])])
        hay = norm(hay)
        if q in hay or (q.isdigit() and str(it.meta.get("number")) == q) or (a.text and q in norm(it.body)):
            hits.append(it)
    other = []
    if a.text:
        for path in iter_markdown():
            meta, body = read_frontmatter(path)
            if not meta.get("id") and q in norm(body):
                other.append(path)
    if not hits and not other:
        print(f"No matches for {q!r}." + ("" if a.text else " Try --text for full-text search."))
        return
    for it in sorted(hits, key=lambda it: (it.type, it.id)):
        print(f"{it.type:<7} {it.label()[:46]:<46} {it.srs.get('status', ''):<10} {rel(it.path)}")
    for p in other:
        print(f"{'note':<7} {p.stem[:46]:<46} {'':<10} {rel(p)}")


def cmd_build(a):
    from .build import build
    build()


def cmd_plan(a):
    from .build import build
    build(quiet=True)
    print((ROOT / "07-study-plan" / "weekly-plan.md").read_text(encoding="utf-8"))


def cmd_next(a):
    from . import metrics
    from .core import load_problem_list
    from .plan import build_plan
    items = _items_scheduled()
    cfg = load_config()
    plist = load_problem_list()
    weak = metrics.weakness(items, cfg, plist, today())
    plan = build_plan(items, cfg, weak, plist, today())
    todays = plan["schedule"][plan["days"][0]]
    print("Today:")
    for t in todays["review"]:
        print(f"  review  {t['label']:<46} {t['cmd']}")
    for t in todays["new"]:
        print(f"  new     {t['label']:<46} {t['cmd']} && prep start lc {t['cmd'].split()[-1]}")
    for o in todays["other"]:
        print(f"  other   {o}")


def cmd_import(a):
    from .importer import run
    run(sync=a.sync, remote=a.remote, online=not a.offline, dry=a.dry_run)
    if not a.dry_run:
        from .build import build
        build()


def cmd_master(a):
    from .entries import resolve
    it = resolve(a.ref)
    meta, body = read_frontmatter(it.path)
    if a.undo:
        meta.pop("status_override", None)
    else:
        meta["status_override"] = "mastered"
    write_entry(it.path, meta, body)
    from .build import build
    build(quiet=True)
    print(f"{it.id}: {'back in rotation' if a.undo else 'marked mastered (no more reviews)'}")


def cmd_interview(a):
    rows = []
    if INTERVIEWS_PATH.exists():
        with open(INTERVIEWS_PATH, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    if a.action == "add":
        dt.date.fromisoformat(a.date)
        rows.append({"date": a.date, "company": a.what, "type": a.type, "notes": a.notes or ""})
    elif a.action == "remove":
        rows = [r for r in rows if not (r["date"] == a.date and (not a.what or r["company"] == a.what))]
    with open(INTERVIEWS_PATH, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "company", "type", "notes"], lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["date"]))
    for r in sorted(rows, key=lambda r: r["date"]):
        mark = "" if r["date"] >= today().isoformat() else " (past)"
        print(f"{r['date']}  {r['type']:<5} {r['company']}{mark}")
    if a.action != "list":
        from .build import build
        build(quiet=True)


LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)|!\[[^\]]*\]\(([^)\s]+)\)|(?:src|href)=\"([^\"]+)\"")


def gh_anchor(heading: str) -> str:
    h = re.sub(r"<[^>]+>", "", heading).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    out, seen = set(), {}
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            a = gh_anchor(m.group(1))
            n = seen.get(a, 0)
            out.add(a if n == 0 else f"{a}-{n}")
            seen[a] = n + 1
    return out


def cmd_check(a):
    broken = 0
    skip = {".git", ".leethub-cache", "node_modules"}
    files = [p for p in ROOT.rglob("*.md") if not skip & set(p.parts)
             and p.parent != ROOT / "templates" or p == ROOT / "templates" / "README.md"]
    files = [p for p in files if not skip & set(p.parts)]
    for path in sorted(files):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        text = re.sub(r"`[^`\n]*`", "", text)
        for m in LINK_RE.finditer(text):
            target = next(g for g in m.groups() if g)
            if re.match(r"^(https?:|mailto:)", target):
                continue
            file_part, _, frag = target.partition("#")
            dest = (path.parent / file_part).resolve() if file_part else path
            if not dest.exists():
                print(f"BROKEN  {rel(path)} -> {target}")
                broken += 1
                continue
            if frag and dest.suffix == ".md" and frag not in anchors(dest):
                print(f"ANCHOR  {rel(path)} -> {target}")
                broken += 1
    print(f"check: {len(files)} markdown files, {broken} broken links")
    if broken:
        sys.exit(1)


def cmd_issue(a):
    from .srs import due
    items = _items_scheduled()
    t = today()
    due_today, overdue = due(items, t)
    repo = load_config().get("github", "")
    lines = [f"Reviews due {t.isoformat()}", ""]
    if not due_today and not overdue:
        lines.append("Nothing due today.")
    for title, rows in (("Overdue", overdue), ("Due today", due_today)):
        if rows:
            lines += [f"### {title} ({len(rows)})", ""]
            for it in rows:
                url = f"https://github.com/{repo}/blob/main/{rel(it.path)}" if repo else rel(it.path)
                cmd = f"prep start lc {it.meta['number']}" if it.type == "lc" else f"prep start {it.id}"
                lines.append(f"- [ ] [{it.label()}]({url}) ({it.type}, due {it.srs['next_review']}): `{cmd}`")
            lines.append("")
    lines += ["<sub>Opened by the daily dashboard workflow. It is closed automatically when nothing is due.</sub>"]
    text = "\n".join(lines) + "\n"
    if a.write:
        Path(a.write).write_text(text, encoding="utf-8")
    else:
        print(text)
    if a.count_file:
        Path(a.count_file).write_text(str(len(due_today) + len(overdue)), encoding="utf-8")


def cmd_samples(a):
    items = load_items()
    samples = [it for it in items.values() if it.meta.get("sample")]
    if a.action == "list" or not samples:
        for it in samples:
            print(f"{it.id:<36} {rel(it.path)}")
        print(f"{len(samples)} sample entries")
        return
    ids = {it.id for it in samples}
    for it in samples:
        for sib in it.path.parent.glob(it.path.stem + ".*"):
            sib.unlink()
        if it.path.name == "design.md" and it.path.parent.exists() and not any(it.path.parent.iterdir()):
            it.path.parent.rmdir()
    rows = [r for r in read_attempts() if r["id"] not in ids]
    rewrite_attempts(rows)
    from .build import build
    build(quiet=True)
    print(f"Removed {len(samples)} sample entries and their attempts.")


# ---------------------------------------------------------------- parser

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(prog="prep", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="create an entry from its template",
                       description="lc <number> [title] | sd <name> [title] | ood <name> [title] | concept <name> [title] | "
                                   "note <area> <name> [title] | oa <platform> <name> [title] | star <slug> [title] | "
                                   "mock <platform> [format] [title]")
    s.add_argument("type", choices=["lc", "sd", "ood", "concept", "note", "oa", "star", "mock"])
    s.add_argument("name")
    s.add_argument("title", nargs="?")
    s.add_argument("extra", nargs="?")
    s.add_argument("--lang", choices=["python", "java", "cpp"])
    s.add_argument("--pattern")
    s.add_argument("--difficulty", choices=["Easy", "Medium", "Hard", "easy", "medium", "hard"])
    s.add_argument("--limit", type=int, help="OA time limit in minutes")
    s.add_argument("--format", help="mock format: coding / system-design / behavioral")
    s.add_argument("--no-build", action="store_true")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("start", help="start the timer: prep start lc 146 | prep start sd url-shortener")
    s.add_argument("ref", nargs="+")
    s.add_argument("--lang", choices=["python", "java", "cpp"])
    s.set_defaults(fn=cmd_start)
    for name, fn, h in (("pause", timer.pause, "pause the timer"), ("resume", timer.resume, "resume the timer"),
                        ("phase", timer.phase, "system design: close the current phase"),
                        ("status", timer.status, "show the running timer"),
                        ("cancel", timer.cancel, "discard the running timer")):
        s = sub.add_parser(name, help=h)
        s.set_defaults(fn=lambda a, f=fn: f())

    def outcome_args(s):
        s.add_argument("--outcome", "-o", choices=["solved", "hints", "failed"])
        s.add_argument("--grade", "-g", choices=["again", "hard", "good", "easy"])
        s.add_argument("--lang", choices=["python", "java", "cpp"])
        s.add_argument("--note")
        s.add_argument("--yes", "-y", action="store_true", help="accept defaults, no prompts")

    s = sub.add_parser("stop", help="stop the timer and log the attempt")
    outcome_args(s)
    s.set_defaults(fn=cmd_stop)

    s = sub.add_parser("log", help="log a time by hand: prep log lc 146 23 -o solved")
    s.add_argument("ref", nargs="+", help="item reference followed by minutes")
    outcome_args(s)
    s.add_argument("--date")
    s.add_argument("--phases", help="system design: requirements=5,estimates=6,...")
    s.set_defaults(fn=lambda a: (setattr(a, "minutes", float(a.ref.pop())), cmd_log(a)))

    s = sub.add_parser("due", help="list today's and overdue reviews")
    s.add_argument("--days", type=int, default=0, help="also show the next N days")
    s.set_defaults(fn=cmd_due)

    s = sub.add_parser("find", help="search by tag, name, number, pattern or id")
    s.add_argument("query", nargs="+")
    s.add_argument("--text", action="store_true", help="also search note bodies")
    s.set_defaults(fn=cmd_find)

    sub.add_parser("build", help="regenerate dashboard, indexes, charts, plan").set_defaults(fn=cmd_build)
    sub.add_parser("plan", help="print the next-7-days plan").set_defaults(fn=cmd_plan)
    sub.add_parser("next", help="what to do today").set_defaults(fn=cmd_next)

    s = sub.add_parser("import", help="pull solutions from your LeetHub repo")
    s.add_argument("--sync", action="store_true", help="git pull the LeetHub repo first")
    s.add_argument("--remote", action="store_true", help="use a temporary clone (CI)")
    s.add_argument("--offline", action="store_true", help="do not call the LeetCode API")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_import)

    s = sub.add_parser("master", help="mark an item mastered (stop reviewing it)")
    s.add_argument("ref", nargs="+")
    s.add_argument("--undo", action="store_true")
    s.set_defaults(fn=cmd_master)

    s = sub.add_parser("interview", help="schedule mocks / real interviews")
    s.add_argument("action", choices=["add", "remove", "list"])
    s.add_argument("date", nargs="?")
    s.add_argument("what", nargs="?")
    s.add_argument("--type", choices=["mock", "real"], default="real")
    s.add_argument("--notes")
    s.set_defaults(fn=cmd_interview)

    sub.add_parser("check", help="verify every relative link and anchor").set_defaults(fn=cmd_check)

    s = sub.add_parser("issue", help="markdown body for the daily reviews issue")
    s.add_argument("--write")
    s.add_argument("--count-file")
    s.set_defaults(fn=cmd_issue)

    s = sub.add_parser("samples", help="list or remove the sample entries")
    s.add_argument("action", choices=["list", "remove"])
    s.set_defaults(fn=cmd_samples)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
