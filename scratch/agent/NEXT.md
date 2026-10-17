# Next: fold s5249_old70a56647_arm verdict (SOAK-RESULTS.md + soak_results/s5249_old70a56647_arm/keys.log). If exit 2 (no old binary): finish `tools/bisect_worktree.sh 70a56647 build`, requeue.
- Old arm passes (>=2 hangar) => src regression: build HEAD with main.cpp task_ptr early-return and s5235 save-guard toggled via env flags in ONE build, run arms concurrently.
- Old arm fails => host/lib/env; resume M5 audio plan (docs/M5-AUDIO-PLAN.md) next de-stub step.
Positive control: origin=0x790400 reached each try.
HYPOTHESIS-ID: m3-idiom-class-audit
