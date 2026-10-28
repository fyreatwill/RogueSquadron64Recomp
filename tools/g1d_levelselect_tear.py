#!/usr/bin/env python3
"""s6611: classify the 21:9 level-select tear from existing framebuffer dumps.

Per row, record the column of the strongest horizontal luma step (mean of
HALF pixels on each side) and whether that column is stable down the frame.

  H-stride    That column moves linearly with y, and slope * bpp (2) equals
              a 1024-vs-640 or 1024-vs-512 stride (slope 384 or 512 px/row).
              The clean flight frame must not.
  H-composite One y-band has a stable step, and one side — or the gap between
              a step pair — is 512 or 640 wide. Outside that band the same
              column is quiet.
  none        Neither. A torn frame that scores none is a blind step metric;
              the row inspection below is what the rows actually do.

Positive control, same process: paste a 200-row 640-wide block from the
lower part of the flight frame into its middle. That must score H-composite.
The untouched flight frame must score none.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import g3c_horizon_score as g

HALF = 4
MIN_MAG = 28.0
MIN_RUN = 80
MAX_BAND_FRAC = 0.80
SEAM_MIN = 10.0
NARROW = (512, 640)
NARROW_TOL = 16
STRIDE_SLOPES = (384, -384, 512, -512)
STRIDE_R_MIN = 0.90
BPP = 2


def luma_rows(w, h, px):
    out = [None] * h
    for y in range(h):
        base = y * w * 3
        row = bytearray(w)
        for x in range(w):
            i = base + 3 * x
            row[x] = (px[i] * 2 + px[i + 1] * 5 + px[i + 2]) // 8
        out[y] = row
    return out


def load_rows(path):
    w, h, px = g.load(path)
    if len(px) < w * h * 3:
        raise SystemExit(f"{path}: short PPM {len(px)} < {w * h * 3}")
    return w, h, luma_rows(w, h, px)


def row_steps(rows, w):
    xs, mags = [], []
    for row in rows:
        pref = [0] * (w + 1)
        s = 0
        for x, v in enumerate(row):
            s += v
            pref[x + 1] = s
        best_x, best = 0, -1.0
        for x in range(HALF, w - HALF):
            left = (pref[x] - pref[x - HALF]) / HALF
            right = (pref[x + HALF] - pref[x]) / HALF
            mag = abs(left - right)
            if mag > best:
                best, best_x = mag, x
        xs.append(best_x)
        mags.append(best)
    return xs, mags


def grad_columns(rows, w, h):
    """g[x][y] = windowed horizontal step at x. x is stored sparsely: every pixel."""
    # Store as list per x would be huge to build naively. Compute per y a full grad row.
    grad = [None] * h
    for y, row in enumerate(rows):
        pref = [0] * (w + 1)
        s = 0
        for x, v in enumerate(row):
            s += v
            pref[x + 1] = s
        g = [0.0] * w
        for x in range(HALF, w - HALF):
            left = (pref[x] - pref[x - HALF]) / HALF
            right = (pref[x + HALF] - pref[x]) / HALF
            g[x] = abs(left - right)
        grad[y] = g
    return grad


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return 0.0
    return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def near_narrow(width):
    return any(abs(width - n) <= NARROW_TOL for n in NARROW)


def circular_R(xs, mags, slope, w):
    strong = [y for y, m in enumerate(mags) if m >= MIN_MAG]
    if len(strong) < 40:
        return 0.0, len(strong)
    ang = [((xs[y] - slope * y) % w) / w * 2 * math.pi for y in strong]
    c = sum(math.cos(a) for a in ang) / len(ang)
    s = sum(math.sin(a) for a in ang) / len(ang)
    return math.hypot(c, s), len(strong)


def linear_fit(xs, mags):
    pts = [(y, xs[y]) for y, m in enumerate(mags) if m >= MIN_MAG]
    n = len(pts)
    if n < 40:
        return 0.0, 0.0, n
    my = sum(p[0] for p in pts) / n
    mx = sum(p[1] for p in pts) / n
    var_y = sum((p[0] - my) ** 2 for p in pts)
    var_x = sum((p[1] - mx) ** 2 for p in pts)
    cov = sum((p[0] - my) * (p[1] - mx) for p in pts)
    if var_y < 1 or var_x < 1:
        return 0.0, 0.0, n
    return cov / var_y, (cov * cov) / (var_y * var_x), n


def stride_class(xs, mags, w):
    best_R, best_s = 0.0, 0
    for s in STRIDE_SLOPES:
        R, _ = circular_R(xs, mags, s, w)
        if R > best_R:
            best_R, best_s = R, s
    hit = best_R >= STRIDE_R_MIN and any(abs(abs(best_s) - s) <= 8 for s in (384, 512))
    return hit, best_s, best_R


def composite_bands(grad, w, h):
    """Stable columns whose run median clears SEAM_MIN and matches 512 or 640."""
    hits = []
    # Every pixel is cheap enough at 1024x444.
    for x in range(HALF + 24, w - HALF - 24):
        col = [grad[y][x] for y in range(h)]
        y = 0
        while y < h:
            if col[y] < SEAM_MIN:
                y += 1
                continue
            y1 = y + 1
            while y1 < h and col[y1] >= SEAM_MIN:
                y1 += 1
            length = y1 - y
            if MIN_RUN <= length <= MAX_BAND_FRAC * h:
                inside = median(col[y:y1])
                outside_vals = col[:y] + col[y1:]
                outside = median(outside_vals) if outside_vals else inside
                side = median(grad[yy][x - 24] for yy in range(y, y1))
                side2 = median(grad[yy][x + 24] for yy in range(y, y1))
                peak = inside >= 1.8 * max(side, side2, 0.5)
                widths = [x, w - x]
                # pair: look for another strong column ~512 or ~640 away, same rows
                matched = [wd for wd in widths if near_narrow(wd)]
                if not matched:
                    for delta in (512, 640, -512, -640):
                        x2 = x + delta
                        if HALF < x2 < w - HALF and near_narrow(abs(delta)):
                            other = median(grad[yy][x2] for yy in range(y, y1))
                            if other >= SEAM_MIN:
                                matched.append(abs(delta))
                                break
                if matched and peak and outside <= 0.5 * inside:
                    hits.append({
                        "y0": y, "y1": y1, "x": x, "median": round(inside, 2),
                        "outside": round(outside, 2), "matched": matched,
                    })
            y = y1 if y1 > y else y + 1
    # Keep the strongest median per frame, not every adjacent x.
    hits.sort(key=lambda h_: -h_["median"])
    kept = []
    for h_ in hits:
        if any(abs(h_["x"] - k["x"]) <= 8 and abs(h_["y0"] - k["y0"]) <= 8 for k in kept):
            continue
        kept.append(h_)
        if len(kept) == 4:
            break
    return kept


def paste_block(rows, w, h):
    """200-row, 640-wide block from the lower frame, written into the middle.

    Vertically centered. Horizontally left-aligned so the cut sits at x=640,
    which is the narrower-buffer width the composite test is looking for.
    Source rows are the lower terrain, so the cut is terrain against sky.
    """
    out = [bytearray(r) for r in rows]
    bh, bw = 200, 640
    y0 = (h - bh) // 2
    src0 = h - bh
    for i in range(bh):
        out[y0 + i][0:bw] = rows[src0 + i][0:bw]
    return out, y0, y0 + bh, 0


def row_inspection(rows, w, h):
    """What the rows do when the step column is blind.

    Outer thirds only (the center is the level-select ring on both aspects).
    The score is the 70-row window with the largest mean |row-row| luma.
    A framebuffer stride of 1024-vs-640 or 1024-vs-512 would align that
    window at shift 384 or 512 better than at shift 0.
    """
    spans = ((16, w // 3), (2 * w // 3, w - 16))
    dy = [0.0] * h
    for y in range(1, h):
        a, b = rows[y], rows[y - 1]
        acc = n = 0
        for x0, x1 in spans:
            for x in range(x0, x1, 2):
                acc += abs(int(a[x]) - int(b[x]))
                n += 1
        dy[y] = acc / n if n else 0.0
    length = 70
    best = None
    if h > length + 2:
        for y0 in range(1, h - length):
            mean = sum(dy[y0:y0 + length]) / length
            if best is None or mean > best[0]:
                best = (mean, y0, y0 + length)
    quiet = None
    for y0 in range(1, max(2, h // 2 - length)):
        mean = sum(dy[y0:y0 + length]) / length
        if quiet is None or mean < quiet[0]:
            quiet = (mean, y0)
    report = {
        "side_dy70": None if best is None else {
            "y0": best[1], "y1": best[2], "dy": round(best[0], 2),
        },
        "quiet_dy70": None if quiet is None else {"y0": quiet[1], "dy": round(quiet[0], 2)},
    }
    if best is None:
        return report
    y0, y1 = best[1], best[2]

    def region(x0, x1):
        acc = n = 0
        for y in range(y0, y1):
            a, b = rows[y], rows[y - 1]
            for x in range(x0, x1, 2):
                acc += abs(int(a[x]) - int(b[x]))
                n += 1
        return round(acc / n, 2) if n else 0.0

    report["side_dy70"]["L"] = region(16, w // 3)
    report["side_dy70"]["C"] = region(w // 3, 2 * w // 3)
    report["side_dy70"]["R"] = region(2 * w // 3, w - 16)
    shifts = [0, 1, -1, 384, -384, 512, -512]
    ranked = []
    for s in shifts:
        acc = n = 0
        for y in range(y0, y1):
            a, b = rows[y], rows[y - 1]
            for x in range(max(16, -s), min(w - 16, w - s)):
                acc += abs(int(a[x]) - int(b[x + s]))
                n += 1
        ranked.append({"shift": s, "sad": round(acc / n, 2) if n else None})
    ranked.sort(key=lambda r: r["sad"])
    report["shifts"] = ranked
    return report


def classify(rows, w, h):
    xs, mags = row_steps(rows, w)
    slope, r2, n_strong = linear_fit(xs, mags)
    is_stride, s_slope, s_R = stride_class(xs, mags, w)
    grad = grad_columns(rows, w, h)
    bands = [] if is_stride else composite_bands(grad, w, h)
    if is_stride:
        label = "H-stride"
    elif bands:
        label = "H-composite"
    else:
        label = "none"
    info = {
        "label": label,
        "n_strong": n_strong,
        "lin_slope": round(slope, 3),
        "lin_r2": round(r2, 3),
        "stride_slope": s_slope,
        "stride_R": round(s_R, 3),
        "stride_bytes": s_slope * BPP,
        "bands": bands,
        "rows": row_inspection(rows, w, h),
        "step_every_20": [{"y": y, "x": xs[y], "mag": round(mags[y], 1)} for y in range(0, h, 20)],
    }
    return label, info


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frames = [
        ("ls1400", "scratch/agent/s6610_hud_anchor/wide21/fbd/fb_0001400_w1024.ppm"),
        ("ls1500", "scratch/agent/s6610_hud_anchor/wide21/fbd/fb_0001500_w1024.ppm"),
        ("ls1600", "scratch/agent/s6610_hud_anchor/wide21/fbd/fb_0001600_w1024.ppm"),
        ("flight", "scratch/agent/s6610_hud_anchor/wide21/fbd/fb_0002500_w1024.ppm"),
        ("ls16", "scratch/agent/s6608_capture_bounds/wide16/fbd/fb_0001400_w796.ppm"),
    ]
    out = {}
    flight_rows = None
    for name, rel in frames:
        w, h, rows = load_rows(os.path.join(root, rel))
        label, info = classify(rows, w, h)
        info["w"], info["h"] = w, h
        out[name] = info
        if name == "flight":
            flight_rows = (rows, w, h)
        print(f"{name} {w}x{h} {label} stride_R={info['stride_R']} slope={info['stride_slope']} "
              f"bands={info['bands']} rows={info['rows'].get('side_dy70')} shifts={info['rows'].get('shifts')}")

    rows, w, h = flight_rows
    pasted, y0, y1, x0 = paste_block(rows, w, h)
    label, info = classify(pasted, w, h)
    info["w"], info["h"] = w, h
    info["paste"] = {"y0": y0, "y1": y1, "x0": x0, "bw": 640, "bh": 200}
    out["synthetic"] = info
    print(f"synthetic {label} paste y={y0}..{y1} x0={x0} bands={info['bands']}")

    ok_flight = out["flight"]["label"] == "none"
    ok_synth = out["synthetic"]["label"] == "H-composite"
    torn = [out[n]["label"] for n in ("ls1400", "ls1500", "ls1600")]
    print("CONTROL flight", out["flight"]["label"], "PASS" if ok_flight else "FAIL")
    print("CONTROL synthetic", label, "PASS" if ok_synth else "FAIL")
    verdict = "control-failed"
    if ok_flight and ok_synth:
        if all(t == "none" for t in torn):
            verdict = "step-metric-blind"
        elif len(set(torn)) == 1 and torn[0] == "H-composite":
            verdict = "H-composite"
        elif len(set(torn)) == 1 and torn[0] == "H-stride":
            verdict = "H-stride"
        else:
            verdict = "mixed:" + ",".join(torn)
    print("VERDICT", verdict, "torn", torn)
    out["verdict"] = verdict
    out["torn_labels"] = torn
    dest = os.path.join(root, "scratch/agent/s6611_tear/summary.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", dest)
    return 0 if verdict != "control-failed" else 2


if __name__ == "__main__":
    sys.exit(main())
