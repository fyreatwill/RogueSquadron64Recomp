#!/usr/bin/env python3
"""Defect-specific per-phase measures for regress.sh frame bursts.

Session 24's harness caveat: distinct-colour count moves the WRONG way for a fix
that removes a corruption artifact (removing a black wedge removes its
high-contrast edge pixels). So score the defect directly instead:

  black   -- fraction of near-black pixels  (the negative-shade population)
  warm    -- fraction of orange/red-scramble pixels, the hangar floor band
             signature (#ce6238: R-B = 150)
  lum     -- mean luminance, for the "hangar is dimmer than the s11 peak" claim

Window chrome is cropped off; only the game surface is measured.
"""
import os
import re
import sys
from collections import defaultdict

from PIL import Image

PHASE_RE = re.compile(r"_p(\d+)_w(\d+)\.png$")


def measure(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # Crop window chrome: title bar is ~6% of height, thin border elsewhere.
    im = im.crop((int(w * 0.03), int(h * 0.08), int(w * 0.97), int(h * 0.98)))
    # NEAREST-downsampling to 256 wide dropped most of the band: it is made of
    # thin horizontal streaks, so an aggressive resample lands between them and
    # reported 0.75% where the defect visibly covers ~10% of the frame.
    im = im.resize((512, 400), Image.BILINEAR)
    px = list(im.getdata())
    n = len(px)
    black = warm = 0
    lum = 0.0
    for r, g, b in px:
        lum += 0.2126 * r + 0.7152 * g + 0.0722 * b
        if r < 16 and g < 16 and b < 16:
            black += 1
        # The band is warm but mostly DARK (dark red / ember streaks on black),
        # so the r>60 gate excluded it. Gate on warm HUE, not brightness.
        if r > 40 and (r - b) > 25 and (r - g) > 12:
            warm += 1
    return black / n, warm / n, lum / n


def main():
    for d in sys.argv[1:]:
        by_phase = defaultdict(list)
        for f in sorted(os.listdir(d)):
            m = PHASE_RE.search(f)
            if not m:
                continue
            by_phase[(m.group(1), m.group(2))].append(os.path.join(d, f))
        print(f"=== {d}")
        print(f"  {'phase':>12}  {'n':>4}  {'black%':>7}  {'warm%':>7}  {'lum':>6}")
        for (p, wd), files in sorted(by_phase.items()):
            bs, ws, ls = [], [], []
            for f in files:
                b, wr, l = measure(f)
                bs.append(b)
                ws.append(wr)
                ls.append(l)
            med = lambda v: sorted(v)[len(v) // 2]
            print(f"  p{p:>3} w{wd:>5}  {len(files):>4}  "
                  f"{med(bs) * 100:7.2f}  {med(ws) * 100:7.2f}  {med(ls):6.1f}")


if __name__ == "__main__":
    main()
