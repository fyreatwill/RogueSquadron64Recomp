# Next: fold s5246_head_arm_loadlog verdict (SOAK-RESULTS.md + soak_results/s5246_head_arm_loadlog/{load_before.txt,keys.log}). If the arm has not run yet, do offline work (m3-idiom-class-audit) and check the queue next iteration.
- HEAD arm passes (>=2 hangar) => H1 host load/time-of-day supported; route stall not a regression; resume M5 audio plan next de-stub step.
- HEAD arm fails again => old-commit arm needed. cp/ditto are permission-denied headless; try `git worktree add scratch/wt_70a56647 70a56647` (plain git) with lib/ symlinked read-only; only if that fails, write BLOCKED.md with the human one-liner `cd .. && cp -c -R RogueSquadron64Recomp RogueSquadron64Recomp-bisect`.
Positive control: origin=0x790400 must be reached in each try (keys.log origin790400=1).
HYPOTHESIS-ID: m3-idiom-class-audit
