# Next: M3 idiom list exhausted after s5349 — check M5 status before any rename step

Check docs/M5-AUDIO-PLAN.md status (ITERATION.md priority 2) and execute the next un-run de-stub step with its validation soak. If M5 is closed, run `grep -n '^## Session ' PORTING-STATE.md | tail -15` for the sweep-revisit rule (priority 4). Prefer an M5 de-stub or a new guard-class audit over a rename step (renames trip the churn counter).

HYPOTHESIS-ID: m5-audio-destub-or-sweep
