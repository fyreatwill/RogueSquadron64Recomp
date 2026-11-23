# NEXT (s7843)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this. CURRENT-TRUTH is 59.1 KB: if Step 0 trips (>60000) this is maintenance.
Why: s7842 named the lvl5 camera fork carrier: the chase step's dt operand (f20 at 0x8004D6C8, = cam+0xA4) is 0x3D088888 every tick
in the port (RETAIL_SNAP pin el 811160 vd 1) but retail flips to 0x3D088887 from chase tick 276 (88 x274, 87 x1750). All other
operands bit-identical. Decide whether that flip is ground truth.
Hypotheses:
  H-cpo-model: retail's el jitter (811160..811170) comes from mupen CountPerOp=1 instruction-count timing; the dt flip follows a
     particular el value -> the oracle's timing model, not hardware; close the lvl5 residual fork as "not a port defect" (pin is the
     best constant) and move on to 0x31=5.
  H-state: dt is a deterministic function of game state (e.g. an accumulator or vd/frame branch at 0x8000BE80/0x8000BF34) that
     flips at tick 276 independent of el -> a better RETAIL_SNAP model can match it; implement it behind the same knob.
Unit: ONE retail run: r4 recipe (PORTING-STATE s7842) + `--watch-pc 0x8000BE28,0x8000BF3C,0x8004D6C8` with RS64_ORACLE_FPR=0,2,20
(BE28 prints v0=el, v1=prev; BF3C f0 = the stored dt). Offline: per tick, el/vd/stored-dt beside the chase f20; does the first 87
coincide with an el change (H-cpo-model) or not (H-state)? Port twin if needed: ROGUESQ_S7839_SNAP=1 logs el/vd/ret. If H-cpo-model,
also try the lever ROGUESQ_S7839_SNAP_EL=<the el that gives 87> in one port run to show the fork moves (positive control).
Then 0x31=5: `python3 tools/g3_eep_patch.py scratch/s7832/lvl.eep scratch/s7843/lvl.eep --set 0x31=5`, recipes in PORTING-STATE s7841.
Scorers: scratch/s7842/{fork,replay,chase_cmp}.py, scratch/s7841/score2.py, tools/s7827_tri_yshift_census.py --controls,
tools/s7836_hud_elem_census.py.
