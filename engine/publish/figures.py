"""Figures: diagrams, charts and tables drawn from an entry's own facts, for any EPUB reader (e-ink included).

EPUB readers run no JavaScript, so nothing is drawn on the device: tables become plain XHTML tables and every
other figure is drawn here, with Pillow, as a sharp grayscale PNG. Figures live in subjects/<s>/figures.json,
keyed by entry id (an entry may have several, drawn after its text in list order):

    {"soil-phys-003": [{"type": "scale", "caption": "...", "sent_ids": ["..."], ...}]}

Every figure has `type`, `caption` (one sentence, no new facts) and `sent_ids` (the sentences it draws on).
`write check` holds figures to the prose rule: every number in a figure must be in its entry's facts.

Types and their fields:
  table   header: [..], rows: [[..], ..]                    comparisons, classifications, properties side by side
  flow    mermaid: "flowchart TD|LR" + lines `A[Label] --> B[Label]`, `A -->|label| B`, `A -.-> B`,
          `A{Decision}`, `A([Rounded])`; a subset of Mermaid    processes, causal chains, decision keys
  cycle   steps: [..] (or [[step, arrow label], ..])          nutrient, carbon, water and rock cycles
  layers  layers: [[name, note], ..] top to bottom; optional `top`/`bottom` labels   horizons, strata, atmosphere
  scale   axis: label, log: bool, marks: [[value, label], ..] or ranges: [[from, to, label], ..]
                                                               grain sizes, pH, time scales, orders of magnitude
  bar     unit: label, bars: [[label, value], ..]             quantities to compare (only numbers from the facts)
  tree    root: label, children: {label: {..} | null}        hierarchies and taxonomies
"""
import hashlib
import io
import json
import math
import re
from html import escape

from PIL import Image, ImageDraw, ImageFont

W = 1000                      # drawn width in px; readers scale it to the screen
INK, MID, PALE, PAPER = 0, 110, 215, 255
PAD = 24
TYPES = ("table", "flow", "cycle", "layers", "scale", "bar", "tree")
_FONTS = {}


def font(size=26, bold=False):
    k = (size, bold)
    if k not in _FONTS:
        f = None
        if bold:
            for p in ("DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
                try:
                    f = ImageFont.truetype(p, size)
                    break
                except OSError:
                    pass
        _FONTS[k] = f or ImageFont.load_default(size=size)
    return _FONTS[k]


def _tw(t, f):
    b = f.getbbox(t or " ")
    return b[2] - b[0]


def wrap(text, f, width):
    lines, cur = [], ""
    for w in str(text).split():
        t = f"{cur} {w}".strip()
        if cur and _tw(t, f) > width:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + ([cur] if cur else []) or [""]


def _lh(f):
    return int(f.size * 1.25)


def text_block(d, cx, y, text, f, width, fill=INK, align="center"):
    """Draw wrapped text centered on cx (or left-aligned at cx); return the height used."""
    lines = wrap(text, f, width)
    for k, ln in enumerate(lines):
        x = cx - _tw(ln, f) / 2 if align == "center" else cx
        d.text((x, y + k * _lh(f)), ln, font=f, fill=fill)
    return len(lines) * _lh(f)


def text_h(text, f, width):
    return len(wrap(text, f, width)) * _lh(f)


def arrow(d, p, q, width=3, head=16, dashed=False, fill=INK):
    (x1, y1), (x2, y2) = p, q
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * 0.8 * math.cos(ang), y2 - head * 0.8 * math.sin(ang)
    if dashed:
        n = max(1, int(math.hypot(bx - x1, by - y1) // 14))
        for k in range(0, n, 2):
            a, b = k / n, min(1, (k + 1) / n)
            d.line([(x1 + (bx - x1) * a, y1 + (by - y1) * a), (x1 + (bx - x1) * b, y1 + (by - y1) * b)],
                   fill=fill, width=width)
    else:
        d.line([(x1, y1), (bx, by)], fill=fill, width=width)
    l, r = ang + math.radians(152), ang - math.radians(152)
    d.polygon([(x2, y2), (x2 + head * math.cos(l), y2 + head * math.sin(l)),
               (x2 + head * math.cos(r), y2 + head * math.sin(r))], fill=fill)


def _canvas(h):
    img = Image.new("L", (W, int(h)), PAPER)
    return img, ImageDraw.Draw(img)


def _fmt(v):
    return f"{v:,.0f}" if abs(v) >= 1000 and v == int(v) else (f"{v:g}" if v == int(v) or abs(v) >= 1 else f"{v:g}")


# -- flow (Mermaid subset) ---------------------------------------------------
NODE = re.compile(r"([A-Za-z_][\w]*)\s*(\(\[.*?\]\)|\[\[.*?\]\]|\[.*?\]|\(\(.*?\)\)|\(.*?\)|\{.*?\})?")
EDGE = re.compile(r"\s*(-->|---|-\.->|==>)\s*(?:\|([^|]*)\|\s*)?")


def parse_mermaid(src):
    lines = [ln.strip() for ln in src.strip().splitlines() if ln.strip() and not ln.strip().startswith("%%")]
    head = lines[0].split() if lines else []
    if not head or head[0] not in ("flowchart", "graph"):
        raise ValueError("mermaid must start with 'flowchart TD' or 'flowchart LR'")
    direction = (head[1] if len(head) > 1 else "TD").upper()
    nodes, edges = {}, []

    def node(tok):
        m = NODE.fullmatch(tok.strip())
        if not m:
            raise ValueError(f"cannot read node {tok!r}")
        nid, shape = m.group(1), m.group(2)
        if shape:
            if shape.startswith("{"):
                kind, label = "decision", shape[1:-1]
            elif shape.startswith(("([", "((", "(")):
                kind, label = "round", shape.strip("()[]")
            else:
                kind, label = "box", shape.strip("[]")
            nodes[nid] = {"label": label.strip().strip('"'), "kind": kind}
        else:
            nodes.setdefault(nid, {"label": nid, "kind": "box"})
        return nid

    for ln in lines[1:]:
        if ln.startswith(("classDef", "class ", "style ", "linkStyle", "subgraph", "end", "direction")):
            continue
        parts = EDGE.split(ln)
        # parts: node, op, label, node, op, label, node ...
        prev = node(parts[0])
        for k in range(1, len(parts) - 1, 3):
            op, label, nxt = parts[k], parts[k + 1], node(parts[k + 2])
            edges.append({"a": prev, "b": nxt, "label": (label or "").strip(), "dashed": op == "-.->",
                          "arrow": op != "---"})
            prev = nxt
    return direction in ("LR", "RL"), nodes, edges


def draw_flow(fig):
    horiz, nodes, edges = parse_mermaid(fig["mermaid"])
    ids = list(nodes)
    # longest-path layering over the graph with back edges (cycles) ignored
    out = {i: [] for i in ids}
    for e in edges:
        out[e["a"]].append(e["b"])
    state, back = {}, set()

    def dfs(u):
        state[u] = 1
        for v in out[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif not state.get(v):
                dfs(v)
        state[u] = 2
    for i in ids:
        if not state.get(i):
            dfs(i)
    layer = {i: 0 for i in ids}
    for _ in ids:
        for e in edges:
            if (e["a"], e["b"]) not in back and layer[e["b"]] < layer[e["a"]] + 1:
                layer[e["b"]] = layer[e["a"]] + 1
    n_layers = max(layer.values()) + 1
    rows = [[i for i in ids if layer[i] == k] for k in range(n_layers)]
    for k in range(1, n_layers):   # order each layer by its parents' mean position
        prev = {i: p for p, i in enumerate(rows[k - 1])}
        def bary(i):
            ps = [prev[e["a"]] for e in edges if e["b"] == i and e["a"] in prev]
            return sum(ps) / len(ps) if ps else 1e9
        rows[k].sort(key=bary)
    f = font(24)
    widest = max(len(r) for r in rows)
    if horiz:
        col_w = (W - 2 * PAD) / n_layers
        box_w = min(260, col_w - 70)
    else:
        box_w = min(300, (W - 2 * PAD) / widest - 40)
    pos, size = {}, {}
    for i in ids:
        label = nodes[i]["label"]
        bw = box_w if nodes[i]["kind"] != "decision" else box_w
        th = text_h(label, f, bw - 28)
        size[i] = (bw, th + 28 + (24 if nodes[i]["kind"] == "decision" else 0))
    if horiz:
        y_gap = 40
        col_h = [sum(size[i][1] for i in r) + y_gap * (len(r) - 1) for r in rows]
        H = max(col_h) + 2 * PAD
        for k, r in enumerate(rows):
            y = PAD + (H - 2 * PAD - col_h[k]) / 2
            for i in r:
                pos[i] = (PAD + col_w * (k + 0.5), y + size[i][1] / 2)
                y += size[i][1] + y_gap
    else:
        y_gap = 70 if any(e["label"] for e in edges) else 56
        row_h = [max(size[i][1] for i in r) for r in rows]
        H = sum(row_h) + y_gap * (n_layers - 1) + 2 * PAD
        y = PAD
        for k, r in enumerate(rows):
            cw = (W - 2 * PAD) / len(r)
            for j, i in enumerate(r):
                pos[i] = (PAD + cw * (j + 0.5), y + row_h[k] / 2)
            y += row_h[k] + y_gap
    img, d = _canvas(H)

    def port(i, toward):
        (cx, cy), (bw, bh) = pos[i], size[i]
        dx, dy = toward[0] - cx, toward[1] - cy
        if dx == 0 and dy == 0:
            return cx, cy
        sx = (bw / 2) / abs(dx) if dx else 1e9
        sy = (bh / 2) / abs(dy) if dy else 1e9
        s = min(sx, sy)
        return cx + dx * s, cy + dy * s

    fl = font(20)
    for e in edges:
        a, b = pos[e["a"]], pos[e["b"]]
        if (e["a"], e["b"]) in back or e["a"] == e["b"]:
            # route a back edge around the outside
            (ax, ay), (bx, by) = a, b
            if horiz:
                yy = H - 10
                pts = [(ax, ay + size[e["a"]][1] / 2), (ax, yy), (bx, yy)]
                end = (bx, by + size[e["b"]][1] / 2)
            else:
                xx = W - 12 if ax > W / 2 or bx > W / 2 else 12
                ox = ax + (size[e["a"]][0] / 2 if xx > ax else -size[e["a"]][0] / 2)
                pts = [(ox, ay), (xx, ay), (xx, by)]
                end = (bx + (size[e["b"]][0] / 2 if xx > bx else -size[e["b"]][0] / 2), by)
            d.line(pts, fill=MID, width=3)
            arrow(d, pts[-1], end, fill=MID, dashed=False)
            mid = pts[1]
        else:
            p, q = port(e["a"], b), port(e["b"], a)
            if e["arrow"]:
                arrow(d, p, q, dashed=e["dashed"])
            else:
                d.line([p, q], fill=INK, width=3)
            mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        if e["label"]:
            lw = min(220, _tw(e["label"], fl) + 12)
            lh = text_h(e["label"], fl, lw)
            d.rectangle([mid[0] - lw / 2 - 4, mid[1] - lh / 2 - 2, mid[0] + lw / 2 + 4, mid[1] + lh / 2 + 2], fill=PAPER)
            text_block(d, mid[0], mid[1] - lh / 2, e["label"], fl, lw, fill=INK)
    for i in ids:
        (cx, cy), (bw, bh) = pos[i], size[i]
        box = [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2]
        k = nodes[i]["kind"]
        if k == "decision":
            d.polygon([(cx, box[1]), (box[2], cy), (cx, box[3]), (box[0], cy)], fill=PALE + 25, outline=INK, width=3)
        elif k == "round":
            d.rounded_rectangle(box, radius=bh / 2, fill=PALE, outline=INK, width=3)
        else:
            d.rounded_rectangle(box, radius=10, fill=PAPER, outline=INK, width=3)
        th = text_h(nodes[i]["label"], f, bw - 28)
        text_block(d, cx, cy - th / 2, nodes[i]["label"], f, bw - 28)
    return img


# -- cycle -------------------------------------------------------------------
def draw_cycle(fig):
    steps = [s if isinstance(s, list) else [s, ""] for s in fig["steps"]]
    n = len(steps)
    f, fl = font(24), font(20)
    bw = 250 if n <= 6 else 210
    R = 300 if n > 4 else 260
    H = 2 * R + 220
    cx, cy = W / 2, H / 2
    img, d = _canvas(H)
    centers, sizes = [], []
    for k, (label, _) in enumerate(steps):
        a = -math.pi / 2 + 2 * math.pi * k / n
        centers.append((cx + R * 1.25 * math.cos(a), cy + R * math.sin(a)))
        sizes.append((bw, text_h(label, f, bw - 24) + 24))
    for k, (_, lab) in enumerate(steps):
        a0 = -math.pi / 2 + 2 * math.pi * k / n
        a1 = -math.pi / 2 + 2 * math.pi * (k + 1) / n
        gap = min(0.4, max(0.16, (bw / 2 + 18) / (R * 1.25) / (2 * math.pi / n) * 0.85))
        pts = [(cx + R * 1.25 * math.cos(a0 + (a1 - a0) * t), cy + R * math.sin(a0 + (a1 - a0) * t))
               for t in [gap + (1 - 2 * gap) * j / 12 for j in range(13)]]
        d.line(pts[:-1], fill=INK, width=3)
        arrow(d, pts[-2], pts[-1])
        if lab:
            m = pts[6]
            ox, oy = (m[0] - cx) * 0.18, (m[1] - cy) * 0.18
            th = text_h(lab, fl, 200)
            text_block(d, m[0] + ox, m[1] + oy - th / 2, lab, fl, 200, fill=MID)
    for (x, y), (w, h), (label, _) in zip(centers, sizes, steps):
        d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=14, fill=PAPER, outline=INK, width=3)
        text_block(d, x, y - h / 2 + 12, label, f, w - 24)
    if fig.get("center"):
        th = text_h(fig["center"], font(26, True), 260)
        text_block(d, cx, cy - th / 2, fig["center"], font(26, True), 260, fill=MID)
    return img


# -- layers ------------------------------------------------------------------
def draw_layers(fig):
    layers = [l if isinstance(l, list) else [l, ""] for l in fig["layers"]]
    fn, fd = font(26, True), font(22)
    name_w, note_w = 260, W - 2 * PAD - 260 - 40
    hs = [max(70, text_h(note or " ", fd, note_w) + 28, text_h(name, fn, name_w - 20) + 28) for name, note in layers]
    top_lab = fig.get("top")
    bot_lab = fig.get("bottom")
    H = sum(hs) + 2 * PAD + (40 if top_lab else 0) + (40 if bot_lab else 0)
    img, d = _canvas(H)
    y = PAD
    if top_lab:
        text_block(d, PAD, y, top_lab, font(20), W, fill=MID, align="left")
        y += 40
    shades = [PAPER, 235, 215, 195, 175, 235, 215, 195]
    for k, ((name, note), h) in enumerate(zip(layers, hs)):
        x0, x1 = PAD, PAD + name_w
        d.rectangle([x0, y, x1, y + h], fill=shades[k % len(shades)], outline=INK, width=3)
        # a light texture so neighbouring layers differ on a two-tone screen
        if k % 3 == 1:
            for xx in range(int(x0) + 8, int(x1), 22):
                for yy in range(int(y) + 8, int(y + h) - 4, 22):
                    d.ellipse([xx, yy, xx + 4, yy + 4], fill=MID)
        elif k % 3 == 2:
            for xx in range(int(x0) - int(h), int(x1), 20):
                d.line([(max(x0, xx), y + max(0, x0 - xx)), (min(x1, xx + h), y + h - max(0, xx + h - x1))],
                       fill=170, width=2)
        th = text_h(name, fn, name_w - 30)
        tw = max(_tw(ln, fn) for ln in wrap(name, fn, name_w - 30))
        cxn = (x0 + x1) / 2
        d.rectangle([cxn - tw / 2 - 6, y + h / 2 - th / 2 - 3, cxn + tw / 2 + 6, y + h / 2 + th / 2 + 3], fill=PAPER)
        text_block(d, cxn, y + h / 2 - th / 2, name, fn, name_w - 30)
        if note:
            nh = text_h(note, fd, note_w)
            text_block(d, x1 + 30, y + h / 2 - nh / 2, note, fd, note_w, align="left")
        d.line([(x1, y + h), (W - PAD, y + h)], fill=PALE, width=2)
        y += h
    if bot_lab:
        text_block(d, PAD, y + 10, bot_lab, font(20), W, fill=MID, align="left")
    return img


# -- scale -------------------------------------------------------------------
def draw_scale(fig):
    log = fig.get("log")
    marks = [list(m) for m in fig.get("marks") or []]
    ranges = [list(r) for r in fig.get("ranges") or []]
    vals = [m[0] for m in marks] + [v for r in ranges for v in r[:2]]
    lo, hi = min(vals), max(vals)
    if log:
        lo, hi = math.log10(lo), math.log10(hi)
    if hi == lo:
        hi = lo + 1
    span = hi - lo
    lo, hi = lo - span * 0.04, hi + span * 0.04
    x0, x1 = PAD + 30, W - PAD - 30

    def X(v):
        v = math.log10(v) if log else v
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    f, fl = font(22), font(24, True)
    img, d = _canvas(2000)
    y = PAD + 10
    if fig.get("ends"):
        d.text((x0, y), fig["ends"][0], font=font(20), fill=MID)
        d.text((x1 - _tw(fig["ends"][1], font(20)), y), fig["ends"][1], font=font(20), fill=MID)
        y += 34
    # ranges as stacked bands above the axis
    rows = []
    for r in sorted(ranges, key=lambda r: X(r[0])):
        a, b = X(r[0]), X(r[1])
        lw = _tw(r[2], f) + 16
        row = next((k for k, end in enumerate(rows) if end < a - 4), None)
        if row is None:
            rows.append(0)
            row = len(rows) - 1
        rows[row] = max(b, a + lw)
        r.append(row)
    band_h = 50
    for r in ranges:
        a, b, row = X(r[0]), X(r[1]), r[3]
        yy = y + row * (band_h + 8)
        shade = (235, 205, 180)[row % 3]
        d.rectangle([a, yy, b, yy + band_h], fill=shade, outline=INK, width=2)
        label = r[2]
        tw = _tw(label, f)
        lx = (a + b) / 2 - tw / 2 if tw < b - a - 8 else a + 4
        d.text((lx, yy + 12), label, font=f, fill=INK)
    y += len(rows) * (band_h + 8) + (10 if rows else 0)
    ay = y + 20
    d.line([(x0, ay), (x1, ay)], fill=INK, width=4)
    ticks = sorted(set([r[0] for r in ranges] + [r[1] for r in ranges] + [m[0] for m in marks]))
    for v in ticks:
        d.line([(X(v), ay - 10), (X(v), ay + 10)], fill=INK, width=3)
    # tick values, skipping ones that would collide
    last = -1e9
    for v in ticks:
        t = _fmt(v)
        tx = X(v) - _tw(t, f) / 2
        if tx > last + 6:
            d.text((tx, ay + 16), t, font=f, fill=MID)
            last = tx + _tw(t, f)
    y = ay + 52
    if fig.get("axis"):
        text_block(d, W / 2, y, fig["axis"] + (" (log scale)" if log else ""), font(20), W - 2 * PAD, fill=MID)
        y += 34
    # point marks below, staggered so labels never overlap
    lanes = []
    for v, label in sorted(marks, key=lambda m: X(m[0])):
        x = X(v)
        lines = wrap(label, f, 220)
        w = max(_tw(ln, f) for ln in lines)
        left = min(max(PAD, x - w / 2), W - PAD - w)
        lane = next((k for k, end in enumerate(lanes) if end < left - 10), None)
        if lane is None:
            lanes.append(0)
            lane = len(lanes) - 1
        lanes[lane] = left + w
        ly = y + 8 + lane * 70
        d.line([(x, y - 4), (x, ly)], fill=PALE - 40, width=2)
        d.ellipse([x - 6, ay - 6, x + 6, ay + 6], fill=INK)
        for k, ln in enumerate(lines):
            d.text((left, ly + k * _lh(f)), ln, font=f, fill=INK)
    H = y + (len(lanes) * 70 + 20 if lanes else 0) + PAD
    return img.crop((0, 0, W, int(H)))


# -- bar ---------------------------------------------------------------------
def draw_bar(fig):
    bars = fig["bars"]
    f, fv = font(22), font(22, True)
    label_w = min(360, max(_tw(str(b[0]), f) for b in bars) + 20)
    x0 = PAD + label_w
    x1 = W - PAD - 120
    top = max(b[1] for b in bars) or 1
    bh, gap = 40, 18
    hs = [max(bh, text_h(str(b[0]), f, label_w - 16)) for b in bars]
    H = sum(hs) + gap * len(bars) + 2 * PAD + (40 if fig.get("unit") else 0)
    img, d = _canvas(H)
    y = PAD
    for (label, v), h in zip(bars, hs):
        th = text_h(str(label), f, label_w - 16)
        for k, ln in enumerate(wrap(str(label), f, label_w - 16)):
            d.text((x0 - 12 - _tw(ln, f), y + h / 2 - th / 2 + k * _lh(f)), ln, font=f, fill=INK)
        bw = (x1 - x0) * v / top
        d.rectangle([x0, y + h / 2 - bh / 2, x0 + max(2, bw), y + h / 2 + bh / 2], fill=MID + 40, outline=INK, width=2)
        d.text((x0 + bw + 10, y + h / 2 - 13), _fmt(v), font=fv, fill=INK)
        y += h + gap
    d.line([(x0, PAD - 6), (x0, y - gap + 6)], fill=INK, width=3)
    if fig.get("unit"):
        text_block(d, (x0 + x1) / 2, y + 4, fig["unit"], font(20), x1 - x0, fill=MID)
    return img


# -- tree --------------------------------------------------------------------
def draw_tree(fig):
    """A hierarchy as an indented outline with connector lines: reads on a narrow screen at any depth."""
    f, fb = font(24), font(26, True)
    rows = []

    def walk(label, kids, depth):
        rows.append((label, depth))
        for k, v in (kids or {}).items():
            walk(k, v, depth + 1)
    walk(fig["root"], fig.get("children"), 0)
    ind, line_h = 54, 0
    hs = [text_h(l, fb if dep == 0 else f, W - 2 * PAD - 40 - dep * ind) + 18 for l, dep in rows]
    H = sum(hs) + 2 * PAD
    img, d = _canvas(H)
    y, ys = PAD, []
    for (label, dep), h in zip(rows, hs):
        x = PAD + dep * ind
        ys.append((x, y + _lh(f) / 2 + 4, dep))
        if dep:
            d.line([(x - ind + 6, y + _lh(f) / 2 + 4), (x, y + _lh(f) / 2 + 4)], fill=INK, width=2)
        d.ellipse([x, y + _lh(f) / 2 - 2, x + 12, y + _lh(f) / 2 + 10], fill=INK if dep < 2 else PAPER, outline=INK, width=2)
        text_block(d, x + 22, y, label, fb if dep == 0 else f, W - 2 * PAD - 40 - dep * ind, align="left")
        y += h
    # vertical connectors from each parent to its last child
    for k, (x, yy, dep) in enumerate(ys):
        last = None
        for j in range(k + 1, len(ys)):
            if ys[j][2] <= dep:
                break
            if ys[j][2] == dep + 1:
                last = ys[j][1]
        if last:
            d.line([(x + 6, yy + 6), (x + 6, last)], fill=INK, width=2)
    return img


DRAW = {"flow": draw_flow, "cycle": draw_cycle, "layers": draw_layers, "scale": draw_scale, "bar": draw_bar,
        "tree": draw_tree}


def png(fig):
    img = DRAW[fig["type"]](fig)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def table_html(fig):
    head = "".join(f"<th>{escape(str(h))}</th>" for h in fig.get("header") or [])
    rows = "".join("<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in r) + "</tr>" for r in fig["rows"])
    return (f'<table class="fig">{"<thead><tr>" + head + "</tr></thead>" if head else ""}<tbody>{rows}</tbody>'
            "</table>")


def key(fig):
    return hashlib.sha1(json.dumps(fig, sort_keys=True).encode()).hexdigest()[:12]


def load(subject):
    p = subject.dir / "figures.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def numbers(fig):
    """Every number a figure states, for write check."""
    from .check import nums
    skip = {"type", "sent_ids", "log", "mermaid"}
    txt = []

    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                txt.append(str(k))
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            txt.append(_fmt(v))
        elif v is not None:
            txt.append(str(v))
    for k, v in fig.items():
        if k not in skip:
            walk(v)
    if fig.get("mermaid"):   # labels only, not node ids
        txt += re.findall(r"[\[\(\{|]+([^\]\)\}|]*)[\]\)\}|]", fig["mermaid"])
    return nums(" ".join(txt))


def validate(fig):
    """Problems with one figure's shape (empty when it draws)."""
    t = fig.get("type")
    if t not in TYPES:
        return [f"unknown figure type {t!r}"]
    out = []
    if not fig.get("caption"):
        out.append("no caption")
    if not fig.get("sent_ids"):
        out.append("no sent_ids")
    try:
        if t == "table":
            if not fig.get("rows"):
                out.append("table has no rows")
        else:
            png(fig)
    except Exception as ex:  # noqa: BLE001
        out.append(f"does not draw: {ex}")
    return out


def figures_html(figs, sink, eid):
    out = []
    for k, fig in enumerate(figs):
        cap = f"<figcaption>{escape(fig.get('caption') or '')}</figcaption>"
        if fig["type"] == "table":
            out.append(f'<figure class="fig">{cap}{table_html(fig)}</figure>')
            continue
        href = sink(fig, eid, k)
        if href:
            alt = fig.get("alt") or fig.get("caption") or ""
            out.append(f'<figure class="fig"><img src="{href}" alt="{escape(alt)}"/>{cap}</figure>')
    return "".join(out)


class Sink:
    """Draws figures into a book on demand and returns their hrefs."""

    def __init__(self, book):
        self.book, self.added = book, {}

    def __call__(self, fig, eid, k):
        h = key(fig)
        if h not in self.added:
            href = f"figures/{eid}-{k + 1}.png"
            self.book.add(f"fig{len(self.added) + 1}", href, "image/png", png(fig))
            self.added[h] = href
        return self.added[h]


def preview(subject, out_dir, ids=None, log=print):
    """Draw every figure (or those of `ids`) to PNG files, to look at before publishing."""
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for eid, figs in load(subject).items():
        if ids and eid not in ids:
            continue
        for k, fig in enumerate(figs):
            if fig["type"] == "table":
                continue
            (out_dir / f"{eid}-{k + 1}.png").write_bytes(png(fig))
            n += 1
    log(f"[figures] {n} drawn to {out_dir}")
