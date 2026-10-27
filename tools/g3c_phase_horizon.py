#!/usr/bin/env python3
"""Phase-aligned horizon profile for G3c(a). Usage: g3c_phase_horizon.py <flightW> <fbd-dir> [offsets VIs...]
Flight start = first dump of width flightW starting a run of >=30 consecutive flightW dumps.
Scores the dump nearest start+offset using g3c_horizon_score.score; also prints the
per-column horizon-row profile (16 bins, fraction of height) so arms can be eyeballed."""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from g3c_horizon_score import load, score
W = int(sys.argv[1]); root = sys.argv[2]
offs = [int(x) for x in sys.argv[3:]] or [150, 300, 600, 900, 1200, 1500]
fr = []
for p in sorted(glob.glob(os.path.join(root, "fb_*.ppm"))):
    m = re.search(r"fb_(\d+)_w(\d+)", p)
    fr.append((int(m.group(1)), int(m.group(2)), p))
# anchor = start of the FINAL uninterrupted run of width W (earlier W runs are hangar/title/other surface)
start = None
i = len(fr) - 1
while i >= 0 and fr[i][1] == W: i -= 1
start = fr[i + 1][0] if i + 1 < len(fr) else None
print("flight start VI", start, "of", len(fr), "dumps")
if start is None: sys.exit(1)
for o in offs:
    f = min((f for f in fr if f[1] == W), key=lambda f: abs(f[0] - start - o))
    w, h, px = load(f[2])
    j, ho, c = score(w, h, px)
    print("off=%d vi=%d jump=%.3f hole=%.4f cols=%d  %s" % (o, f[0], j, ho, c, f[2]))
