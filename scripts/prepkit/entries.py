"""Create entries from templates and resolve CLI references to items."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from .core import (DATA, FUND_AREAS, OA_PLATFORMS, PATTERN_DIRS, PATTERN_NAMES, ROOT, SECTIONS, Item,
                   load_config, load_items, load_problem_list, parse_frontmatter, read_frontmatter,
                   slugify, today,
                   write_entry, write_text)

TEMPLATES = ROOT / "templates"
CACHE_PATH = DATA / "lc-cache.json"

# LeetCode topic tag -> pattern folder, most specific first.
TOPIC_PATTERNS = [
    ("Trie", "tries"), ("Sliding Window", "sliding-window"), ("Monotonic Stack", "stack"),
    ("Heap (Priority Queue)", "heap-priority-queue"), ("Backtracking", "backtracking"),
    ("Linked List", "linked-list"), ("Binary Search Tree", "trees"), ("Binary Tree", "trees"),
    ("Tree", "trees"), ("Shortest Path", "advanced-graphs"), ("Minimum Spanning Tree", "advanced-graphs"),
    ("Topological Sort", "graphs"), ("Union Find", "graphs"), ("Graph", "graphs"),
    ("Breadth-First Search", "graphs"), ("Depth-First Search", "graphs"), ("Matrix", "math-geometry"),
    ("Two Pointers", "two-pointers"), ("Dynamic Programming", "1-d-dp"), ("Binary Search", "binary-search"),
    ("Stack", "stack"), ("Interval", "intervals"), ("Greedy", "greedy"),
    ("Bit Manipulation", "bit-manipulation"), ("Math", "math-geometry"), ("Hash Table", "arrays-hashing"),
    ("String", "arrays-hashing"), ("Array", "arrays-hashing"),
]


def pattern_from_topics(topics: list[str]) -> str:
    for topic, pat in TOPIC_PATTERNS:
        if topic in topics:
            return pat
    return "arrays-hashing"


def render(template: str, values: dict) -> str:
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values.get(m.group(1), "")), text)


def split_template(text: str) -> tuple[dict, str]:
    return parse_frontmatter(text)


# ---------------------------------------------------------------- LeetCode metadata

def _cache() -> dict:
    return json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}


def lc_lookup(slug: str, online: bool = True) -> dict | None:
    cache = _cache()
    if slug in cache:
        return cache[slug]
    if not online:
        return None
    query = {"query": "query q($s:String!){question(titleSlug:$s){questionFrontendId title difficulty "
                      "isPaidOnly topicTags{name}}}", "variables": {"s": slug}}
    req = urllib.request.Request("https://leetcode.com/graphql", data=json.dumps(query).encode(),
                                 headers={"Content-Type": "application/json", "Referer": "https://leetcode.com",
                                          "User-Agent": "interview-prep-cli"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            q = json.load(resp)["data"]["question"]
    except Exception:
        return None
    if not q:
        return None
    info = {"number": int(q["questionFrontendId"]), "title": q["title"], "difficulty": q["difficulty"],
            "premium": bool(q["isPaidOnly"]), "topics": [t["name"] for t in q["topicTags"]]}
    cache[slug] = info
    write_text(CACHE_PATH, json.dumps(dict(sorted(cache.items())), indent=1) + "\n")
    return info


def lc_by_number(number: int, online: bool = True) -> dict | None:
    for p in load_problem_list():
        if p["number"] == number:
            return {**p, "lists": ["neetcode150"]}
    for slug, info in _cache().items():
        if info["number"] == number:
            return {**info, "slug": slug, "pattern": pattern_from_topics(info["topics"]), "lists": []}
    return None


# ---------------------------------------------------------------- creation

def lc_path(number: int, slug: str, pattern: str) -> Path:
    return ROOT / SECTIONS["lc"] / PATTERN_DIRS[pattern] / f"{number:04d}-{slug}.md"


def add_solution_file(md_path: Path, lang: str, cfg: dict, code: str | None = None) -> Path:
    ext = cfg["langs"][lang]
    sol = md_path.with_suffix(ext)
    if code is not None:
        write_text(sol, code if code.endswith("\n") else code + "\n")
    elif not sol.exists():
        write_text(sol, (TEMPLATES / f"solution{ext}").read_text(encoding="utf-8"))
    meta, body = read_frontmatter(md_path)
    langs = meta.get("langs") or []
    if lang not in langs:
        meta["langs"] = langs + [lang]
        write_entry(md_path, meta, body)
    return sol


def create_lc(number: int, title: str | None = None, *, lang: str | None = None, pattern: str | None = None,
              difficulty: str | None = None, slug: str | None = None, tags: list | None = None,
              extra: dict | None = None, online: bool = True, with_solution: bool = True) -> Path:
    cfg = load_config()
    info = lc_by_number(number, online=False) or {}
    if not info and slug:
        looked = lc_lookup(slug, online)
        if looked:
            info = {**looked, "slug": slug, "pattern": pattern_from_topics(looked["topics"]), "lists": []}
    title = title or info.get("title")
    if not title:
        raise SystemExit(f"LC {number} is not in NeetCode 150 or the cache: pass a title, e.g. "
                         f'`prep new lc {number} "Problem Title" --difficulty Medium --pattern graphs`')
    slug = slug or info.get("slug") or slugify(title)
    if not info.get("difficulty") and online and not difficulty:
        looked = lc_lookup(slug, online)
        if looked:
            info.update(difficulty=looked["difficulty"], topics=looked["topics"],
                        pattern=pattern_from_topics(looked["topics"]))
    pattern = pattern or info.get("pattern") or "arrays-hashing"
    if pattern not in PATTERN_DIRS:
        raise SystemExit(f"unknown pattern {pattern!r}; choose from: {', '.join(PATTERN_DIRS)}")
    difficulty = (difficulty or info.get("difficulty") or "Medium").capitalize()
    lang = lang or cfg["default_lang"]
    path = lc_path(number, slug, pattern)
    if path.exists():
        if with_solution:
            add_solution_file(path, lang, cfg)
        return path
    topic_tags = [slugify(t) for t in info.get("topics", [])][:5]
    tags = tags or list(dict.fromkeys([pattern] + topic_tags))
    text = render("lc.md", {"title": title, "number": number, "slug": slug, "difficulty": difficulty,
                            "pattern": pattern, "pattern_name": PATTERN_NAMES[pattern],
                            "id": f"lc-{number:04d}", "padded": f"{number:04d}"})
    meta, body = split_template(text)
    meta["tags"] = tags
    meta["lists"] = info.get("lists") or []
    meta["langs"] = []
    if info.get("premium") in (True, "1"):
        meta["premium"] = True
    if extra:
        meta.update(extra)
    write_entry(path, meta, body)
    if with_solution:
        add_solution_file(path, lang, cfg)
    return path


def create_simple(kind: str, name: str, title: str | None = None, **opts) -> Path:
    """sd / ood / concept / note / oa / star / mock."""
    d = today().isoformat()
    slug = slugify(name)
    title = title or name.replace("-", " ").title()
    values = {"title": title, "slug": slug, "date": d}
    if kind in ("sd", "ood"):
        sub = "questions" if kind == "sd" else "ood"
        path = ROOT / SECTIONS["sd"] / sub / slug / "design.md"
        values.update(id=f"{kind}-{slug}", category="system-design" if kind == "sd" else "object-oriented")
        template = "system-design.md" if kind == "sd" else "ood.md"
    elif kind == "concept":
        path = ROOT / SECTIONS["sd"] / "concepts" / f"{slug}.md"
        values.update(id=f"concept-{slug}", area="system-design")
        template = "concept.md"
    elif kind == "note":
        area = opts.get("area")
        if area not in FUND_AREAS:
            raise SystemExit(f"area must be one of: {', '.join(FUND_AREAS)}")
        path = ROOT / SECTIONS["fund"] / area / f"{slug}.md"
        values.update(id=f"concept-{area}-{slug}", area=area)
        template = "concept.md"
    elif kind == "oa":
        platform = opts.get("platform")
        if platform not in OA_PLATFORMS:
            raise SystemExit(f"platform must be one of: {', '.join(OA_PLATFORMS)}")
        stem = f"{d}-{platform}-{slug}"
        path = ROOT / SECTIONS["oa"] / platform / f"{stem}.md"
        values.update(id=f"oa-{stem}", platform=platform, platform_name=OA_PLATFORMS[platform],
                      time_limit=opts.get("limit") or 70,
                      title=title if title else f"{OA_PLATFORMS[platform]} {name.replace('-', ' ').upper()}")
        template = "oa.md"
    elif kind == "star":
        path = ROOT / SECTIONS["star"] / "stories" / f"{slug}.md"
        values.update(id=f"star-{slug}")
        template = "star.md"
    elif kind == "mock":
        fmt = opts.get("format") or "coding"
        stem = f"{d}-{slug}-{fmt}"
        path = ROOT / SECTIONS["mock"] / f"{stem}.md"
        values.update(id=f"mock-{stem}", platform=name, format=fmt,
                      title=title if opts.get("title_given") else f"{name.title()} {fmt} mock")
        template = "mock.md"
    else:
        raise SystemExit(f"unknown type {kind}")
    if path.exists():
        return path
    text = render(template, values)
    meta, body = split_template(text)
    write_entry(path, meta, body)
    return path


# ---------------------------------------------------------------- resolving references

def resolve(args: list[str], items: dict[str, Item] | None = None) -> Item:
    """`lc 146`, `lc-0146`, `146`, `sd url-shortener`, `url-shortener`, or any unique id suffix."""
    items = items if items is not None else load_items()
    if not args:
        raise SystemExit("which item? e.g. `lc 146` or `sd url-shortener`")
    if len(args) >= 2:
        kind, key = args[0].lower(), "-".join(args[1:])
        if kind == "lc" and key.isdigit():
            cand = f"lc-{int(key):04d}"
        else:
            cand = f"{kind}-{key}"
        if cand in items:
            return items[cand]
        args = [cand]
    key = args[0].lower()
    if key.isdigit():
        key = f"lc-{int(key):04d}"
    if key in items:
        return items[key]
    matches = [it for it in items.values() if it.id.endswith(key) or it.id.endswith("-" + key)
               or it.meta.get("slug") == key]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"no entry matches {' '.join(args)!r}. Create it first, e.g. `prep new lc 146`.")
    raise SystemExit("ambiguous: " + ", ".join(sorted(m.id for m in matches)))
