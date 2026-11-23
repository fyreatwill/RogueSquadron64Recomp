# NEXT (s7840)
HYPOTHESIS-ID: g3-flight-fork-carrier
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines (fold s7839_snappin_L1: pass = rP and rC alive, vi_stalls30s 0, pin banner rP=1 rC=0). Crash/owner report outranks this.
Why: s7839 selected H-snapshot: timeSnapshotFiller's mid-frame el/vd (port 0/2, retail ~1 VI/1) carries the lvl4 camera fork;
ROGUESQ_S7839_SNAP_EL=811160 ROGUESQ_S7839_SNAP_VD=1 gives rest pitch 0.2085 = retail. Not yet shown: that it closes the reticle
pixels, and that it generalises across levels.
Hypotheses:
  H-general: the pin closes the rest-pitch gap on every level (lvl2 retail 0.0627/0.0632 vs port 0.0603; lvl3 retail 0.0656 vs 0.0631).
  H-lvl4-only: lvl2/lvl3 settle elsewhere (other inputs, e.g. el varying 1-3 VI in retail, matter there).
Unit (3 port runs, no retail runs needed: retail ramdumps exist in scratch/s7834/r1, s7836/r1d, s7838/ret):
  1. lvl4 p1 recipe (s7839 PORTING-STATE entry) + pin + RS64_RDP_BIN_PORT -> tools/s7836_hud_elem_census.py vs scratch/s7838/ret/retail.bin:
     reticle big/small must land at retail 230.0,149.5 / 242.75,159.5 (unpinned 5.75 px low).
  2. lvl2 (SAVE_FROM scratch/s7832/lvl.eep) and lvl3 (scratch/s7836/lvl.eep) with the pin; w441 rest pitch vs retail (scratch/s7838/steady.py).
If H-general: propose ROGUESQ_RETAIL_SNAP (=the pin) to the owner decisions list as a retail-accuracy candidate default (with VI_STAMP).
If H-lvl4-only: one more model (el from a per-frame guest-cost estimate) is out of scope; record and move the det sweep to 0x31=4.
