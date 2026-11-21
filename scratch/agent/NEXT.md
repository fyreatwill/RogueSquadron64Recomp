# NEXT (s7738)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7737 census/replay passes (s7737: DIAG consumer census H-none, wired into the s7719 gate; 2 stale
s6826 TICK_TRACE menu hooks accepted).

Candidate bounded item if nothing above applies: the live tree has drifted from the replay in diagnostic-only ways (stale s6826 menu
hooks, duplicate s6314 block, orphan funcs_50.c, 16 data_gap funcs). Question: H-swap-safe (building from the s7736 replay tree gives
the same owner behaviour: same-run A/B on L4 owner recipe, both builds, present-ring stalls + crash count + framebuffer at a fixed
phase) vs H-hidden-dep (something in the build depends on a live-only symbol: link error or behaviour change). Cheap first step: link
a build dir against scratch/s7736/gate/replay (separate build dir, never touch build/) and record link errors. Only then an A/B soak.
