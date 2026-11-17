#!/usr/bin/env python3
"""s7532 FY undo-window scorer: per arm, the LAST [s7532-undo] line of $R/log_<arm>.txt must show runs>0,
control(must be 1)=1 and foreign_runs=0.  usage: s7532_undo_score.py <R> <arm>...  exit 0 pass, 1 fail.
--controls: synthetic logs (clean pass, foreign fail, dead-control fail, no-line fail)."""
import re, sys, os, tempfile
def score_log(path):
    last = None
    try:
        for l in open(path, errors="replace"):
            if l.startswith("[s7532-undo]"): last = l
    except OSError: return "nolog"
    if not last: return "noline"
    f = dict(re.findall(r'(\w+(?:\(must be 1\))?)=([\d.]+)', last))
    if int(f.get("runs", 0)) == 0: return "noruns"
    if int(f.get("control(must be 1)", 0)) != 1: return "control=%s" % f.get("control(must be 1)")
    if int(f.get("foreign_runs", 1)) != 0: return "foreign_runs=%s bytes=%s" % (f["foreign_runs"], f.get("foreign_bytes"))
    return "ok runs=%s undo_bytes=%s window_ms=%s" % (f["runs"], f.get("undo_bytes"), f.get("window_ms_total"))
def controls():
    L = "[s7532-undo] runs=%d undo_runs=%d undo_bytes=9 foreign_runs=%d foreign_bytes=%d any_diff_runs=0 control(must be 1)=%d window_ms_total=1.0 window_us_max=2.0\n"
    cases = [("clean", L % (9, 9, 0, 0, 1), True), ("foreign", L % (9, 9, 2, 5, 1), False), ("deadctl", L % (9, 9, 0, 0, 0), False), ("noline", "x\n", False)]
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
