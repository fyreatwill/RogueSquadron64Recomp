# Next: fold s5246_head_arm_loadlog verdict (SOAK-RESULTS.md + soak_results/s5246_head_arm_loadlog/{load_before.txt,keys.log}). If it still has not run, do offline M3 idiom-class audit work; do not re-do worktree prep.
- HEAD arm passes (>=2 hangar) => host load/time-of-day; resume M5 audio plan next de-stub step.
- HEAD arm fails => `tools/bisect_worktree.sh 70a56647 build` (worktree already exists, symlinks done; build untested), queue the same recipe against that binary. If old src also fails => host/lib; if passes => toggle main.cpp task_ptr early-return and s5235 save-guard (only behaviour deltas).
Positive control: origin=0x790400 reached in each try (keys.log origin790400=1).
HYPOTHESIS-ID: m3-idiom-class-audit
