#!/usr/bin/env python3
"""s6867: longest continuous mission per run. A hold can span relaunches (mission failed or ended, harness keys restart it), which
hold/flight_s and mission_cycles do not show; mission_cycles only counts 0x690400 -> 0x6AB400 origin changes. Segments run from one
[initMission] to the next, the last one to gate_t + hold. Times are the autopilot run clock, so an init after the key schedule ends
(~520 s) reads the last fire: such a segment is a lower bound on the one before it. Usage: tools/audit_hold_segments.py <m6 run dir>..."""
import gzip, pathlib, re, subprocess, sys

def stream(d):
    p = pathlib.Path(d) / "run.log"
    if p.exists():
        return p.open("rb")
    if p.with_suffix(".log.gz").exists():
        return gzip.open(p.with_suffix(".log.gz"), "rb")
    if p.with_suffix(".log.zst").exists():
        return subprocess.Popen(["zstd", "-dc", str(p.with_suffix(".log.zst"))], stdout=subprocess.PIPE).stdout
    return None

def segments(inits, end):
    return [b - a for a, b in zip(inits, inits[1:] + [end])]

assert segments([10.0, 40.0, 50.0], 100.0) == [30.0, 10.0, 50.0]  # control

for d in sys.argv[1:]:
    s = (pathlib.Path(d) / "summary").read_text(errors="replace") if (pathlib.Path(d) / "summary").exists() else ""
    m = re.search(r"mission_t=(\d+)s hold=(\d+)s", s)
    f = stream(d)
    if not m or f is None:
        continue
    t = 0.0; inits = []
    for l in f:
        if l.startswith(b"[autopilot] fire"):
            t = float(re.search(rb"t=([0-9.]+)", l).group(1))
        elif l.startswith(b"[initMission]"):
            inits.append(t)
    if inits:
        seg = segments(inits, float(int(m[1]) + int(m[2])))
        print(f"{pathlib.Path(d).name} inits={len(inits)} longest_s={max(seg):.0f} segments={' '.join(f'{x:.0f}' for x in seg)}")
