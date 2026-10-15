# Next work unit
HYPOTHESIS-ID: vi640-route-wall
Read scratch/agent/soak_results/s4972r_a/summary.txt (soak s4972r_vi640_idle_a; the s4972 originals never ran - zsh bug, see s4973). Each line needs seen640=1 as positive control.
- bad=0 (0/5 stall): close the VI-640 wall in CURRENT-TRUTH, then M3 idiom-class audit or the renaming sweep (check `grep -n '^## Session ' PORTING-STATE.md | tail -15` first).
- any stay640: reproduced stall; capture the log's vi-fs stalled state and investigate with phase-gated instrumentation.
- recipe absent from SOAK-RESULTS.md: check soak_queue/ still holds it; if rc=2 in 0s again, read the log for the shell error. Do not use `${0:A:h...}` in recipes.
