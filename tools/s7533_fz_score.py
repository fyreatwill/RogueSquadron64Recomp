#!/usr/bin/env python3
"""s7533 FZ FPS60-clamp scorer: per arm, the LAST [s7533-fz] line of $R/log_<arm>.txt must show clamps>2,
control(must be 1 once clamps>2)=1 and cas_fail=0 (a CAS failure = a guest store the pre-s7533 RMW clamp would have lost).
usage: s7533_fz_score.py <R> <arm>...  exit 0 pass, 1 fail.  --controls: synthetic logs."""
import re, sys, os, tempfile
def score_log(path):
    last = None
    try:
        for l in open(path, errors="replace"):
            if l.startswith("[s7533-fz]"): last = l
    except OSError: return "nolog"
    if not last: return "noline"
    f = {k: int(v) for k, v in re.findall(r'(\w+)(?:\([^)]*\))?=(\d+)', last)}
    if f.get("clamps", 0) <= 2: return "noplant clamps=%d" % f.get("clamps", 0)
    if f.get("control", 0) != 1: return "control=%d" % f.get("control", 0)
    if f.get("cas_fail", 1) != 0: return "cas_fail=%d" % f["cas_fail"]
    return "ok vi=%d clamps=%d guest_changes=%d" % (f["vi"], f["clamps"], f.get("guest_changes", -1))
def controls():
    L = "[s7533-fz] vi=7200 clamps=%d cas_fail=%d guest_changes=9 control(must be 1 once clamps>2)=%d\n"
    cases = [("clean", L % (900, 0, 1), True), ("lost", L % (900, 2, 1), False), ("deadctl", L % (900, 0, 0), False),
             ("noplant", L % (2, 0, 0), False), ("noline", "x\n", False)]
    ok = 0
    with tempfile.TemporaryDirectory() as d:
        for n, txt, want in cases:
            p = os.path.join(d, n); open(p, "w").write(txt); got = score_log(p).startswith("ok")
            print("control %-8s %s" % (n, "PASS" if got == want else "FAIL")); ok += got == want
    print("controls: %d/%d PASS" % (ok, len(cases))); return 0 if ok == len(cases) else 1
if __name__ == "__main__":
    if "--controls" in sys.argv: sys.exit(controls())
    R, arms, bad = sys.argv[1], sys.argv[2:], 0
    for a in arms:
        v = score_log(os.path.join(R, "log_%s.txt" % a)); bad += not v.startswith("ok"); print("arm %s %s" % (a, v))
    print("score=%d" % bad); sys.exit(1 if bad else 0)
