# NEXT (s7841)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7840 showed VI_STAMP=1 + ROGUESQ_RETAIL_SNAP=1 makes the port settle exactly where retail CPO1 does on lvl2/3/4 (rest pitch and
lvl4 reticle pixels). Continue the det sweep on mission 0x31=4 (Gerrard V, G5a's level) with both knobs, now expecting exactness.
Hypotheses:
  H-exact: pinned port == retail CPO1 on lvl5 too (world tris dy mode 0, HUD census identical, rest pose equal).
  H-new-fork: something else differs on Gerrard V (another host-timing read, or a real defect) -> name the first differing ramdump row.
Unit (2 runs): save `python3 tools/g3_eep_patch.py scratch/s7832/lvl.eep scratch/s7841/lvl.eep --set 0x31=4`;
  port: s7840 l4 recipe (PORTING-STATE s7840) with SAVE_FROM=scratch/s7841/lvl.eep, XE + ROGUESQ_RETAIL_SNAP=1 (no explicit levers) + RDP bin;
  retail: tools/s7828_retail_cpo.sh CPO=1 with the same PP, XO --pc-ram-dump as s7840 r3c1, RDP bin kept.
  Score: scratch/s7829/tl.py flight bands, s7827 world-tri compare --controls, s7836 HUD census, scratch/s7840/steady.py rows.
If H-exact: record lvl5 closed; next level 0x31=5. If H-new-fork: first differing row + which word, one lever.
