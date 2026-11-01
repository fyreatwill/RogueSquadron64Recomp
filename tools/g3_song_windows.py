#!/usr/bin/env python3
"""s6760 G3: every song-handle (0x8010C0E0) transition in a dt-pinned retail/port pair, and per song window the sim
ticks, VIs and AI buffers in each arm. g3_ai_clock.py reports only the first song (handle 0->1->0); lvl8's split was
the third (handle 3). Equal VI/buffer counts with unequal ticks = the song ended on the audio clock, not a sim defect.
usage: g3_song_windows.py RETAIL_ORACLE_LOG PORT_RAND_TXT"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_ai_clock():
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "g3_ai_clock.py")).read()
    ns = {"__name__": "g3_ai_clock_lib"}
    exec(src.replace("\nmain()", ""), ns)
    return ns

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    ac = load_ai_clock()
    for name, path, retail in (("retail", sys.argv[1], True), ("port", sys.argv[2], False)):
        tick, ticks, bufs, song = -1, [], [], []
        for vi, pc, l in ac["rows"](path, retail):
            if pc == ac["TICK"]:
                tick += 1
                ticks.append(vi)
                i = l.find(" m=8010c0e0:")
                if i >= 0:
                    song.append((tick, l[i + 12:].split()[0]))
            elif pc in ac["AI"]:
                bufs.append((tick, vi))
        ch = [(t, v) for (t, v), (t0, v0) in zip(song[1:], song) if v != v0]
        print(f"== {name}: ticks {len(ticks)}  handle changes " + " ".join(f"t{t}:{v}" for t, v in ch))
        for (s, v), (e, _) in zip(ch, ch[1:]):
            if v in ("00000000", "ffffffff") or e >= len(ticks):
                continue
            n = sum(1 for t, _ in bufs if s <= t < e)
            dv = ticks[e] - ticks[s]
            print(f"   song {v[-2:]} t{s}-t{e}: {e - s} ticks  {dv} VI  {n} AI buffers  ({dv / (e - s):.3f} VI/tick)")

main()
