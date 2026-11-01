#!/usr/bin/env python3
"""s6709 G1e: map a run's fbd dumps (fb_<VI>_w<W>.ppm, FBD_EVERY_V) to the [g1e-aq] arm active when they were taken,
and lay them out one row per arm, for the same-run render check of an ASYNC_TOGGLE / NODRAIN A/B (H-race: running the
guest ahead of RT64 shows up as texture garbage / stale or torn frames in the as=3 row only).
VI -> second via the cumulative [g1b] vi= counts; second -> arm via [g1e-aq] t= as= (a second with two arms is dropped).
Per frame it also prints non-black fraction and distinct colours (cheap outlier screen).
Usage: g1e_fbd_arms.py <run_dir> <out.png> [--tmin S] [--per N]"""
import sys, os, re, glob
from PIL import Image, ImageDraw
a = sys.argv[1:]; tmin = 90; per = 5
if "--tmin" in a: i = a.index("--tmin"); tmin = int(a[i + 1]); del a[i:i + 2]
if "--per" in a: i = a.index("--per"); per = int(a[i + 1]); del a[i:i + 2]
run, out = a[0], a[1]
cum = []; arms = {}; acc = 0
for ln in open(os.path.join(run, "run.log"), errors="replace"):
    m = re.match(r"^\[g1b\] t=(\d+) vi=(\d+)", ln)
    if m: acc += int(m[2]); cum.append((acc, int(m[1]))); continue
    m = re.match(r"^\[g1e-aq\] t=(\d+) as=(\d)", ln)
    if m: arms.setdefault(int(m[1]), set()).add(int(m[2]))
def sec(vi):
    for c, t in cum:
        if vi <= c: return t
    return None
rows = {}
for f in sorted(glob.glob(os.path.join(run, "fbd", "fb_*_w*.ppm"))):
    vi = int(re.search(r"fb_(\d+)_w", f)[1]); t = sec(vi)
    if t is None or t < tmin or len(arms.get(t, ())) != 1: continue
    arm = next(iter(arms[t])); im = Image.open(f).convert("RGB")
    cols = im.getcolors(1 << 24); n = im.width * im.height; nb = 1 - sum(c for c, p in cols if p == (0, 0, 0)) / n
    print(f"as={arm} t={t:3d} vi={vi:7d} {os.path.basename(f)} nonblack={nb:.3f} colours={len(cols)}")
    rows.setdefault(arm, []).append((t, im))
CW, CH = 320, 240
names = {0: "sync", 1: "async", 2: "async drained", 3: "async no-drain"}
sheet = Image.new("RGB", (CW * per, CH * max(1, len(rows))), (40, 40, 40)); d = ImageDraw.Draw(sheet)
for r, arm in enumerate(sorted(rows)):
    for c, (t, im) in enumerate(rows[arm][:per]):
        sheet.paste(im.resize((CW, CH)), (c * CW, r * CH))
        d.text((c * CW + 4, r * CH + 4), f"as={arm} {names.get(arm, '')} t={t}", fill=(255, 255, 0))
sheet.save(out); print("wrote", out, {k: len(v) for k, v in rows.items()})
