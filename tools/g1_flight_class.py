"""Flight framebuffer class rule (s6632 sky/HUD, s6634 night terrain and craft).

Sky and the radar HUD are the bright-scene cuts from s6632. Terrain replaces
luma stddev with relative local edge energy so a dark ridged surface counts
and high-contrast menu art does not. Craft keeps the s6632 engine bloom and
adds a chase-camera metal hull or a saturated green reticle.

Canonical check (no args) exits 0 only when the five-file table holds:
  pass  docs/g3_retail_lvl1_flight_oracle.png
  pass  scratch/agent/s6632_lvl2/fbd/fb_0002700_w512.ppm
  pass  scratch/agent/s6633_lvl3/fbd/fb_0002700_w512.ppm
  fail  scratch/agent/s6631_heapcap_at/wide16/fbd/fb_0001400_w796.ppm
  fail  scratch/agent/s6633_lvl3/fbd/fb_0000450_w512.ppm
It also scores the thirteen s6633 mission dumps n=2550..3150.
"""
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_any(p):
    if p.endswith(".ppm"):
        rest = open(p, "rb").read()
        nl = rest.find(b"\n") + 1
        if rest[nl:nl + 1] == b"#":
            nl = rest.find(b"\n", nl) + 1
        nl2 = rest.find(b"\n", nl)
        w, h = map(int, rest[nl:nl2].split())
        nl3 = rest.find(b"\n", nl2 + 1) + 1
        return w, h, rest[nl3:]
    from PIL import Image
    im = Image.open(p).convert("RGB")
    return im.size[0], im.size[1], im.tobytes()


def _pix(px, w, x, y):
    i = (y * w + x) * 3
    return px[i], px[i + 1], px[i + 2]


def _luma(c):
    return (c[0] + c[1] + c[2]) / 3.0


def classes(p):
    w, h, px = load_any(p)

    def box(x0, x1, y0, y1, step=2):
        pts = []
        for y in range(int(h * y0), int(h * y1), step):
            for x in range(int(w * x0), int(w * x1), step):
                pts.append(_pix(px, w, x, y))
        return pts

    sky = box(0.15, 0.85, 0.02, 0.18)
    sm = [sum(c[i] for c in sky) / len(sky) for i in range(3)]
    dark = sum(1 for c in sky if _luma(c) < 35) / len(sky)
    sky_ok = dark >= 0.60 or (sum(sm) / 3 >= 70 and sm[0] <= sm[1] + 15)

    # Relative local edge energy. Absolute stddev stays under 18 on the
    # level-3 night ground; dividing the neighbor delta by local luma
    # counts those ridges. Title and level-select art land well above 0.33.
    acc = n = 0
    step = 2
    y0, y1 = int(h * 0.45), int(h * 0.95)
    x0, x1 = int(w * 0.15), int(w * 0.85)
    for y in range(y0, y1 - step, step):
        for x in range(x0, x1 - step, step):
            L = _luma(_pix(px, w, x, y))
            d = abs(L - _luma(_pix(px, w, x + step, y))) + abs(L - _luma(_pix(px, w, x, y + step)))
            acc += d / (L + 12.0)
            n += 1
    rel = acc / n
    terr_ok = 0.08 <= rel <= 0.33

    rad = box(0.70, 0.98, 0.02, 0.32, 1)
    radar = sum(1 for r, g, b in rad if r > 140 and r > g + 50 and r > b + 50) / len(rad)
    hud_ok = radar >= 0.02

    cen = box(0.28, 0.72, 0.38, 0.75, 1)
    pink = sum(1 for r, g, b in cen if r > 170 and r > g + 40 and r > b + 30 and g < 170) / len(cen)
    yel = sum(1 for r, g, b in cen if r >= 230 and g >= 210 and 150 <= b < 230 and abs(r - g) <= 30 and (r + g) / 2 >= b + 15) / len(cen)
    engines = (0.003 <= pink <= 0.05) or (0.002 <= yel <= 0.015 and pink < 0.001)

    # Chase-camera band. A hull pixel is brighter than the band median,
    # not a saturated UI colour. The level-3 ship clears 0.10; the
    # level-select floor in the same band does not.
    ys = range(int(h * 0.40), int(h * 0.62))
    xs = range(int(w * 0.32), int(w * 0.68))
    band = [_pix(px, w, x, y) for y in ys for x in xs]
    med = statistics.median(_luma(c) for c in band)
    metal_n = 0
    for c in band:
        L = _luma(c)
        ch = max(c) - min(c)
        if L >= med + 30 and ch <= 80 and L >= 40:
            metal_n += 1
    metal = metal_n / len(band)

    rg = box(0.35, 0.65, 0.28, 0.55, 1)
    pure = sum(1 for r, g, b in rg if g >= 80 and r <= 50 and b <= 50 and g >= r + 40 and g >= b + 40) / len(rg)
    craft_ok = engines or metal >= 0.10 or pure >= 0.004

    ok = sky_ok and terr_ok and craft_ok and hud_ok
    return {
        "ok": ok, "sky": sky_ok, "terr": terr_ok, "craft": craft_ok, "hud": hud_ok,
        "rel": rel, "metal": metal, "pure": pure, "pink": pink, "yel": yel, "radar": radar,
        "dark": dark,
    }


CANON = [
    ("oracle", "docs/g3_retail_lvl1_flight_oracle.png", True),
    ("lvl2", "scratch/agent/s6632_lvl2/fbd/fb_0002700_w512.ppm", True),
    ("lvl3", "scratch/agent/s6633_lvl3/fbd/fb_0002700_w512.ppm", True),
    ("floor", "scratch/agent/s6631_heapcap_at/wide16/fbd/fb_0001400_w796.ppm", False),
    ("title", "scratch/agent/s6633_lvl3/fbd/fb_0000450_w512.ppm", False),
]


def line(name, d, want=None):
    flag = "pass" if d["ok"] else "fail"
    extra = ""
    if want is not None:
        extra = " table=OK" if d["ok"] == want else " table=BAD"
    return (
        f"{flag} {name} sky={int(d['sky'])} terr={int(d['terr'])} "
        f"craft={int(d['craft'])} hud={int(d['hud'])} "
        f"rel={d['rel']:.3f} metal={d['metal']:.3f} pure={d['pure']:.4f} "
        f"pink={d['pink']:.4f} yel={d['yel']:.4f} radar={d['radar']:.3f}{extra}"
    )


def main(argv):
    os.chdir(ROOT)
    if argv:
        bad = 0
        for p in argv:
            d = classes(p)
            print(line(p, d))
        return 0
    bad = 0
    for name, p, want in CANON:
        d = classes(p)
        print(line(name, d, want))
        bad += d["ok"] != want
    mission_pass = 0
    mission_n = 0
    for n in range(2550, 3151, 50):
        p = f"scratch/agent/s6633_lvl3/fbd/fb_{n:07d}_w512.ppm"
        d = classes(p)
        mission_n += 1
        mission_pass += bool(d["ok"])
        print(line(f"m{n}", d))
    print(f"mission {mission_pass}/{mission_n}")
    print(f"canon_bad {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
