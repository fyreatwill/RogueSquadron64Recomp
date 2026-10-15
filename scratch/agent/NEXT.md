# Next work unit
HYPOTHESIS-ID: vi640-route-wall
Read SOAK-RESULTS.md for s4972_vi640_idle_a/b (summary.txt in scratch/agent/soak_results/s4972_{a,b}/; each line needs seen640=1 as positive control).
- bad=0 across both (0/10 stall): close the VI-640 wall in CURRENT-TRUTH (fixed by s4970 movz/movn or never real), then resume the generated-symbol-renaming sweep or an M3 idiom-class audit (check `grep -n '^## Session ' PORTING-STATE.md | tail -15` first).
- any stay640: that is a reproduced stall; capture its log's vi-fs stalled state and investigate with phase-gated instrumentation.
- soaks absent from SOAK-RESULTS.md: check soak_queue/ still holds them; do not re-run by hand.
