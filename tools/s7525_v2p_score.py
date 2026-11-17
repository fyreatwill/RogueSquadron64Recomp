#!/usr/bin/env python3
"""s7525: score one ROGUESQ_S7524_V2P arm from its copied logs.
usage: s7525_v2p_score.py <dir> <arm>...   (dir holds s7094_<arm>.log s7095_<arm>.log s7096_<arm>.log log_<arm>.txt)
Per arm: escapes==0, s7096 MAIN missing/dup/order==0 and selftest pass, gfx DMA writes dram_hi8==0 (positive control: V2P live),
last ovl0 L_1DB0 row b2>0 and b3==0 (task entry takes the physical-pointer test). Exit 0 all pass, 1 any live failure, 4 missing log."""
import re, sys, os
d, arms = sys.argv[1], sys.argv[2:]
rc = 0
for a in arms:
    p = lambda k: os.path.join(d, k)
    try:
        s95 = open(p(f"s7095_{a}.log")).read(); s96 = open(p(f"s7096_{a}.log")).read()
        s94 = open(p(f"s7094_{a}.log")).read(); lg = open(p(f"log_{a}.txt"), errors="replace").read()
    except OSError as e:
        print(f"arm={a} MISSING {e}"); rc = max(rc, 4); continue
    esc = int(re.search(r"escapes=(\d+)", s95).group(1))
    m = re.search(r"^MAIN .*?order=(\d+) dup=(\d+) .*?MISSING_UNEXPLAINED=(\d+)", s96, re.M)
    order, dup, miss = map(int, m.groups()) if m else (-1, -1, -1)
    st = "selftest=pass" in s96
    w = re.search(r"TOT dir=wr bank=gfx n=(\d+) .*?dram_hi8=(\d+)", s94)
    wn, whi = (int(w.group(1)), int(w.group(2))) if w else (0, -1)
    rows = re.findall(r"\[s7521-l1db0\] why=\w+ win=ovl0 entry=(\d+) b0=\d+ b1=\d+ b2=(\d+) b3=(\d+)", lg)
    ent, b2, b3 = map(int, rows[-1]) if rows else (0, 0, -1)
    ok = esc == 0 and (order, dup, miss) == (0, 0, 0) and st and wn > 0 and whi == 0 and b2 > 0 and b3 == 0
    print(f"arm={a} escapes={esc} order={order} dup={dup} missing={miss} s7096_selftest={st} gfx_wr={wn} gfx_wr_hi8={whi} "
          f"l1db0_entry={ent} b2={b2} b3={b3} {'PASS' if ok else 'FAIL'}")
    if not ok: rc = max(rc, 1)
print(f"s7525_v2p score={rc}"); sys.exit(rc)
