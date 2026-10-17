# Next: read the SOAK-RESULTS.md line for s5243_envflag_ab (keys.log in scratch/agent/soak_results/s5243_envflag_ab/).
A pass + B fail => one of the five ROGUESQ_LOG_*GUARD* flags changes the route; bisect the flags in one sequential script and find why a log flag has behaviour.
A pass + B pass => flake/timing; re-queue the TO_PTR mask regression (maskon vs maskoff) with the s5099 env (BASE only).
A fail => positive control failed: HEAD code or host regressed the route; check uptime, then bisect commits s5229..s5240 via builds.
If clean, resume M5 audio plan (docs/M5-AUDIO-PLAN.md) next de-stub step.
HYPOTHESIS-ID: m3-idiom-class-audit
