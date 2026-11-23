# NEXT (s7844)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this. CURRENT-TRUTH is 59.5 KB: if Step 0 trips (>60000) this is maintenance.
Why: s7843 closed the lvl5 residual camera fork as oracle timing (chase dt = running min of a 1/60-snapped dt; 87 only for raw dts
with low nibble 0; retail first hits one at tick 276 by mupen CPO jitter). Continue the sweep: mission 0x31=5.
Hypotheses for 0x31=5:
  H-exact: render tris dy mode 0 + HUD census identical, ramdump pose words equal until a known-class fork (alloc ptr / dt-snap nibble).
  H-new-fork: a pose/state word forks before any dt-snap 87 tick -> a new carrier; name it with the s7842 chasehex/replay method.
  H-render: render diff (tri dy mode != 0 or HUD census diff) -> render defect, root-cause before state work.
Unit: save `python3 tools/g3_eep_patch.py scratch/s7832/lvl.eep scratch/s7844/lvl.eep --set 0x31=5`; port p1 + retail r1 per the
s7841 recipes in PORTING-STATE (p1 with RS64_RDP_BIN_PORT, r1 with RDP bin + --pc-ram-dump). Add to r1 the s7843 watches
0x800FA738,0x800FA7D0 + RS64_ORACLE_FPR=0,4,6,14,20 so tools/s7843_dt_snap_replay.py marks every nibble-0 tick (expected fork
points that are NOT port defects). Find flight start with scratch/s7829/tl.py; scorers tools/s7827_tri_yshift_census.py --controls,
tools/s7836_hud_elem_census.py, scratch/s7841/score2.py. If a fork precedes the first retail 87 tick, it is new: run chase_cmp.
