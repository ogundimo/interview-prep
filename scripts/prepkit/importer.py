"""`prep import`: pull solutions from a LeetHub-synced repo and link them to timed attempts.

LeetHub layout: <NNNN>-<slug>/<NNNN>-<slug>.<ext> + README.md (problem statement).
LeetHub's NNNN is sometimes LeetCode's internal id, not the public number, so
problems are matched by slug and renumbered from NeetCode 150 / the LeetCode API.
Problem statements are not copied (only a link).
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
from pathlib import Path

from .core import (DATA, ROOT, append_attempt, load_config, load_items, load_problem_list, read_frontmatter,
                   write_entry)
from .entries import add_solution_file, create_lc, lc_lookup, pattern_from_topics

DIR_RE = re.compile(r"^(\d{4})-([a-z0-9-]+)$")
EXT_LANG = {".py": "python", ".java": "java", ".cpp": "cpp", ".cc": "cpp"}


def _git(repo: Path, *args) -> str:
    return subprocess.run(["git", "-c", "core.longpaths=true", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def _topics_from_readme(repo: Path) -> dict[str, list[str]]:
    """LeetHub's root README lists problems under '## <Topic>' headings."""
    readme = repo / "README.md"
    out: dict[str, list[str]] = {}
    if not readme.exists():
        return out
    topic = None
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            topic = line[3:].strip()
        elif topic:
            for m in re.finditer(r"\[(\d{4}-[a-z0-9-]+)\]", line):
                out.setdefault(m.group(1), []).append(topic)
    return out


def _readme_meta(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    m = re.search(r'<a href="https://leetcode.com/problems/([a-z0-9-]+)/?">(\d+)\. ([^<]+)</a>', text)
    d = re.search(r"<h3>(Easy|Medium|Hard)</h3>", text)
    out = {}
    if m:
        out.update(slug=m.group(1), title=m.group(3).replace("&#39;", "'").replace("&amp;", "&").strip())
    if d:
        out["difficulty"] = d.group(1)
    return out


def locate(cfg: dict, sync: bool, remote: bool) -> Path:
    lh = cfg["leethub"]
    if remote:
        repo = DATA / ".leethub-cache"
        if (repo / ".git").exists():
            _git(repo, "pull", "-q", "--ff-only")
        else:
            subprocess.run(["git", "-c", "core.longpaths=true", "clone", "-q", lh["url"], str(repo)], check=True)
        return repo
    repo = (ROOT / lh["path"]).resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"LeetHub repo not found at {repo}. Clone it:\n  git clone {lh['url']} \"{repo}\"\n"
                         "or run `prep import --remote` to use a temporary clone.")
    if sync:
        _git(repo, "pull", "-q", "--ff-only")
    return repo


def run(sync: bool = False, remote: bool = False, online: bool = True, dry: bool = False) -> int:
    cfg = load_config()
    repo = locate(cfg, sync, remote)
    plist = {p["slug"]: p for p in load_problem_list()}
    topics_map = _topics_from_readme(repo)
    items = load_items()
    by_slug = {it.meta.get("slug"): it for it in items.values() if it.type == "lc"}
    cutoff = cfg.get("legacy", {}).get("cutoff", "0000")
    created = updated = linked = new_rows = 0
    for d in sorted(p for p in repo.iterdir() if p.is_dir()):
        m = DIR_RE.match(d.name)
        if not m:
            continue
        lh_slug = m.group(2)
        rmeta = _readme_meta(d / "README.md")
        slug = rmeta.get("slug", lh_slug)
        sols = [f for f in sorted(d.iterdir()) if f.suffix in EXT_LANG]
        if not sols:
            continue
        if slug in plist:
            p = plist[slug]
            number, title, diff, pattern = p["number"], p["title"], p["difficulty"], p["pattern"]
            topics = topics_map.get(d.name, [])
        else:
            info = lc_lookup(slug, online) or {}
            topics = info.get("topics") or topics_map.get(d.name, [])
            number = info.get("number") or int(m.group(1))
            title = info.get("title") or rmeta.get("title") or slug.replace("-", " ").title()
            diff = info.get("difficulty") or rmeta.get("difficulty") or "Easy"
            pattern = pattern_from_topics(topics)
        dates = sorted(set(_git(repo, "log", "--format=%cs", "--", d.name).split()))
        if dry:
            print(f"{d.name:<60} -> lc-{number:04d} {pattern:<20} {diff:<6} first {dates[0] if dates else '?'}")
            continue
        it = by_slug.get(slug)
        if it is None:
            tag_list = list(dict.fromkeys([pattern] + [re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
                                                      for t in topics][:4]))
            path = create_lc(number, title, pattern=pattern, difficulty=diff, slug=slug, tags=tag_list,
                             extra={"source": "leethub"}, online=False, with_solution=False)
            created += 1
        else:
            path = it.path
        for f in sols:
            lang = EXT_LANG[f.suffix]
            code = f.read_text(encoding="utf-8")
            dest = path.with_suffix(cfg["langs"][lang])
            if not dest.exists() or dest.read_text(encoding="utf-8").strip() != code.strip():
                add_solution_file(path, lang, cfg, code)
                updated += 1
            else:
                add_solution_file(path, lang, cfg, None)
        # link commits to attempts: any attempt within +-1 day of a commit counts as that solve
        existing = [a["date"] for a in (it.attempts if it else [])]
        # a brand-new entry only gets its first solve; later commits on tracked entries become attempts
        # (history before the cutoff is collapsed into that first solve)
        for day in (dates[:1] if it is None else [d for d in dates if d >= cutoff]):
            dd = dt.date.fromisoformat(day)
            near = any(abs((dt.date.fromisoformat(x) - dd).days) <= 1 for x in existing)
            if near:
                linked += 1
                continue
            if existing and day <= max(existing):
                continue  # older than what we already track
            if existing or day == dates[0]:
                append_attempt({"id": f"lc-{number:04d}" if it is None else it.id, "date": day, "minutes": None,
                                "outcome": "solved", "grade": "", "lang": EXT_LANG[sols[0].suffix],
                                "source": "legacy" if day < cutoff else "leethub",
                                "note": "imported from LeetHub (untimed)"})
                existing.append(day)
                new_rows += 1
    if not dry:
        print(f"import: {created} new entries, {updated} solution files written, "
              f"{new_rows} untimed attempts added, {linked} commits already tracked")
    return created + updated + new_rows
