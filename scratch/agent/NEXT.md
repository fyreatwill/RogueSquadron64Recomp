# Next: fold s5250_taskptr_baseline / s5250_taskptr_noguard from SOAK-RESULTS.md (logs in scratch/agent/soak_results/<name>/keys.log + run*.log; grep '[s5250-taskptr-guard]').
- guard fires + noguard hangar>=2 and baseline fails => guard is the regression; find the caller that passes a wild task_ptr (ORIGIN rule 11).
- guard never fires, both fail => src cleared; host/lib environment. Then resume M5 audio plan (docs/M5-AUDIO-PLAN.md) and stop bisecting.
- both pass => host load/time-of-day flake; note and resume M5.
HYPOTHESIS-ID: m3-idiom-class-audit
