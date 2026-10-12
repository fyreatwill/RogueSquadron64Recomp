# Next work unit

HYPOTHESIS-ID: m5-b40-gate-default

s4701 flipped the B40 default to pass-through (0/7 crash vs B40=0 1/2). Remaining: confirm on a longer soak, then take the next M5 de-stub.
Unit: enqueue scratch/agent/soak_queue/s4701_b40_default_long.sh (based on run_s4701_b40_default.sh, 3 default arms, longer window, exit nonzero on any CRASH row), read the SOAK-RESULTS line. If 0 crashes in >=6 arm-runs, close the crash family in CURRENT-TRUTH and do the next step in docs/M5-AUDIO-PLAN.md (survey remaining audio stubs now the MusyX gate is on).
Outcomes: a crash with the s4457-bad / far=0x38000950e signature => B40 is not the whole story (stale-callback path remains); a different signature => new family.
