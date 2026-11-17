#!/usr/bin/env python3
"""s7536: score ROGUESQ_SP_LATE=alt per-task-state logs (build/rs64_s7536.log, src/rsp/s7535_ga_chk.cpp).

Per arm, flight phases (>= 5) summed per state (late=0 early upstream sp_complete, late=1 hardware order):
tasks, tris/task, spikes per 1k tris (guard-band test, CULL_SPIKE's), culled per 1k tris, big hulls per task.
VALID arm: both states have tasks and tris; control ctl (every N-th late=1 tri, ROGUESQ_S7536_CTL=N) fired in
late=1 only and within 2% of tris_late/N; tris/task ratio late/early within 0.8..1.25 (same scenes in both states).
Verdict per arm: H-visible when early spikes/1k > 1.5x late AND the excess > 3 sigma (Poisson), else H-none.

  python3 tools/s7536_splate_score.py <dir> l4d2 l4d4 l1d8      # reads <dir>/s7536_<arm>.log
  python3 tools/s7536_splate_score.py --controls
"""
import math, re, sys, tempfile, os

SUM = re.compile(r'\[s7536-sum\] phase=(\d+) late=(\d) (.*)')
MODE = re.compile(r'\[s7536-mode\] sp_late=(-?\d+) ctl_n=(\d+)')


def parse(path):
    try:
        txt = open(path, errors="replace").read()
    except OSError:
        return None
    m = MODE.search(txt)
    ctl_n = int(m.group(2)) if m else 0
    st = [dict(), dict()]
    for m in SUM.finditer(txt):
        if int(m.group(1)) < 5:
            continue
        d = st[int(m.group(2))]
        for k, v in re.findall(r'(\w+)=(\d+)', m.group(3)):
            d[k] = d.get(k, 0) + int(v)
    return ctl_n, st


def score(name, parsed):
    if parsed is None:
        return 1, "%s: MISSING log" % name, None
    ctl_n, st = parsed
    g = lambda l, k: st[l].get(k, 0)
    bad = []
    for l in (0, 1):
        if not g(l, "tasks") or not g(l, "tris"):
            bad.append("state %d empty" % l)
    if bad:
        return 1, "%s: INVALID %s" % (name, ", ".join(bad)), None
    tpt = [g(l, "tris") / g(l, "tasks") for l in (0, 1)]
    r = tpt[1] / tpt[0]
    if not 0.8 <= r <= 1.25:
        bad.append("tris/task ratio %.2f" % r)
    if ctl_n:
        exp = g(1, "tris") // ctl_n
        if g(0, "ctl") or abs(g(1, "ctl") - exp) > max(2, 0.02 * exp) or not g(1, "ctl"):
            bad.append("ctl early=%d late=%d expected 0/%d" % (g(0, "ctl"), g(1, "ctl"), exp))
    else:
        bad.append("no control armed")
    sp = [1000.0 * g(l, "spikes") / g(l, "tris") for l in (0, 1)]
    # Poisson: expected early spikes if early had the late rate
    exp0 = g(1, "spikes") / g(1, "tris") * g(0, "tris")
    z = (g(0, "spikes") - exp0) / math.sqrt(max(exp0, 1.0))
    vis = sp[0] > 1.5 * sp[1] and z > 3 and not bad
    line = ("%s: %s early tasks=%d tris/task=%.0f spikes=%d (%.3f/1k) culled=%d big/task=%.2f | late tasks=%d tris/task=%.0f "
            "spikes=%d (%.3f/1k) culled=%d big/task=%.2f | ctl %d/%d z=%.1f -> %s") % (
        name, "INVALID " + ",".join(bad) if bad else "ok", g(0, "tasks"), tpt[0], g(0, "spikes"), sp[0], g(0, "culled"),
        g(0, "big") / g(0, "tasks"), g(1, "tasks"), tpt[1], g(1, "spikes"), sp[1], g(1, "culled"), g(1, "big") / g(1, "tasks"),
        g(1, "ctl"), g(1, "tris") // ctl_n if ctl_n else 0, z, "H-visible" if vis else ("H-none" if not bad else "n/a"))
    return (1 if bad else 0), line, vis


def controls():
    def mk(rows, ctl=1000):
        f = tempfile.NamedTemporaryFile("w", delete=False, suffix=".log")
        f.write("[s7536-mode] sp_late=2 ctl_n=%d\n" % ctl)
        for p, l, t, tr, s, c in rows:
            f.write("[s7536-sum] phase=%d late=%d tasks=%d tris=%d spikes=%d culled=%d big=%d ctl=%d\n" % (p, l, t, tr, s, s, t, c))
        f.close(); return f.name
    cases = [
        ("equal rates -> H-none", [(6, 0, 100, 100000, 50, 0), (6, 1, 100, 100000, 50, 100)], 0, False),
        ("early 4x -> H-visible", [(6, 0, 100, 100000, 200, 0), (6, 1, 100, 100000, 50, 100)], 0, True),
        ("ctl missed -> invalid", [(6, 0, 100, 100000, 200, 0), (6, 1, 100, 100000, 50, 0)], 1, None),
        ("ctl in early -> invalid", [(6, 0, 100, 100000, 200, 3), (6, 1, 100, 100000, 50, 100)], 1, None),
        ("pre-flight only -> invalid", [(3, 0, 100, 100000, 200, 0), (3, 1, 100, 100000, 50, 100)], 1, None),
        ("scene mismatch -> invalid", [(6, 0, 100, 200000, 200, 0), (6, 1, 100, 100000, 50, 100)], 1, None),
    ]
    ok = 0
    for nm, rows, want_rc, want_vis in cases:
        p = mk(rows); rc, line, vis = score(nm, parse(p)); os.unlink(p)
        good = rc == want_rc and (want_vis is None or vis == want_vis)
        ok += good; print(("PASS " if good else "FAIL ") + line)
    print("controls %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--controls"]:
        sys.exit(controls())
    d, arms = sys.argv[1], sys.argv[2:]
    rc = 0
    for a in arms:
        r, line, _ = score(a, parse(os.path.join(d, "s7536_%s.log" % a)))
        rc |= r; print(line)
    sys.exit(rc)
