#!/usr/bin/env python3
"""s6755 G3: audio clock vs VI clock vs sim tick in a dt-pinned retail/port pair.
Rows used: the runInMissionFrame tick row (0x800FA730, with an XTRACE_MEM dump of the song handle word
0x8010C0E0: 800FA730:0:8010C0E0:1) and one row per AI buffer at runAiAudioStreamPlaybackLoop's osAiSetNextBuffer
calls (0x8008EE08 / 0x8008EE84; oracle --exec-trace-also, port fixup_rand_trace.py s6755 marks). Each buffer is a
fixed 0x300 bytes (192 stereo frames). Reports, per arm, the song window (handle 0 -> 1 -> 0, i.e. the lvl4 cue whose
end posts event bit 0x100 via tickSongFadeTimer) in sim ticks, VIs and AI buffers, and the buffers-per-VI rate over the
whole flight. Port [s4245] rows (ROGUESQ_S4245=1) add buffers per host wall second.
usage: g3_ai_clock.py RETAIL_ORACLE_LOG PORT_RAND_TXT [PORT_RUN_LOG]"""
import re, sys

TICK, AI = "800fa730", ("8008ee08", "8008ee84")

def rows(path, retail):
    for l in open(path, errors="replace"):
        f = l.split()
        if retail:
            if not l.startswith("[xtrace] ") or len(f) < 6 or not f[5].startswith("pc="):
                continue
            f = [f[1], f[2], f[5][3:]]  # oracle column 3 is the trace site; the executed pc is the pc= field
        if len(f) < 3:
            continue
        try:
            yield int(f[1]), f[2], l
        except ValueError:
            continue

def arm(path, retail):
    tick, ticks, bufs, song = -1, [], [], []
    for vi, pc, l in rows(path, retail):
        if pc == TICK:
            tick += 1
            ticks.append(vi)
            i = l.find(" m=8010c0e0:")
            if i >= 0:
                song.append((tick, l[i + 12:].split()[0]))
        elif pc in AI:
            bufs.append((tick, vi))
    start = next((t for (t, v), (t0, v0) in zip(song[1:], song) if v == "00000001" and v0 != "00000001"), None)
    end = next((t for t, v in song if start is not None and t > start and v != "00000001"), None)
    return ticks, bufs, start, end

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    for name, path, retail in (("retail", sys.argv[1], True), ("port", sys.argv[2], False)):
        ticks, bufs, s, e = arm(path, retail)
        print(f"== {name}: ticks {len(ticks)}  AI buffers {len(bufs)}  song start tick {s} end tick {e}")
        if not bufs or len(ticks) < 2:
            continue
        b0 = next((i for i, (t, _) in enumerate(bufs) if t >= 1), 0)
        dv = bufs[-1][1] - bufs[b0][1]
        print(f"   flight: {len(bufs) - b0} buffers over {dv} VI = {(len(bufs) - b0 - 1) / max(dv, 1):.4f} buf/VI")
        if s is not None and e is not None:
            n = sum(1 for t, _ in bufs if s <= t < e)
            v = ticks[e] - ticks[s]
            print(f"   song: {e - s} ticks  {v} VI  {n} AI buffers  ({n / max(v, 1):.4f} buf/VI, {v / (e - s):.3f} VI/tick,"
                  f" {n / (e - s):.3f} buf/tick)")
    if len(sys.argv) > 3:
        sn = [(float(m.group(1)), int(m.group(2))) for m in
              (re.search(r"\[s4245\] t=([\d.]+) .*? setnext=(\d+) ", l) for l in open(sys.argv[3], errors="replace")) if m]
        if len(sn) > 20:
            (t0, n0), (t1, n1) = sn[10], sn[-1]
            print(f"== port wall: {n1 - n0} buffers in {t1 - t0:.1f} s = {(n1 - n0) / (t1 - t0):.2f} buf/s"
                  f" ({(n1 - n0) / (t1 - t0) * 192:.0f} frames/s)")

main()
