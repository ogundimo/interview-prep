"""`prep start / pause / resume / phase / stop / status / cancel` and manual `prep log`."""
from __future__ import annotations

import datetime as dt
import json

from .core import (GRADES, OUTCOMES, TIMER_PATH, append_attempt, is_timed, load_config, load_items,
                   now, rel, today)
from .entries import resolve
from .srs import schedule, suggest_grade


def _load():
    return json.loads(TIMER_PATH.read_text(encoding="utf-8")) if TIMER_PATH.exists() else None


def _save(state):
    TIMER_PATH.write_text(json.dumps(state, indent=1), encoding="utf-8")


def elapsed_min(state) -> float:
    secs = sum((dt.datetime.fromisoformat(b) - dt.datetime.fromisoformat(a)).total_seconds()
               for a, b in state["segments"])
    if state.get("running_since"):
        secs += (now() - dt.datetime.fromisoformat(state["running_since"])).total_seconds()
    return secs / 60


def _clock(m: float) -> str:
    s = int(round(m * 60))
    return f"{s // 60:02d}:{s % 60:02d}"


def start(ref: list[str], lang: str | None = None):
    st = _load()
    if st:
        raise SystemExit(f"a timer is already running for {st['id']} ({_clock(elapsed_min(st))}). "
                         "Use `prep stop` or `prep cancel` first.")
    cfg = load_config()
    item = resolve(ref)
    target = item.target(cfg)
    state = {"id": item.id, "type": item.type, "title": item.title, "target": target,
             "started": now().isoformat(), "running_since": now().isoformat(), "segments": [],
             "lang": lang, "phases": [], "phase_mark": 0.0}
    _save(state)
    kind = "review" if item.attempts else "first attempt"
    print(f"Timer started: {item.label()} [{item.difficulty or item.type}] ({kind}), target {target:g} min"
          if target else f"Timer started: {item.label()} ({kind})")
    if item.type == "sd":
        p, m = cfg["sd_phases"][0]
        print(f"Phase 1/{len(cfg['sd_phases'])}: {p} ({m} min). Run `prep phase` to move to the next phase.")
    print(f"File: {rel(item.path)}")


def pause():
    st = _require()
    if not st.get("running_since"):
        raise SystemExit("already paused")
    st["segments"].append([st["running_since"], now().isoformat()])
    st["running_since"] = None
    _save(st)
    print(f"Paused at {_clock(elapsed_min(st))}. `prep resume` to continue.")


def resume():
    st = _require()
    if st.get("running_since"):
        raise SystemExit("timer is running")
    st["running_since"] = now().isoformat()
    _save(st)
    print(f"Resumed at {_clock(elapsed_min(st))}.")


def phase():
    st = _require()
    cfg = load_config()
    phases = cfg["sd_phases"]
    i = len(st["phases"])
    if i >= len(phases):
        raise SystemExit("all phases done; run `prep stop`")
    e = elapsed_min(st)
    took = e - st["phase_mark"]
    name, tgt = phases[i]
    st["phases"].append([name, round(took, 1)])
    st["phase_mark"] = e
    _save(st)
    flag = "on time" if took <= tgt else f"+{took - tgt:.1f} over"
    print(f"{name}: {took:.1f} min (target {tgt}, {flag})")
    if i + 1 < len(phases):
        n, m = phases[i + 1]
        print(f"Phase {i + 2}/{len(phases)}: {n} ({m} min)")
    else:
        print("Last phase done. `prep stop` to log.")


def status():
    st = _load()
    if not st:
        print("No timer running.")
        return
    e = elapsed_min(st)
    state = "running" if st.get("running_since") else "paused"
    line = f"{st['id']} ({st['title']}): {_clock(e)} {state}"
    if st.get("target"):
        rem = st["target"] - e
        line += f", {'remaining ' + _clock(rem) if rem >= 0 else 'over by ' + _clock(-rem)} (target {st['target']:g}m)"
    print(line)
    if st["type"] == "sd":
        cfg = load_config()
        i = len(st["phases"])
        if i < len(cfg["sd_phases"]):
            n, m = cfg["sd_phases"][i]
            print(f"Current phase: {n}, {e - st['phase_mark']:.1f}/{m} min")


def cancel():
    st = _require()
    TIMER_PATH.unlink()
    print(f"Discarded timer for {st['id']} ({_clock(elapsed_min(st))}).")


def _require():
    st = _load()
    if not st:
        raise SystemExit("no timer running. Start one with `prep start lc 146`.")
    return st


def _ask(prompt: str, choices: dict, default: str, assume: bool) -> str:
    if assume:
        return default
    keys = "/".join(f"[{k}]{v[len(k):]}" if v.startswith(k) else f"{k}={v}" for k, v in choices.items())
    while True:
        try:
            ans = input(f"{prompt} {keys} (Enter = {default}): ").strip().lower()
        except EOFError:
            return default
        if not ans:
            return default
        for k, v in choices.items():
            if ans in (k, v):
                return v
        print("  ?", ", ".join(choices.values()))


def record(item, minutes: float | None, *, outcome=None, grade=None, lang=None, date=None, source="timer",
           phases=None, note="", assume=False):
    cfg = load_config()
    outcome = outcome or _ask("Outcome?", {"s": "solved", "h": "hints", "f": "failed"}, "solved", assume)
    if outcome not in OUTCOMES:
        raise SystemExit(f"outcome must be one of {OUTCOMES}")
    target = item.target(cfg)
    prev = [a["minutes"] for a in item.attempts if is_timed(a)]
    suggestion = suggest_grade(outcome, minutes, target, min(prev) if prev else None)
    if item.attempts and not grade:
        grade = _ask(f"Grade (suggested: {suggestion})?", {"a": "again", "h": "hard", "g": "good", "e": "easy"},
                     suggestion, assume)
    grade = grade or suggestion
    if grade not in GRADES:
        raise SystemExit(f"grade must be one of {GRADES}")
    if item.type == "lc":
        langs = item.meta.get("langs") or [cfg["default_lang"]]
        lang = lang or langs[0]
    row = {"id": item.id, "date": (date or today().isoformat()), "minutes": minutes, "outcome": outcome,
           "grade": grade, "lang": lang or "", "source": source,
           "phases": ";".join(f"{k}={v:g}" for k, v in (phases or [])), "note": note}
    append_attempt(row)
    # report new schedule
    from .build import build
    build(quiet=True)
    fresh = load_items()[item.id]
    from .srs import legacy_slots
    sched = schedule(fresh, cfg, legacy_slots(list(load_items().values()), cfg).get(item.id))
    t = f"{minutes:.1f} min" if minutes is not None else "untimed"
    vs = ""
    if minutes is not None and target:
        vs = f" ({'within' if minutes <= target else 'over'} {target:g}m target)"
    print(f"Logged {item.id}: {t}{vs}, {outcome}, grade {grade}.")
    if sched.get("next_review"):
        print(f"Next review: {sched['next_review']} (status {sched['status']}, streak {sched['streak']}/"
              f"{cfg['mastery_streak']}). Dashboard rebuilt.")
    if not item.meta.get("key_insight") and item.type in ("lc", "sd"):
        print(f"Tip: fill in key_insight / complexity in {item.path.name}.")


def stop(outcome=None, grade=None, lang=None, note="", assume=False):
    st = _require()
    if st.get("running_since"):
        st["segments"].append([st["running_since"], now().isoformat()])
        st["running_since"] = None
    minutes = round(elapsed_min(st), 1)
    phases = st.get("phases", [])
    if st["type"] == "sd":
        cfg = load_config()
        done = {p for p, _ in phases}
        rest = [p for p, _ in cfg["sd_phases"] if p not in done]
        if rest:
            phases.append([rest[0], round(minutes - st["phase_mark"], 1)])
    item = resolve([st["id"]])
    print(f"Stopped {st['id']} at {_clock(minutes)}.")
    _save(st)  # keep the stopped time if anything below fails; `prep stop` again retries
    record(item, minutes, outcome=outcome, grade=grade, lang=lang or st.get("lang"), phases=phases,
           note=note, assume=assume)
    TIMER_PATH.unlink(missing_ok=True)
