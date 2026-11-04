#!/usr/bin/env python3
"""s6865: how much of a G1 "hold" was flight? m6_god_common counts the hold from its mission gate; with a loose origin gate that is
boot, and lvl5/10 only reach [initMission] at ~185 s. Prints per run: reported hold, seconds from [initMission] to the last autopilot
fire (autopilot t is the game's run clock). Usage: tools/audit_hold_flight.py <m6 run dir>..."""
import io, pathlib, re, subprocess, sys

def lines(d):
    p = pathlib.Path(d) / "run.log"
    if p.exists():
        return p.open("rb")
    z = p.with_suffix(".log.zst")
    if z.exists():
        return io.BytesIO(subprocess.run(["zstd", "-dc", str(z)], capture_output=True).stdout)
    return None

for d in sys.argv[1:]:
    s = (pathlib.Path(d) / "summary").read_text(errors="replace") if (pathlib.Path(d) / "summary").exists() else ""
    m = re.search(r"mission_t=(\d+)s hold=(\d+)s", s)
    f = lines(d)
    if not m or f is None:
        continue
    t = 0.0; init = None
    for l in f:
        if l.startswith(b"[autopilot] fire"):
            t = float(re.search(rb"t=([0-9.]+)", l).group(1))
        elif init is None and l.startswith(b"[initMission]"):
            init = t
    fl = "none" if init is None else f"{t - init:.0f}"
    print(f"{pathlib.Path(d).name} gate_t={m[1]} hold={m[2]} init_t={init} flight_s={fl}")
