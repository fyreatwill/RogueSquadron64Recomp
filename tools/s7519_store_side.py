#!/usr/bin/env python3
"""s7519 class FP scorer: the store side of the s7518 D-cache audit (write-back + write-allocate).
Reads game logs from ROGUESQ_S7518_STALEWATCH=1 + ROGUESQ_STORE_DIAG=1 (+ ROGUESQ_CACHE_SHAPE_CTL_WB=<k>) runs: the last
[s7519-sum] line and every [s7519] row (src/main/upstream_compat.cpp s7519 block).
LIVE = a row where port and hardware differ: live_wb (a dirty line written back over DMA bytes), live_load (a load of a dirty line
the DMA overwrote in RAM), live_lost (a load of a store an interior Hit_Invalidate discarded). Outside-ctl dma_over_dirty / discard
rows are hazards (counted, reported) even when they resolve dead.
Exit: 0 = no live and no hazard row outside the ctl, ctl seen (--ctl) on >= 1 log; 1 = live or hazard row outside ctl;
3 = --ctl and no log's planted missing writeback produced a dma_over_dirty row; 4 = no [s7519-sum] in a log; 5 = --controls fail."""
import re, sys
KEYS = ["st_seen", "st_on_S", "wb_clean", "dma_over_dirty", "dd_inv_ok", "live_wb", "live_load", "discard", "live_lost",
        "lost_dma_ok", "ctl_lines", "ctl_wb_hit", "pending_dirty", "pending_over_dma", "pending_lost"]
HAZ = ("dma_over_dirty", "discard", "live_wb", "live_load", "live_lost", "st_on_S")

def score(lines):
    s, rows, ctl = None, [], None
    for ln in lines:
        if ln.startswith("[s7519-sum]"):
            s = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", ln)}
        elif ln.startswith("[s7519] "):
            m = re.match(r"\[s7519\] (\w+) line=(\w+) st_pc=(\w+) at_pc=(\w+) fn=(\S+) ctl=(\d)", ln)
            if m: rows.append(m.groups())
        elif ln.startswith("[cache-ctl] dropped wb"):
            ctl = ln.strip()
    if s is None: return None
    out = [r for r in rows if r[5] == "0" and r[0] in HAZ]
    live = s.get("live_wb", 0) + s.get("live_load", 0) + s.get("live_lost", 0)
    ctlrows = [r for r in rows if r[5] == "1" and r[0] == "dma_over_dirty"]
    return dict(sum=s, out=out, live=live, ctl=ctl, ctl_ok=bool(ctl) and len(ctlrows) > 0, ctlrows=len(ctlrows))

def verdict(rs, want_ctl):
    if any(r is None for r in rs): return 4
    if any(r["out"] for r in rs): return 1
    if any(r["live"] and not r["ctlrows"] for r in rs): return 1
    if want_ctl and not any(r["ctl_ok"] for r in rs): return 3
    return 0

def controls():
    base = "[s7519-sum] st_seen=10 st_on_S=0 wb_clean=5 dma_over_dirty=%d dd_inv_ok=%d live_wb=%d live_load=0 discard=0 live_lost=0 lost_dma_ok=0 ctl_lines=1 ctl_wb_hit=0 pending_dirty=0 pending_over_dma=0 pending_lost=0 row_keys=1\n"
    ctl = "[cache-ctl] dropped wb k=5 a=80760C40 n=100 dirty=1\n"
    row = "[s7519] %s line=80760C40 st_pc=80018F30 at_pc=00000000 fn=dma ctl=%d n=1\n"
    cases = {
        "clean_ctl": ([ctl, row % ("dma_over_dirty", 1), base % (1, 1, 0)], True, 0),
        "no_ctl_row": ([ctl, base % (0, 0, 0)], True, 3),
        "hazard_outside": ([ctl, row % ("dma_over_dirty", 1), row % ("dma_over_dirty", 0), base % (2, 2, 0)], True, 1),
        "live_wb_outside": ([row % ("live_wb", 0), base % (0, 0, 1)], False, 1),
        "discard_outside": ([row % ("discard", 0), base % (0, 0, 0)], False, 1),
        "no_sum": ([ctl], False, 4),
        "clean_noctl": ([base % (0, 0, 0)], False, 0),
    }
    ok = True
    for n, (ls, wc, want) in cases.items():
        got = verdict([score(ls)], wc); ok &= got == want
        print(f"control {n}: got {got} want {want} {'PASS' if got == want else 'FAIL'}")
    return ok

def main():
    a = sys.argv[1:]; want_ctl = "--ctl" in a
    if "--controls" in a and not controls(): print("controls FAIL"); sys.exit(5)
    logs = [x for x in a if not x.startswith("--")]
    rs = []
    for p in logs:
        r = score(open(p, errors="replace").read().splitlines()); rs.append(r)
        if r is None: print(p, "no [s7519-sum]"); continue
        s = r["sum"]
        print(p, " ".join(f"{k}={s.get(k, 0)}" for k in KEYS), f"ctl={'yes' if r['ctl'] else 'no'} ctl_rows={r['ctlrows']} outside_hazard_rows={len(r['out'])}")
        for o in r["out"][:10]: print("  OUTSIDE", o)
    v = verdict(rs, want_ctl); print("s7519_fp verdict", v); sys.exit(v)

if __name__ == "__main__": main()
