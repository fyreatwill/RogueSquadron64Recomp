"""Flight framebuffer class rule (s6632 sky/HUD, s6634 night, s6636 sunset, s6641 dusk).

Sky and the radar HUD are the bright-scene cuts from s6632. Terrain replaces
luma stddev with relative local edge energy so a dark ridged surface counts
and high-contrast menu art does not. Craft keeps the s6632 engine bloom and
adds a chase-camera metal hull, a saturated green reticle, a dark hull
against a bright sky, or low-chroma metal against a coloured neighbour.
A third sky arm accepts an orange sky, including the dimmer dusk.
A fourth accepts the level-10 tan cloud field.
A fifth accepts the level-17 grey trench wall.

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
    luma = sum(sm) / 3.0
    # Orange sky: R well above G and B. Level 4 clears luma 140; level 8's
    # dusk is 84..97 with the same chroma. The title reaches luma ~85, but
    # its R-G stays near 32, so the +40 gate keeps that cast out.
    # Tan clouds (level 10): R-G is 23..28, between the blue and orange
    # arms, at luma 73..104. The title photo shares that R-G (about 25..27)
    # but G stays near B (G-B about 5, R-B about 30). Clouds drop B
    # (R-B 49..61, G-B 22..33). The B gates keep the title sky false.
    rg = sm[0] - sm[1]
    rb = sm[0] - sm[2]
    gb = sm[1] - sm[2]
    # Grey trench wall (level 17 chase, n=2300). The sky window is panel
    # grey, not a starfield: mean luma is ~42 with almost no cast, and
    # 0.845 of the samples have channel spread <= 8. The level-3 dump
    # that misses dark>=0.60 (m3150) has the same mean luma (~40) but
    # only 0.613 of its samples are that neutral, so 0.80 keeps mission
    # at 11/13. Both title skies are luma ~74 with R-G ~25.
    neutral8 = sum(1 for c in sky if max(c) - min(c) <= 8) / len(sky)
    sky_ok = (
        dark >= 0.60
        or (luma >= 70 and sm[0] <= sm[1] + 15)
        or (luma >= 80 and sm[0] >= sm[1] + 40 and sm[0] >= sm[2] + 20)
        or (luma >= 70 and 20 <= rg <= 32 and rb >= 40 and gb >= 18)
        or (38 <= luma <= 55 and abs(rg) <= 8 and abs(rb) <= 8 and abs(gb) <= 8 and neutral8 >= 0.80)
    )

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
    sil_n = 0
    for c in band:
        L = _luma(c)
        ch = max(c) - min(c)
        if L >= med + 30 and ch <= 80 and L >= 40:
            metal_n += 1
        # Sunset fills the chase band, so the hull is darker than the
        # median rather than brighter. Only count that when the band
        # itself is a bright sky; a dark menu median never qualifies.
        if med >= 120 and L <= med - 50 and ch <= 90 and L >= 15:
            sil_n += 1
    metal = metal_n / len(band)
    sil = sil_n / len(band)

    rg = box(0.35, 0.65, 0.28, 0.55, 1)
    pure = sum(1 for r, g, b in rg if g >= 80 and r <= 50 and b <= 50 and g >= r + 40 and g >= b + 40) / len(rg)

    # Chase X-wing: low-chroma metal in the lower centre with a strongly
    # coloured neighbour (the desert). Flat menu grey in that box has no
    # such neighbour. Measured chase frames are 0.063..0.115; the title
    # is 0.017 and craft-select is 0.021. The side view is 0.041.
    x0e, x1e = int(w * 0.34), int(w * 0.66)
    y0e, y1e = int(h * 0.48), int(h * 0.70)
    nedge = nbox = 0
    for y in range(y0e, y1e):
        for x in range(x0e, x1e):
            c = _pix(px, w, x, y)
            L = _luma(c)
            ch = max(c) - min(c)
            nbox += 1
            if 60 <= L <= 160 and ch <= 22:
                best = 0
                for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4), (8, 0), (-8, 0)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        nc = _pix(px, w, xx, yy)
                        best = max(best, max(nc) - min(nc))
                if best >= 45:
                    nedge += 1
    edge = nedge / nbox if nbox else 0.0
    craft_ok = engines or metal >= 0.10 or pure >= 0.004 or sil >= 0.06 or edge >= 0.05

    ok = sky_ok and terr_ok and craft_ok and hud_ok
    return {
        "ok": ok, "sky": sky_ok, "terr": terr_ok, "craft": craft_ok, "hud": hud_ok,
        "rel": rel, "metal": metal, "sil": sil, "pure": pure, "pink": pink, "yel": yel,
        "radar": radar, "dark": dark, "luma": luma, "rg": sm[0] - sm[1], "edge": edge,
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
        f"rel={d['rel']:.3f} metal={d['metal']:.3f} sil={d['sil']:.3f} pure={d['pure']:.4f} edge={d['edge']:.3f} "
        f"pink={d['pink']:.4f} yel={d['yel']:.4f} radar={d['radar']:.3f} "
        f"luma={d['luma']:.1f} rg={d['rg']:.1f}{extra}"
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
