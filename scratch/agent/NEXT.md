# Next: old-src arm is BLOCKED (fresh worktree build needs Metal toolchain: `xcodebuild -downloadComponent MetalToolchain`, human-only; recipe moved to soak_queue/cancelled/). Do the no-human equivalent in the EXISTING build/ (incremental, no shader rebuild):
1. Add env flags in src disabling (a) main.cpp task_ptr range early-return and (b) the s5235 save-guard (if lib edited: export.sh + commit). One build.
2. Queue three recipes from the s5246 template (soak_queue/done/s5246_head_arm_loadlog_*.sh): baseline, no-task_ptr-guard, no-save-guard. PASS = >=2/3 hangar, 0 CRASH; positive control origin=0x790400.
3. All fail => host/environment; resume M5 audio plan (docs/M5-AUDIO-PLAN.md).
HYPOTHESIS-ID: m3-idiom-class-audit
