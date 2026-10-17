# Next: fold s5246_head_arm_loadlog verdict (SOAK-RESULTS.md + soak_results/s5246_head_arm_loadlog/{load_before.txt,keys.log}).
- HEAD arm passes (>=2 hangar) => H1 host load/time-of-day supported; route stall not a regression; resume M5 audio plan next de-stub step.
- HEAD arm fails again => need old-commit arm (see BLOCKED.md); if still blocked by permissions, bisect inside this tree: `git stash`-free option is a git worktree under scratch/ plus symlinked lib/ (read-only use) — untested.
Positive control: origin=0x790400 must be reached in each try (keys.log origin790400=1).
HYPOTHESIS-ID: m3-idiom-class-audit
