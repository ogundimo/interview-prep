"""Dependency-free SVG charts that render on GitHub in light and dark mode."""
from __future__ import annotations

from html import escape

W, H = 720, 280
PAD_L, PAD_R, PAD_T, PAD_B = 52, 96, 48, 40

STYLE = """<style>
  .bg{fill:#fcfcfb;stroke:rgba(11,11,11,.10)}
  .t1{fill:#0b0b0b;font:600 14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
  .t2{fill:#52514e;font:12px -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
  .t3{fill:#898781;font:11px -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
  .grid{stroke:#e1e0d9;stroke-width:1}
  .axis{stroke:#c3c2b7;stroke-width:1}
  .ref{stroke:#52514e;stroke-width:1.5;stroke-dasharray:5 4}
  .s1{fill:#2a78d6;stroke:#2a78d6}.s2{fill:#eb6834;stroke:#eb6834}.s3{fill:#1baf7a;stroke:#1baf7a}
  path.line{fill:none!important;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
  .dot{stroke:#fcfcfb;stroke-width:2}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19;stroke:rgba(255,255,255,.10)}
    .t1{fill:#f0efec}.t2{fill:#c3c2b7}
    .grid{stroke:#2c2c2a}.axis{stroke:#383835}.ref{stroke:#c3c2b7}
    .s1{fill:#3987e5;stroke:#3987e5}.s2{fill:#d95926;stroke:#d95926}.s3{fill:#199e70;stroke:#199e70}
    .dot{stroke:#1a1a19}
  }
</style>"""


def _frame(title: str, subtitle: str, inner: str, legend: list[tuple[str, str]]) -> str:
    leg, x = [], PAD_L
    for cls, name in legend:
        leg.append(f'<rect class="{cls}" x="{x}" y="34" width="10" height="10" rx="2"/>'
                   f'<text class="t2" x="{x + 15}" y="43">{escape(name)}</text>')
        x += 24 + 7 * len(name)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="{escape(title)}">{STYLE}'
            f'<rect class="bg" x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8"/>'
            f'<text class="t1" x="{PAD_L}" y="22">{escape(title)}</text>'
            f'<text class="t3" x="{W - 16}" y="22" text-anchor="end">{escape(subtitle)}</text>'
            + "".join(leg) + inner + "</svg>\n")


def _empty(title: str, msg: str) -> str:
    return _frame(title, "", f'<text class="t2" x="{W / 2}" y="{H / 2}" text-anchor="middle">'
                             f'{escape(msg)}</text>', [])


def _y_axis(ymax: float, steps: int, fmt) -> tuple[str, callable]:
    top, bottom = PAD_T + 8, H - PAD_B
    def y(v):
        return bottom - (v / ymax) * (bottom - top)
    out = []
    for i in range(steps + 1):
        v = ymax * i / steps
        out.append(f'<line class="{"axis" if i == 0 else "grid"}" x1="{PAD_L}" x2="{W - PAD_R}" '
                   f'y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                   f'<text class="t3" x="{PAD_L - 8}" y="{y(v) + 4:.1f}" text-anchor="end">{fmt(v)}</text>')
    return "".join(out), y


def time_trend(weeks: list[dict]) -> str:
    title = "Solve time vs target, by week"
    series = [("Easy", "s3"), ("Medium", "s1"), ("Hard", "s2")]
    vals = [w["ratio"].get(d) for w in weeks for d, _ in series if w["ratio"].get(d) is not None]
    if not vals:
        return _empty(title, "No timed attempts yet - run `prep start lc <n>`")
    ymax = max(2.0, round(max(vals) + 0.25, 1))
    grid, y = _y_axis(ymax, 4, lambda v: f"{v:.1f}x")
    n = len(weeks)
    span = W - PAD_L - PAD_R
    def x(i):
        return PAD_L + 16 + i * (span - 32) / max(n - 1, 1)
    parts = [grid]
    parts.append(f'<line class="ref" x1="{PAD_L}" x2="{W - PAD_R}" y1="{y(1):.1f}" y2="{y(1):.1f}"/>'
                 f'<text class="t2" x="{W - PAD_R + 6}" y="{y(1) + 4:.1f}">target</text>')
    for i, w in enumerate(weeks):
        parts.append(f'<text class="t3" x="{x(i):.1f}" y="{H - PAD_B + 18}" text-anchor="middle">'
                     f'{w["week"].strftime("%b %d")}</text>')
    for diff, cls in series:
        pts = [(i, w["ratio"].get(diff)) for i, w in enumerate(weeks)]
        seg, segs = [], []
        for i, v in pts:
            if v is None:
                if seg:
                    segs.append(seg)
                seg = []
            else:
                seg.append((x(i), y(v), v, weeks[i]["week"]))
        if seg:
            segs.append(seg)
        for s in segs:
            if len(s) > 1:
                d = " ".join(f"{'M' if j == 0 else 'L'}{px:.1f},{py:.1f}" for j, (px, py, _, _) in enumerate(s))
                parts.append(f'<path class="line {cls}" d="{d}"/>')
            for px, py, v, wk in s:
                parts.append(f'<circle class="dot {cls}" cx="{px:.1f}" cy="{py:.1f}" r="4.5">'
                             f'<title>{diff}, week of {wk.isoformat()}: {v:.2f}x target</title></circle>')
        last = next(((x(i), y(v)) for i, v in reversed(pts) if v is not None), None)
        if last:
            parts.append(f'<text class="t2" x="{W - PAD_R + 6}" y="{last[1] + 4:.1f}">{diff}</text>'
                         if abs(last[1] - y(1)) > 10 else "")
    return _frame(title, "median time / target (lower is faster)", "".join(parts),
                  [(c, d) for d, c in series])


def _bar_path(x, y0, y1, w, r):
    """Vertical bar from y0 (bottom) up to y1 with rounded top corners."""
    r = min(r, w / 2, max(y0 - y1, 0))
    return (f"M{x:.1f},{y0:.1f} L{x:.1f},{y1 + r:.1f} Q{x:.1f},{y1:.1f} {x + r:.1f},{y1:.1f} "
            f"L{x + w - r:.1f},{y1:.1f} Q{x + w:.1f},{y1:.1f} {x + w:.1f},{y1 + r:.1f} L{x + w:.1f},{y0:.1f} Z")


def solved_per_week(weeks: list[dict]) -> str:
    title = "New problems solved per week"
    series = [("Easy", "s3"), ("Medium", "s1"), ("Hard", "s2")]
    totals = [sum(w["new"].values()) for w in weeks]
    if not any(totals):
        return _empty(title, "Nothing solved in this window yet")
    top_v = max(totals)
    step = max(1, -(-top_v // 4))
    ymax = step * 4
    grid, y = _y_axis(ymax, 4, lambda v: f"{v:.0f}")
    n = len(weeks)
    span = W - PAD_L - PAD_R
    slot = span / n
    bw = min(36, slot * 0.6)
    parts = [grid]
    for i, w in enumerate(weeks):
        bx = PAD_L + i * slot + (slot - bw) / 2
        base = y(0)
        present = [(d, c, w["new"].get(d, 0)) for d, c in series if w["new"].get(d, 0)]
        for j, (d, c, v) in enumerate(present):
            top = base - (y(0) - y(v))
            seg_bottom = base - (2 if j > 0 else 0)
            if j == len(present) - 1:
                parts.append(f'<path class="{c}" d="{_bar_path(bx, seg_bottom, top, bw, 4)}">'
                             f'<title>{d}: {v} (week of {w["week"].isoformat()})</title></path>')
            else:
                parts.append(f'<rect class="{c}" x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" '
                             f'height="{max(seg_bottom - top, 0):.1f}"><title>{d}: {v}</title></rect>')
            base = top
        if totals[i]:
            parts.append(f'<text class="t2" x="{bx + bw / 2:.1f}" y="{base - 6:.1f}" text-anchor="middle">'
                         f'{totals[i]}</text>')
        parts.append(f'<text class="t3" x="{bx + bw / 2:.1f}" y="{H - PAD_B + 18}" text-anchor="middle">'
                     f'{w["week"].strftime("%b %d")}</text>')
    return _frame(title, "first solves (Easy / Medium / Hard)", "".join(parts),
                  [(c, d) for d, c in series])


def first_vs_review(rows: list[tuple[str, float, float]]) -> str:
    """rows: (pattern name, first-attempt avg minutes, review avg minutes)."""
    title = "First attempt vs later reviews"
    if not rows:
        return _empty(title, "Needs at least one reviewed problem")
    rows = rows[:6]
    vmax = max(max(f, r) for _, f, r in rows)
    ymax = max(10, -(-vmax // 10) * 10)
    grid, y = _y_axis(ymax, 4, lambda v: f"{v:.0f}m")
    span = W - PAD_L - PAD_R
    slot = span / len(rows)
    bw = min(26, slot * 0.3)
    parts = [grid]
    for i, (name, f, r) in enumerate(rows):
        cx = PAD_L + i * slot + slot / 2
        for k, (v, c, lab) in enumerate(((f, "s1", "first"), (r, "s2", "review"))):
            bx = cx - bw - 1 + k * (bw + 2)
            parts.append(f'<path class="{c}" d="{_bar_path(bx, y(0), y(v), bw, 4)}">'
                         f'<title>{name} {lab}: {v:.1f} min</title></path>')
        delta = (r - f) / f if f else 0
        parts.append(f'<text class="t2" x="{cx:.1f}" y="{y(max(f, r)) - 6:.1f}" text-anchor="middle">'
                     f'{delta:+.0%}</text>')
        label = name if len(name) <= 16 else name[:15] + "."
        parts.append(f'<text class="t3" x="{cx:.1f}" y="{H - PAD_B + 18}" text-anchor="middle">{escape(label)}</text>')
    return _frame(title, "avg minutes per pattern (label = change)", "".join(parts),
                  [("s1", "First attempt"), ("s2", "Reviews")])
