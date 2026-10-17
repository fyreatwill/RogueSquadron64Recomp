# Next: read SOAK-RESULTS.md lines for s5242_maskon and s5242_maskoff (keys1.log in scratch/agent/soak_results/<name>/).
Outcome map: maskon fail + maskoff pass => H-mask: revert TO_PTR mask in lib ultra64.h, run submodule-patches/export.sh, commit, then find which TO_PTR caller passes an out-of-window (e.g. 0xA0000000) arg. Both pass => H-flake (n=1; note host load). Both fail => H-other: bisect commits s5229..s5240 (src/main probes, rt64/N64ModernRuntime masks) by queueing builds, or check host load (uptime) first.
If maskon passes cleanly (mission_onset ~174s, crash=0), resume M5 audio plan (docs/M5-AUDIO-PLAN.md) next de-stub step.
HYPOTHESIS-ID: m3-idiom-class-audit
