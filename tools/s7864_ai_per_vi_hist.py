#!/usr/bin/env python3
"""s7864 g3-ai-vi-clock: histogram of AI buffers queued per VI inside the mission tick span.

Reads a retail oracle.log or a port *_rand.txt (same rows as s7863_song_end_threshold.load): every AI-queue row
(osAiSetNextBuffer PCs 0x8008EE08 / 0x8008EE84) carries its VI; counts buffers per VI for every VI between the
first and last mission tick (0x800FA730), including VIs with 0 buffers.
usage: s7864_ai_per_vi_hist.py LOG [LOG ...]   prints one line per log: name, VIs, buffers, buf/VI, hist {k: n}.
--control: also plant one extra buffer every 100 VIs in each log's counts; the hist must gain a bucket >=2 more
often (or a new bucket), proving the counter sees per-VI structure. Exit 2 if the control fails."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7863_song_end_threshold import load  # noqa: E402
from rs64_zopen import resolve  # noqa: E402


def hist(tv, bv, plant=False):
    if not tv:
        return None
    lo, hi = tv[0], tv[-1]
    c = collections.Counter(v for v in bv if lo <= v <= hi)
    if plant:
        for v in range(lo, hi + 1, 100):
            c[v] += 1
    h = collections.Counter(c.get(v, 0) for v in range(lo, hi + 1))
    return hi - lo + 1, sum(c.values()), dict(sorted(h.items()))


DEFAULT = ("scratch/s7864/v17/r1/oracle.log", "scratch/s7864/v17/p1_rand.txt", "scratch/s7864/v17/p2_rand.txt")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(a):
    ctl = "--control" in a
    a = [x for x in a if x != "--control"]
    if not a:  # s7864 retained: retail {1,2}; p1 AI_VI_CLOCK=1 {1,2} (+<=1% stragglers); p2 drain-paced keeps 0 and 3
        a = [os.path.join(ROOT, x) for x in DEFAULT]
    a = [resolve(x) or x for x in a]  # s7893: retained inputs survive only as .zst (scratch retention); load() reads via zopen
    bad = 0
    for p in a:
        tv, bv, _ = load(p)
        r = hist(tv, bv)
        if r is None:
            print(p, "no ticks"); bad = 1; continue
        n, b, h = r
        print(f"{p}: vis={n} bufs={b} buf/vi={b / n:.4f} hist={h}")
        if ctl:
            _, _, hc = hist(tv, bv, plant=True)
            ok = hc != h
            print(f"  control planted +1/100 VI: hist={hc} {'PASS' if ok else 'FAIL'}")
            bad |= 0 if ok else 2
    if not bad:
        print("VERDICT PASS" + (" (controls PASS)" if ctl else ""))
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
