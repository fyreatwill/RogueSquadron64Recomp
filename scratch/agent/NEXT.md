# NEXT: finish the 21:9 dd6 auto survey (L8, L9, L14, L16, L17, L18), scoring flight fps with transition gaps excluded
HYPOTHESIS-ID: dd6-219-levelK-survey
Context: s7059 L0/L6/L7/L11 ~59.6-59.9 fps in flight; whole-run shortfalls on L6/L7 are 200-320 ms scene-transition stalls (menu/cutscene/
mission end, audio-slot drain; same at dd1). Measured at 21:9 so far: L0-L7, L11-L13.
Check SOAK-RESULTS.md for s7058_219auto_L{8,9,14,16,17,18}. For each that ran:
  python3 tools/g5e_cost_by_parity.py --phases 1 --skip-s 130 --gaps 150 scratch/s7058/tl_L${L}a.bin* scratch/agent/m6/g1_lvl${L}s7031L${L}a/run.log | sed -n 3,4p
  python3 tools/g5e_cost_by_parity.py --phases 1 --skip-s 130 scratch/s7058/tl_L${L}a.bin* scratch/agent/m6/g1_lvl${L}s7031L${L}a/run.log | tail -1
  cat scratch/s7058/klog_L${L}a.txt ; tail -1 scratch/s7058/arm_L${L}a.out
If none have run: run 2 by hand (mv to soak_queue/running_manual/, zsh it, timeout 600000, mv to done/), check the screen is unlocked first.
Hypotheses:
 H-laggard: some level's "fps excluding these gaps" < 59.5 with rsp >= ~12.5 ms -> same-run tog K split (copy scratch/s7058/run_hold.zsh,
   KLEVEL=<L>:0.5, `<name> <L> tog`), then pose-qualify (scratch/s7057/run.zsh) before adding it to auto KLEVEL.
 H-alldone: all >= 59.5 in flight -> close the 21:9 dd6 perf thread in CURRENT-TRUTH and take the next ladder rung (ITERATION.md 3c).
 A >150 ms gap inside runInMissionFrame (check with tools/g5e_stall_split.py on an xctrace) would be a real in-flight hitch: G5c datum, root-cause it.
 Any crash: side-effect failure (G4 rule) -> capture and root-cause first.
