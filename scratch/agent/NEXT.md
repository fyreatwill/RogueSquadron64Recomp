# NEXT (s7689)
HYPOTHESIS-ID: g6c-l1-bunker-handoff

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7688 refreshed the G6c sheet: no wholesale regression (flicker + early items held/rose on 3/4 arms, controls PASS), but L1 dd2's
far bunker (s7630 med_fpx 153) no longer flickers (med 0; it is in both frames of each pair).
Hypotheses: H-path (this run flew a different path or timing, so the bunker was real/absent in window 1) vs H-handoff (one of
ROGUESQ_S7672_HOLD / S7681_SHIELD / S7684_RSKEY / S7685_POSSUB / S7686_POSSUB / S7687_POSSUB hands the bunker over early).
Discriminator, ONE run, two arms at L1 dd2 (copy scratch/s7688_standins_proof.sh, ARMS a12 new vs a12old with all six knobs =0,
output scratch/s7689_soak):
  - old arm med_fpx >= ~100 with the bunker ON-only, new arm 0 -> H-handoff; then bisect knobs (3 + 3) in the next run.
  - both ~0 -> H-path (scene variance); check [standins-spawn] for the bunker's item in both logs and close the thread.
Score: tools/s7628_standins_sheet.py --cluster 16 --control --pairs 3 per arm (control must PASS in both).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, screen unlocked. Default STANDINS stays off; owner judges the look.
