# NEXT: score the queued 21:9 dd6 auto-path survey (s7058 soaks) and find any level below 59.5 fps
HYPOTHESIS-ID: dd6-219-levelK-survey
Context: s7058 L2/L3 at 21:9 already ~59.6 fps with K0.6 (H-done). KLEVEL auto = 12:0.5,13:0.5. Measured at 21:9: L1-L5, L12, L13.
Queued soaks s7058_219auto_L{0,6,7,8,9,11,14,16,17,18} (auto bundle, 360 s hold). Check SOAK-RESULTS.md for their verdict lines first.
Score each level that ran:
  for L in 0 6 7 8 9 11 14 16 17 18; do echo L$L; python3 tools/g5e_cost_by_parity.py --phases 1 --skip-s 130 scratch/s7058/tl_L${L}a.bin* scratch/agent/m6/g1_lvl${L}s7031L${L}a/run.log | tail -2; done
  plus each level's klog: scratch/s7058/klog_L${L}a.txt (expect `[s7056] level=<L> k=0.6,0.6,0.6`) and crash/alive from arm_L${L}a.out.
Hypotheses:
 H-laggard: some level < 59.5 fps (P(>=2VI) > 0.02) with rsp >= ~12.5 ms -> next unit: same-run tog K split on it
   (copy scratch/s7058/run_hold.zsh, set KLEVEL=<L>:0.5, run `<name> <L> tog`), then pose-qualify (scratch/s7057/run.zsh) before adding it to auto KLEVEL.
 H-alldone: every level >= 59.5 -> the 21:9 dd6 perf thread is CLOSED; record it and take the next ladder item (all G5 items await the owner;
   check ITERATION.md 3c for an open rung, e.g. G5 renaming sweep).
 Any crash in a soak: that is a side-effect failure (G4 rule) -> capture and root-cause it first.
If the soaks have not run yet: run 2-3 of them by hand (zsh scratch/agent/soak_queue/s7058_219auto_L<L>.sh, one at a time, timeout >= 700 s) and
move them to soak_queue/done/.
