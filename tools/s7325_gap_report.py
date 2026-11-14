#!/usr/bin/env python3
"""s7325: summarise build/rs64_s7325.log (audio RSP DMAs in no live heap block).

Usage: s7325_gap_report.py LOG [LOG...]
Per log: positive controls, GAP counters, DG table grouped by kind with the freed-record allocator/freer, age distribution,
and the guest heap-walk cross-check (gk 0 none / 1 header / 2 data, fl 1 free / 2 allocated).
Exit 1 if a control failed (freed_bad or hdr_bad > 0, or no freed_ok / hdr_ok at all).
"""
import collections
import re
import sys

DG = re.compile(r"^DG (\S+) (\S+) x=(\w+) len=(\w+) n=(\d+) lo=(\w+)\+(\w+)\((.*?)\) hi=(\w+)\+(\w+)\((.*?)\) "
                r"freed=(\w+)\+(\w+) age=([\d.]+) freer=(\S+) alloc=(\S+) guest=(\d) fl=(\w+) h=(\w+) sz=(\w+)")


def short(chain, k=2):
    parts = [re.sub(r"\+0x[0-9a-f]+$", "", p) for p in chain.split("<")]
    parts = [p for p in parts if not p.startswith("rs64_s6063") and not p.startswith("?0x0")]
    return "<".join(parts[:k])


def report(path):
    bad = False
    rows = []
    for ln in open(path, errors="replace"):
        ln = ln.rstrip("\n")
        if ln.startswith("s7325 ") or ln.startswith("GAP ") or ln.startswith("DG_OVERFLOW"):
            print("  " + ln)
            if ln.startswith("s7325 "):
                kv = dict(x.split("=") for x in ln.split()[1:])
                if int(kv["freed_bad"]) or int(kv["hdr_bad"]) or not int(kv["freed_ok"]) or not int(kv["hdr_ok"]):
                    bad = True
                    print("  CONTROL FAIL")
                else:
                    print("  CONTROL PASS")
            continue
        m = DG.match(ln)
        if m:
            rows.append(m.groups())
    by = collections.defaultdict(list)
    for r in rows:
        by[(r[0], r[1])].append(r)
    for (src, kind), rs in sorted(by.items()):
        n = sum(int(r[4]) for r in rs)
        print(f"  [{src} {kind}] distinct={len(rs)} reads={n}")
        g = collections.Counter((r[16], int(r[17], 16) & 3) for r in rs)
        print("    guest (gk,fl): " + ", ".join(f"{k}:{v}" for k, v in sorted(g.items())))
        if kind in ("freed", "hdrgap", "untracked"):
            ages = sorted(float(r[13]) for r in rs if int(r[11], 16))
            if ages:
                q = lambda f: ages[min(len(ages) - 1, int(f * len(ages)))]
                print(f"    freed-match {len(ages)}/{len(rs)} age s: min {ages[0]:.3f} p50 {q(.5):.3f} p90 {q(.9):.3f} max {ages[-1]:.3f}")
            al = collections.Counter((short(r[15], 2), int(r[12], 16)) for r in rs if int(r[11], 16))
            for (a, req), c in al.most_common(6):
                print(f"    freed-block alloc {a} req={req:X}: {c}")
            fr = collections.Counter(short(r[14], 3) for r in rs if int(r[11], 16))
            for a, c in fr.most_common(4):
                print(f"    freer {a}: {c}")
            nb = collections.Counter((short(r[7], 1), int(r[6], 16), short(r[10], 1), int(r[9], 16)) for r in rs)
            for (lo, lr, hi, hr), c in nb.most_common(4):
                print(f"    neighbours lo {lo} +{lr:X} | hi {hi} +{hr:X}: {c}")
        ex = sorted(rs, key=lambda r: -int(r[4]))[:3]
        for r in ex:
            print(f"    ex x={r[2]} len={r[3]} n={r[4]} lo={r[5]}+{r[6]} hi={r[8]}+{r[9]} freed={r[11]}+{r[12]} age={r[13]} guest={r[16]} fl={r[17]} h={r[18]} sz={r[19]}")
    return bad


def main():
    bad = False
    for p in sys.argv[1:]:
        print(p)
        bad |= report(p)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
