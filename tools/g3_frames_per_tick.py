#!/usr/bin/env python3
"""s6805 G3: presented frames per sim tick in a dt-pinned retail/port pair, with the song handle (0x8010C0E0) and the
mission phase word (0x8010CA20) per tick, so a frame-counted RDP segment (g3_rdp_segments.py) can be placed on the tick
axis in both arms.
Retail: the oracle log must carry an osViSwapBuffer row (--exec-trace-also 0x80035500); a frame = one swap row, credited
to the tick row before it. Port: frame VIs from the RS64_RDP_BIN_PORT_VI cache (<port.bin>.fvi.pkl, g3_rdp_segcmp) and
tick VIs from the port rand trace; a frame is credited to the last tick whose VI <= the frame's VI.
usage: g3_frames_per_tick.py RETAIL_ORACLE_LOG PORT_RAND_TXT PORT_FVI_PKL FROM_TICK TO_TICK [STEP]
"""
import os, pickle, sys, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SWAP = os.environ.get("G3_SWAP", "80035500").lower()


def ticks(path, retail, swap):
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "g3_ai_clock.py")).read()
    ns = {"__name__": "g3_ai_clock_lib"}
    exec(src.replace("\nmain()", ""), ns)
    T, nfr = [], []  # per tick: (vi, song, phase); frames credited per tick
    for vi, pc, l in ns["rows"](path, retail):
        if pc == ns["TICK"]:
            i, j = l.find(" m=8010c0e0:"), l.find(" m=8010c9e0:")
            song = l[i + 12:].split()[0].split("[")[0] if i >= 0 else "?"
            ph = l[j + 12:].split()[0].split("[")[0].split(",")[16] if j >= 0 else "?"
            T.append((vi, song, ph)); nfr.append(0)
        elif swap and pc == swap and T:
            nfr[-1] += 1
    return T, nfr


def main():
    if len(sys.argv) < 6:
        sys.exit(__doc__)
    lo, hi = int(sys.argv[4]), int(sys.argv[5]); step = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    RT, rf = ticks(sys.argv[1], True, SWAP)
    PT, _ = ticks(sys.argv[2], False, None)
    fvi = pickle.load(open(sys.argv[3], "rb")); pvi = [v for v, _, _ in PT]; pf = [0] * len(PT)
    for v in fvi:
        k = bisect.bisect_right(pvi, v) - 1
        if 0 <= k < len(pf):
            pf[k] += 1
    rc = sum(rf[:lo]); pc = sum(pf[:lo])
    print(f"retail ticks {len(RT)} swaps {sum(rf)} | port ticks {len(PT)} frames {len(fvi)} | cum frames before t{lo}: R {rc} P {pc}")
    print("tick   R.vi  R.fr R.cum song ph |  P.vi  P.fr P.cum song ph")
    for t in range(lo, min(hi, len(RT), len(PT))):
        rc += rf[t]; pc += pf[t]
        if (t - lo) % step == 0 or RT[t][1] != RT[t - 1][1] or PT[t][1] != PT[t - 1][1] or RT[t][2] != RT[t - 1][2] or PT[t][2] != PT[t - 1][2]:
            print(f"{t:5d} {RT[t][0]:6d} {rf[t]:3d} {rc:6d} {RT[t][1][-2:]:>4} {RT[t][2][-1:]:>2} | {PT[t][0]:6d} {pf[t]:3d} {pc:6d} {PT[t][1][-2:]:>4} {PT[t][2][-1:]:>2}")


main()
