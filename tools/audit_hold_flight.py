#!/usr/bin/env python3
"""s6865: how much of a G1 "hold" was flight? m6_god_common counts the hold from its mission gate; with a loose origin gate that is
boot, and lvl5/10 only reach [initMission] at ~185 s. Prints per run: reported hold, seconds from [initMission] to the last autopilot
fire (autopilot t is the game's run clock), and s6867: inits ([initMission] lines; a relaunch adds one, so flight past the first is not one
continuous mission) and wall_s = gate_t + hold - init_t, which is not capped by the key schedule's last fire at ~520 s.
Usage: tools/audit_hold_flight.py <m6 run dir>..."""
import gzip, io, pathlib, re, subprocess, sys

def lines(d):
    p = pathlib.Path(d) / "run.log"
    if p.exists():
        return p.open("rb")
    z = p.with_suffix(".log.zst")
    if z.exists():
        return io.BytesIO(subprocess.run(["zstd", "-dc", str(z)], capture_output=True).stdout)
    g = p.with_suffix(".log.gz")  # s6867: the loop's prune gzips old runs; the audit skipped them, including every m6hold 660 s hold
    if g.exists():
        return gzip.open(g, "rb")
    return None

for d in sys.argv[1:]:
    s = (pathlib.Path(d) / "summary").read_text(errors="replace") if (pathlib.Path(d) / "summary").exists() else ""
    m = re.search(r"mission_t=(\d+)s hold=(\d+)s", s)
    f = lines(d)
    if not m or f is None:
        continue
    t = 0.0; init = None; inits = 0
    for l in f:
        if l.startswith(b"[autopilot] fire"):
            t = float(re.search(rb"t=([0-9.]+)", l).group(1))
        elif l.startswith(b"[initMission]"):
            inits += 1
            if init is None:
                init = t
    fl = "none" if init is None else f"{t - init:.0f}"
    wall = "none" if init is None else f"{int(m[1]) + int(m[2]) - init:.0f}"
    print(f"{pathlib.Path(d).name} gate_t={m[1]} hold={m[2]} init_t={init} flight_s={fl} inits={inits} wall_s={wall}")
