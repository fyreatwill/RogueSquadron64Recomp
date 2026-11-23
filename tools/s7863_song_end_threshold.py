#!/usr/bin/env python3
"""s7863 G3 g3-audio-clock-sign: does an audio-ended song end on the SAME AI-buffer count in two arms?

runAiAudioStreamPlaybackLoop queues every AI buffer with a1 = 0x300 (immediate in the delay slot of both
osAiSetNextBuffer calls, 0x8008EE08 / 0x8008EE84), so buffer length cannot differ between arms (H-buflen dead by
construction). The remaining question is whether the song ends after the same number of buffers (same samples:
the per-tick split is AI-delivery phase, timing class) or after a different number (H-rate: the port synthesises a
different amount per buffer).

Model: song k starts on the tick s where the handle 0x8010C0E0 becomes k and ends on the first later tick e where
it changes again. c(v) = AI buffers queued at VIs <= v since VI tv[s]. Ending first observed at tick e means the end
threshold N satisfies c(tv[e-1]) < N <= c(tv[e]). Each arm gives an interval; a non-empty intersection = one N fits
both arms (same buffer count). SLACK (default 1 buffer) widens each side for the tick-row vs AI-row order inside
one VI. An empty intersection = the arms need different buffer counts -> H-rate.

usage: s7863_song_end_threshold.py [--slack N] [--control] [NAME:ARM_A_LOG:ARM_B_LOG ...]  (none = DEFAULT_PAIRS)
       arm logs: an oracle.log (retail, detected by name) or a port *_rand.txt; .zst resolves via rs64_zopen.
--control: for every pair, also re-score with arm B's buffers thinned by 1% inside each song window (a planted
H-rate); a pair whose real verdict is SAME must turn DIFFERENT for the control to pass. Exit 0 all SAME,
1 any DIFFERENT, 2 no song windows / control failed."""
import bisect, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen  # noqa: E402

TICK, AI = "800fa730", ("8008ee08", "8008ee84")
# the three det-sweep audio-clock forks (s7862 table: 0x31=8, 14, bonus 17), used when no NAME:A:B is given
DEFAULT_PAIRS = ("b17:scratch/s7861/v17/r1/oracle.log:scratch/s7861/v17/p1_rand.txt",
                 "m9:scratch/s7852/r2/oracle.log:scratch/s7852/p3_rand.txt",
                 "m15:scratch/s7857/v14/r1/oracle.log:scratch/s7858/p4_rand.txt",
                 "m15_retail_r1r2:scratch/s7857/v14/r1/oracle.log:scratch/s7857/v14/r2/oracle.log")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    retail = "oracle" in os.path.basename(path)
    tick, tv, bv, song = -1, [], [], []
    with zopen(path) as fh:
        for l in fh:
            f = l.split()
            if retail:
                if not l.startswith("[xtrace] ") or len(f) < 6 or not f[5].startswith("pc="):
                    continue
                f = [f[1], f[2], f[5][3:]]
            if len(f) < 3:
                continue
            try:
                vi = int(f[1])
            except ValueError:
                continue
            pc = f[2]
            if pc == TICK:
                tick += 1
                tv.append(vi)
                i = l.find(" m=8010c0e0:")
                if i >= 0:
                    song.append((tick, l[i + 12:].split()[0].split("[")[0]))
            elif pc in AI:
                bv.append(vi)
    bv.sort()
    return tv, bv, song


def windows(tv, song):
    ch = [(t, v) for (t, v), (_, v0) in zip(song[1:], song) if v != v0]
    out = []
    for (s, v), (e, _) in zip(ch, ch[1:]):
        if v in ("00000000", "ffffffff") or e >= len(tv) or e - s < 30:
            continue
        out.append((v, s, e))
    return out


def interval(tv, bv, s, e, slack):
    b0 = bisect.bisect_right(bv, tv[s])
    lo = bisect.bisect_right(bv, tv[e - 1]) - b0
    hi = bisect.bisect_right(bv, tv[e]) - b0
    return lo + 1 - slack, hi + slack


def thin(bv, tv, s, e):
    lo, hi = tv[s], tv[e]
    inside = [v for v in bv if lo < v <= hi]
    drop = set(inside[::100])
    return [v for v in bv if not (lo < v <= hi and v in drop)] if drop else bv


def score(name, A, B, slack, planted=False):
    res = []
    wa, wb = windows(A[0], A[2]), windows(B[0], B[2])
    for (va, sa, ea), (vb, sb, eb) in zip(wa, wb):
        if va != vb or sa != sb:
            res.append((name, va, None, f"misaligned A {va} t{sa} / B {vb} t{sb}"))
            continue
        bvb = thin(B[1], B[0], sb, eb) if planted else B[1]
        ia, ib = interval(A[0], A[1], sa, ea, slack), interval(B[0], bvb, sb, eb, slack)
        lo, hi = max(ia[0], ib[0]), min(ia[1], ib[1])
        same = lo <= hi
        res.append((name, va, same, f"t{sa}: end A t{ea} N in [{ia[0]},{ia[1]}]  B t{eb} N in [{ib[0]},{ib[1]}]"
                    f"  -> {'SAME N=' + str(lo) + '..' + str(hi) if same else 'DIFFERENT'}"
                    f"{'  (tick split)' if ea != eb else ''}"))
    return res


def main():
    a = sys.argv[1:]
    slack, control = 1, False
    if "--slack" in a:
        i = a.index("--slack"); slack = int(a[i + 1]); del a[i:i + 2]
    if "--control" in a:
        control = True; a.remove("--control")
    if "-h" in a or "--help" in a:
        sys.exit(__doc__)
    if not a:
        os.chdir(ROOT)
        a = list(DEFAULT_PAIRS)
    anydiff, n, ctl_ok = False, 0, True
    for spec in a:
        name, pa, pb = spec.split(":", 2)
        A, B = load(pa), load(pb)
        for nm, v, same, txt in score(name, A, B, slack):
            print(f"{nm} song {v[-2:]} {txt}")
            if same is not None:
                n += 1
                anydiff |= not same
        if control:
            for nm, v, same, txt in score(name, A, B, slack, planted=True):
                if same is None:
                    continue
                if same:
                    ctl_ok = False
                print(f"  CONTROL {nm} song {v[-2:]} planted -1% B: {'caught' if not same else 'MISSED'}")
    if not n:
        print("NO-VERDICT: no song windows"); sys.exit(2)
    if control:
        print("CONTROL", "PASS" if ctl_ok else "FAIL")
        if not ctl_ok:
            sys.exit(2)
    print("VERDICT", "DIFFERENT (H-rate)" if anydiff else f"SAME buffer count in all {n} song windows (timing class)")
    sys.exit(1 if anydiff else 0)


main()
