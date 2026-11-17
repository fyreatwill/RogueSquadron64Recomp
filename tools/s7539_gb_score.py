#!/usr/bin/env python3
"""s7539 class GB scorer: RDP_ASYNC+NODRAIN post-signal texture reads vs the dp_complete snapshot.

Reads the cumulative `[s7539-gb] p<N> as=3 ...` lines (one per 600 posts, ROGUESQ_S7539_GB_CHK=1, src/main/rt64_render_context.cpp)
and the `[s7539-gbd]` diff events. Per log: totals, the tail half (posts after the midpoint print, i.e. mission flight in a
g1e_owner_quiet_arms HOLD 120 arm), and the controls.
Verdict per log:
  CTL-FAIL   planted != caught, or no older-snapshot diffs (the comparator saw no real texture change), or witness 0
  NO-WINDOW  post-signal loads 0
  QUIET      controls pass, diff_loads 0
  TORN       controls pass, diff_loads > 0 (events listed)
s7540: ROGUESQ_RDP_NODRAIN=4 cycles drain (as=1) / nodrain (as=3) / reads-wait (as=4) per task in one run. When as=4 rows exist the
log also gets a FIX verdict: FIX-OK (as=3 controls pass and TORN or QUIET, as=4 diff_loads 0), FIX-RESIDUAL (as=4 diff_loads > 0),
FIX-CTL (as=3 controls fail, so an as=4 zero means nothing). Drain ms per as= comes from the mean of the [g1e-aq] rows (ROGUESQ_G1B=1)
in the tail half of the run, plus [s7540-rw] sig/idle totals.
usage: python3 tools/s7539_gb_score.py <log> [<log> ...]       exit 0 iff every log is QUIET or TORN with controls passing
       python3 tools/s7539_gb_score.py --controls               synthetic logs, one per verdict
"""
import re, sys, os, tempfile

RX = re.compile(r"\[s7539-gb\] (\S+) as=(\d) (.*)")
KV = re.compile(r"(\w+)=(\d+)")


AQ = re.compile(r"\[g1e-aq\] t=\d+ as=(\d) n=(\d+) total=([\d.]+) rsp=[\d.]+ drain=([\d.]+)")
RW = re.compile(r"\[s7540-rw\] t=\d+ sig=(\d+) idle=(\d+)")


def parse(path, mode="3", extra=None):
    rows, events = [], []
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("latin-1", "replace")
            m = RX.search(line)
            if m and m.group(2) == mode:
                rows.append(dict((k, int(v)) for k, v in KV.findall(m.group(3))))
            elif "[s7539-gbd]" in line:
                events.append(line.strip()[line.find("[s7539-gbd]"):])
            elif extra is not None:
                a = AQ.search(line)
                if a:
                    extra.setdefault("aq", []).append((int(a.group(1)), int(a.group(2)), float(a.group(3)), float(a.group(4))))
                r = RW.search(line)
                if r:
                    extra["sig"] = extra.get("sig", 0) + int(r.group(1)); extra["idle"] = extra.get("idle", 0) + int(r.group(2))
    return rows, events


def fix_verdict(rows3, rows4):
    v3 = verdict(rows3)[0]
    if not rows4:
        return "NO-AS4"
    if v3 not in ("QUIET", "TORN"):
        return "FIX-CTL"
    return "FIX-OK" if rows4[-1]["diff_loads"] == 0 else "FIX-RESIDUAL"


def verdict(rows):
    if not rows:
        return "NO-DATA", {}
    last = rows[-1]
    mid = rows[len(rows) // 2 - 1] if len(rows) >= 2 else {k: 0 for k in last}
    tail = {k: last[k] - mid.get(k, 0) for k in last}
    ctl_ok = last["ctl_planted"] > 0 and last["ctl_planted"] == last["ctl_caught"] and last["prev_diff_loads"] > 0 and last["wit_bytes"] > 0
    if not ctl_ok:
        v = "CTL-FAIL"
    elif last["post"] == 0:
        v = "NO-WINDOW"
    elif last["diff_loads"] == 0:
        v = "QUIET"
    else:
        v = "TORN"
    return v, {"last": last, "tail": tail}


def report(path):
    rows, events = parse(path)
    v, d = verdict(rows)
    print(f"== {path}: {v} prints={len(rows)}")
    if d:
        for name in ("last", "tail"):
            x = d[name]
            print(f"  {name:4}: post={x['post']} pre={x['pre']} cmp_MB={x['cmp_bytes'] / 1e6:.1f} diff_loads={x['diff_loads']} diff_bytes={x['diff_bytes']} "
                  f"prev_diff_loads={x['prev_diff_loads']} prev_diff_bytes={x['prev_diff_bytes']} planted={x['ctl_planted']} caught={x['ctl_caught']} "
                  f"wit_n={x['wit_n']} wit_kB/win={(x['wit_bytes'] / x['wit_n'] / 1024) if x['wit_n'] else 0:.0f}")
    for e in events[:12]:
        print("  " + e)
    if len(events) > 12:
        print(f"  ... {len(events) - 12} more events")
    ex = {}
    rows4 = parse(path, "4", ex)[0]
    if rows4:
        l4 = rows4[-1]
        fv = fix_verdict(rows, rows4)
        print(f"  as=4 reads-wait: post={l4['post']} pre={l4['pre']} diff_loads={l4['diff_loads']} diff_bytes={l4['diff_bytes']} "
              f"post_nosnap={l4['post_nosnap']} planted={l4['ctl_planted']} caught={l4['ctl_caught']} -> {fv}")
        rows1 = parse(path, "1")[0]
        if rows1:
            print(f"  as=1 drained: loads={rows1[-1]['loads']} pre={rows1[-1]['pre']} post={rows1[-1]['post']}")
        aq = ex.get("aq", [])
        half = aq[len(aq) // 2:]
        for a in sorted({r[0] for r in half}):
            xs = [r for r in half if r[0] == a]; n = sum(r[1] for r in xs)
            if n:
                print(f"  aq as={a}: tasks={n} drain_ms={sum(r[1] * r[3] for r in xs) / n:.2f} total_ms={sum(r[1] * r[2] for r in xs) / n:.2f}")
        print(f"  reads-wait ended by signal={ex.get('sig', 0)} by idle={ex.get('idle', 0)}")
        if fv != "FIX-OK":
            v = fv
    return v


def controls():
    base = "loads=10 pre=5 post={post} post_nosnap=0 cmp_bytes=100 diff_loads={dl} diff_bytes={db} prev_cmp=5 prev_diff_loads={pd} prev_diff_bytes=9 ctl_planted={pl} ctl_caught={ca} wit_n=1 wit_bytes=4 wit_max=4 snaps=1"
    cases = {"QUIET": dict(post=5, dl=0, db=0, pd=2, pl=1, ca=1), "TORN": dict(post=5, dl=1, db=3, pd=2, pl=1, ca=1),
             "CTL-FAIL": dict(post=5, dl=0, db=0, pd=2, pl=2, ca=1), "NO-WINDOW": dict(post=0, dl=0, db=0, pd=2, pl=1, ca=1)}
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        for want, kw in cases.items():
            p = os.path.join(td, want + ".log")
            open(p, "w").write("junk\n[s7539-gb] p600 as=3 " + base.format(**kw) + "\n[s7539-gb] p600 as=0 loads=1 pre=1\n")
            got = verdict(parse(p)[0])[0]
            print(f"control {want}: got {got} {'PASS' if got == want else 'FAIL'}"); ok += got == want
        p = os.path.join(td, "none.log"); open(p, "w").write("nothing\n")
        got = verdict(parse(p)[0])[0]; print(f"control NO-DATA: got {got} {'PASS' if got == 'NO-DATA' else 'FAIL'}"); ok += got == "NO-DATA"
        t3 = "[s7539-gb] p600 as=3 " + base.format(post=5, dl=1, db=3, pd=2, pl=1, ca=1)
        bad3 = "[s7539-gb] p600 as=3 " + base.format(post=5, dl=1, db=3, pd=0, pl=1, ca=1)
        for want, l3, dl4 in (("FIX-OK", t3, 0), ("FIX-RESIDUAL", t3, 2), ("FIX-CTL", bad3, 0)):
            p = os.path.join(td, want + ".log")
            open(p, "w").write(l3 + "\n[s7539-gb] p600 as=4 " + base.format(post=0, dl=dl4, db=dl4, pd=0, pl=0, ca=0) + "\n")
            got = fix_verdict(parse(p, "3")[0], parse(p, "4")[0])
            print(f"control {want}: got {got} {'PASS' if got == want else 'FAIL'}"); ok += got == want
    print(f"controls {ok}/8"); return 0 if ok == 8 else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--controls"]:
        sys.exit(controls())
    vs = [report(p) for p in sys.argv[1:]]
    sys.exit(0 if vs and all(v in ("QUIET", "TORN") for v in vs) else 1)  # a FIX-RESIDUAL / FIX-CTL replaces v, so exits 1
