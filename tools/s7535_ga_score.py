#!/usr/bin/env python3
"""Score s7535 class GA window logs (build/rs64_s7535.log copied per arm, src/rsp/s7535_ga_chk.cpp).

Per arm, summed over phases: tasks, gfx RSP DMA fetches, fetched bytes, diff_bytes (= bytes changed between the early
sp_complete snapshot and the fetch), control planted/caught, activity witness (bytes changed anywhere in sampled windows).
An arm is VALID when tasks > 0, ctl_planted > 0, ctl_caught == ctl_planted (the compare sees a one-byte change) and the
window is live (win_chg_bytes > 0 in sampled windows: memory really changes while the LLE runs, so diff 0 is not an idle
window).  score = number of invalid arms + number of arms with diff_bytes > 0 (each diff row printed).

  python3 tools/s7535_ga_score.py <dir> l4 l15        # reads <dir>/s7535_<arm>.log
  python3 tools/s7535_ga_score.py --controls
"""
import re, sys, tempfile, os

SUM = re.compile(r'\[s7535-sum\] phase=(\d+) (?:late=(\d) )?(.*)')
DIFF = re.compile(r'\[s7535-diff\] (.*)')


def parse(path):
    tot, phases, diffs = {}, {}, []
    try:
        txt = open(path, errors="replace").read()
    except OSError:
        return None
    for m in SUM.finditer(txt):
        kv = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', m.group(3))}
        late = int(m.group(2) or 0)
        phases[(int(m.group(1)), late)] = kv
        for k, v in kv.items():
            tot["L%d_%s" % (late, k)] = tot.get("L%d_%s" % (late, k), 0) + v
        for k, v in kv.items():
            tot[k] = tot.get(k, 0) + v
    diffs = [m.group(1) for m in DIFF.finditer(txt)]
    return tot, phases, diffs


def score_arm(name, parsed):
    if parsed is None:
        return 1, "%s: MISSING log" % name, []
    tot, phases, diffs = parsed
    g = lambda k: tot.get(k, 0)
    bad = []
    if g("tasks") == 0: bad.append("no tasks")
    if g("ctl_planted") == 0: bad.append("control never planted")
    if g("ctl_caught") != g("ctl_planted"): bad.append("control missed %d/%d" % (g("ctl_planted") - g("ctl_caught"), g("ctl_planted")))
    if g("win_chg_bytes") == 0: bad.append("window idle (activity witness 0)")
    s = (1 if bad else 0) + (1 if g("diff_bytes") else 0)
    line = ("%s: %s tasks=%d dmas=%d bytes=%d diff_bytes=%d diff_dmas=%d diff_tasks=%d oob=%d wr_mirror=%d ctl=%d/%d "
            "witness=%d bytes in %d/%d sampled windows phases=%s%s") % (
        name, "ok" if not s else "SCORE%d" % s, g("tasks"), g("dmas"), g("bytes"), g("diff_bytes"), g("diff_dmas"),
        g("diff_tasks"), g("oob"), g("wr_mirror"), g("ctl_caught"), g("ctl_planted"), g("win_chg_bytes"), g("win_chg_tasks"),
        g("sampled"), ",".join("%d%s:%d/%d" % (p[0], "L" if p[1] else "", v.get("tasks", 0), v.get("diff_tasks", 0)) for p, v in sorted(phases.items())),
        (" INVALID: " + "; ".join(bad)) if bad else "")
    for l in (0, 1):
        t = tot.get("L%d_tasks" % l, 0)
        if t:
            q = lambda k: tot.get("L%d_%s" % (l, k), 0)
            line += ("\n   %s sp_complete: tasks=%d diff_tasks=%d (%.1f%%) diff_bytes/task=%.1f prod=%d clear=%d other=%d refetch=%d "
                     "refetch_diff=%d ctl=%d/%d") % ("LATE " if l else "EARLY", t, q("diff_tasks"), 100.0 * q("diff_tasks") / t,
                     q("diff_bytes") / t, q("prod"), q("clear"), q("other"), q("refetch"), q("refetch_diff"), q("ctl_caught"), q("ctl_planted"))
    return s, line, diffs


def controls():
    res = []
    good = ("[s7535-sum] phase=4 tasks=100 dmas=900 bytes=99999 diff_bytes=0 diff_dmas=0 diff_tasks=0 oob=0 wr_mirror=50 "
            "ctl_planted=2 ctl_caught=2 sampled=3 win_chg_bytes=4000 win_chg_tasks=3\n")
    cases = [("clean", good, 0),
             ("diff", good.replace("diff_bytes=0", "diff_bytes=5") + "[s7535-diff] task=9 phase=4 dram=1000 len=40\n", 1),
             ("ctl missed", good.replace("ctl_caught=2", "ctl_caught=1"), 1),
             ("idle window", good.replace("win_chg_bytes=4000", "win_chg_bytes=0"), 1),
             ("no plant", good.replace("ctl_planted=2 ctl_caught=2", "ctl_planted=0 ctl_caught=0"), 1)]
    with tempfile.TemporaryDirectory() as d:
        for name, txt, want in cases:
            p = os.path.join(d, "x.log"); open(p, "w").write(txt)
            s, line, _ = score_arm(name, parse(p))
            res.append((name, s == want, line))
        s, line, _ = score_arm("missing", parse(os.path.join(d, "nope.log")))
        res.append(("missing log", s == 1, line))
    for n, ok, line in res:
        print("control %-12s %s %s" % (n, "PASS" if ok else "FAIL", "" if ok else line))
    print("controls: %d/%d PASS" % (sum(1 for r in res if r[1]), len(res)))
    return 0 if all(r[1] for r in res) else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    d, arms = sys.argv[1], sys.argv[2:]
    total = 0
    for a in arms:
        s, line, diffs = score_arm(a, parse(os.path.join(d, "s7535_%s.log" % a)))
        total += s
        print(line)
        for x in diffs[:20]:
            print("   diff " + x)
    print("score=%d" % total)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
