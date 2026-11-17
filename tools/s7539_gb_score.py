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
usage: python3 tools/s7539_gb_score.py <log> [<log> ...]       exit 0 iff every log is QUIET or TORN with controls passing
       python3 tools/s7539_gb_score.py --controls               synthetic logs, one per verdict
"""
import re, sys, os, tempfile

RX = re.compile(r"\[s7539-gb\] (\S+) as=(\d) (.*)")
KV = re.compile(r"(\w+)=(\d+)")


def parse(path):
    rows, events = [], []
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("latin-1", "replace")
            m = RX.search(line)
            if m and m.group(2) == "3":
                rows.append(dict((k, int(v)) for k, v in KV.findall(m.group(3))))
            elif "[s7539-gbd]" in line:
                events.append(line.strip()[line.find("[s7539-gbd]"):])
    return rows, events


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
    print(f"controls {ok}/5"); return 0 if ok == 5 else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--controls"]:
        sys.exit(controls())
    vs = [report(p) for p in sys.argv[1:]]
    sys.exit(0 if vs and all(v in ("QUIET", "TORN") for v in vs) else 1)
