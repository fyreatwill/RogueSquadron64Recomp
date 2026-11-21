#!/usr/bin/env python3
"""s7776: score a run carrying ROGUESQ_S7774_SLOTS=1 + ROGUESQ_S7776_TBLWATCH=1 (src/main/upstream_compat.cpp s7776_load).
Question: while the s7774 scan sees the NPC slot table *0x80130BB0 dangling (bad>0), does any guest code read the table pointer?
Joins the two line streams by log order: for every maximal run of s7774 tick/post lines with bad>0, takes the [s7776] sum line
just before its first bad line and the last sum line before its closing clean line (or [s7776] tbl-change re-init), and reports the delta of hits (table-pointer
reads) and ctl (frame-counter reads = watch positive control). The tail between that last sum and the re-init is covered by
dangling_hits: s7776_load rescans the table on a read (>=20 ms cache) and counts any read made while it is dangling.
Verdicts: H-unused (0 reads in every dangling window, ctl grew in it, and dangling_hits=0), H-latent (reads / dangling_hits > 0:
the [s7776] dangling-reader lines name the reader), VOID (no dangling window, or ctl did not grow: the watch was dead).
Also requires in-run reads with a clean table (hits>0 outside the windows) as the "readers do fire" control.
usage: s7776_tblwatch_score.py <run.log> [--selftest]   exit 0 H-unused, 1 H-latent, 3 VOID"""
import re, sys

def score(lines):
    sums, wins, cur, tbl = [], [], None, []
    for ln in lines:
        m = re.search(r"\[s7776\] sum t=([\d.]+) ctl=(\d+) hits=(\d+) dangling_hits=(\d+)", ln)
        if m:
            s = (float(m[1]), int(m[2]), int(m[3]), int(m[4])); sums.append(s)
            if cur is not None and not cur["closed"]: cur["after"] = s  # last sum while the window is still open
            continue
        m = re.search(r"\[s7774\] tag=(tick|post|pre) .* bad=(\d+)", ln)
        if m:
            bad = int(m[2]) > 0 and "live=0 " not in ln
            if bad:
                if cur is None or cur["closed"]:
                    cur = {"before": sums[-1] if sums else None, "after": None, "closed": False, "n": 0}; wins.append(cur)
                cur["n"] += 1
            elif cur is not None and not cur["closed"]:
                cur["closed"] = True
            continue
        if "[s7776] tbl-change" in ln and cur is not None and not cur["closed"]: cur["closed"] = True  # re-init ends the dangling table
        if "[s7776] tbl-change" in ln or "[s7776] dangling-reader" in ln: tbl.append(ln.strip())
    if cur is not None and not cur["closed"]: cur["closed"] = True
    if not sums: return 3, ["no [s7776] sum lines: ROGUESQ_S7776_TBLWATCH not armed"]
    out, latent, void = [], False, False
    full = [w for w in wins if w["before"] and w["after"] and w["n"] >= 2]
    if not full: return 3, ["no dangling window bracketed by sum lines (need >=2 bad ticks)"]
    for w in full:
        b, a = w["before"], w["after"]
        dh, dc = a[2] - b[2], a[1] - b[1]
        out.append(f"window t={b[0]:.1f}..{a[0]:.1f} bad_ticks={w['n']} reads={dh} ctl_reads={dc}")
        if dc <= 0: void = True
        if dh > 0: latent = True
    last = sums[-1]
    clean_reads = last[2] - sum(w["after"][2] - w["before"][2] for w in full)
    out.append(f"total reads={last[2]} clean_reads_outside={clean_reads} dangling_hits={last[3]} ctl={last[1]}")
    out += tbl[:12]
    if last[3] > 0 or any("dangling-reader" in x for x in tbl): latent = True
    if clean_reads <= 0: void = True; out.append("VOID: no table reads at all (readers-fire control failed)")
    if void and not latent: return 3, out + ["VERDICT VOID"]
    return (1, out + ["VERDICT H-latent"]) if latent else (0, out + ["VERDICT H-unused"])

def selftest():
    base = ["[s7776] sum t=5.0 ctl=10 hits=100 dangling_hits=0 tbl=X", "[s7774] tag=tick ram=0 live=5 bad=0 x",
            "[s7774] tag=tick ram=0 live=9 bad=9 x", "[s7776] sum t=10.0 ctl=20 hits=100 dangling_hits=0",
            "[s7774] tag=tick ram=0 live=9 bad=9 x", "[s7774] tag=tick ram=0 live=5 bad=0 x", "[s7776] sum t=15.0 ctl=30 hits=150 dangling_hits=0"]
    r0, _ = score(base)
    lat = list(base); lat[3] = "[s7776] sum t=10.0 ctl=20 hits=120 dangling_hits=0"
    r1, _ = score(lat)
    dead = [l.replace("ctl=20", "ctl=10").replace("ctl=30", "ctl=10") for l in base]
    r3, _ = score(dead)
    print(f"selftest unused={r0} latent={r1} deadwatch={r3} -> {'PASS' if (r0, r1, r3) == (0, 1, 3) else 'FAIL'}")
    return 0 if (r0, r1, r3) == (0, 1, 3) else 2

if __name__ == "__main__":
    if "--selftest" in sys.argv: sys.exit(selftest())
    rc, out = score(open(sys.argv[1], errors="replace"))
    print("\n".join(out)); sys.exit(rc)
