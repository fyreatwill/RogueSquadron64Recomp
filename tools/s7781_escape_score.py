#!/usr/bin/env python3
"""s7781: score the FB-arena escape table of a ROGUESQ_S7779_ARENA=1 ROGUESQ_S7781_PLANT=1 log ([s7781] open/close/cst/pc lines).
Per pc: live = guest stores inside a live arena, closed = guest stores into the last closed extent before the next epoch opens,
closed_busy = of those, while the extent's FB slot state != 0. Families (by pc range, from the retail code):
  DLEMIT 0x8000CFD4-0x8000D6FF  display-list emitter (writes F5 gfx words through *0x8011DC58; 0x100-byte chunks from 0x8002221C)
  LOADER 0x80054xxx-0x80056xxx, 0x80029xxx-0x8002Bxxx (flag-4 callers / zlib), plus 0x80085660 (the s7781a live-only pc)
  other  everything else.
rc 3 = control fail (planted pc DEAD7781 missing, or no close); rc 1 = a LOADER pc stored into a closed extent (H-escape);
rc 4 = no loader escape but a non-loader pc stored into a closed extent while its slot was FREE (st=0), i.e. something besides
       the arena writes into the free FB slot (H-shared-slot, new member); rc 0 = H-clean.
usage: s7781_escape_score.py <run.log>"""
import re, sys
L = open(sys.argv[1], errors="replace").read().splitlines()
sums = [i for i, l in enumerate(L) if l.startswith("[s7781] sum")]
if not sums: print("no [s7781] sum"); sys.exit(3)
rows = []
for l in L[sums[-1] + 1:]:
    if l.startswith("[s7783]"): continue  # s7783 summary lines sit inside the [s7781] dump
    if not l.startswith("[s7781] pc="): break
    rows.append({k: v for k, v in (kv.split("=") for kv in l[8:].split())})
def fam(pc):
    p = int(pc, 16)
    if 0x8000CFD4 <= p <= 0x8000D6FF: return "DLEMIT"
    if 0x80054000 <= p < 0x80057000 or 0x80029000 <= p < 0x8002C000 or p in (0x80085660, 0x80085664): return "LOADER"
    if p == 0xDEAD7781: return "PLANT"
    return "other"
closes = sum(1 for l in L if l.startswith("[s7781] close"))
cst_free = {}
for l in L:
    m = re.match(r"\[s7781\] cst ep=(\d+) pc=(\w+) phys=(\w+) dt_ms=([\d.]+) st=(\d+)", l)
    if m and m[5] == "0": cst_free.setdefault(fam(m[2]), []).append((int(m[1]), m[3], float(m[4])))
agg = {}
for r in rows:
    a = agg.setdefault(fam(r["pc"]), [0, 0, 0, 0]); a[0] += 1; a[1] += int(r["live"]); a[2] += int(r["closed"]); a[3] += int(r["closed_busy"])
print(f"closes={closes} pcs={len(rows)}")
for f, (n, lv, cl, cb) in sorted(agg.items()): print(f"  {f:7s} pcs={n:3d} live={lv:6d} closed={cl:6d} closed_busy={cb:6d} closed_free={cl-cb}")
for f, v in sorted(cst_free.items()):
    print(f"  free-slot stores {f}: {len(v)} logged, phys {sorted(set(x[1] for x in v))[:8]} dt_ms min {min(x[2] for x in v):.2f}")
if agg.get("PLANT", [0, 0, 0])[2] < 1 or closes < 1: print("CONTROL FAIL (plant/close)"); sys.exit(3)
if agg.get("LOADER", [0, 0, 0])[2]: print("H-escape: a flag-4 loader pc stored into a closed extent"); sys.exit(1)
if any(f not in ("PLANT",) for f in cst_free) or any(f not in ("PLANT", "LOADER") and a[2] - a[3] > 0 for f, a in agg.items()): print("H-shared-slot: non-loader stores into the FREE slot after the arena drop"); sys.exit(4)
print("H-clean"); sys.exit(0)
