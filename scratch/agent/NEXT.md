# Next work unit: read s5442_post_a/b verdicts (mission-transition endurance)
HYPOTHESIS-ID: m6-flown-render-fidelity

s5441 closed: log cap works (var_d/e run.log 65 MB vs 905 MB; crashlines=0 vi_stalls30s=0, 5/5 var soaks clean).
Queued m6_post_late_a/b (LATE=200, 480 s hold): the results-screen a/start presses begin early so a briefing->flight->hangar transition lands inside the hold.
- Read SOAK-RESULTS.md tail + scratch/agent/m6/s5442_post_*/summary and keys.log.
- Clean x2 (crashlines=0, vi_stalls30s=0, VI origin changes across the transition): transition endurance is 2/2; move to the title-boot plume SIGSEGV (si_addr=0x58) loop.
- Any CRASH/stall: ASan arm in a separate build dir for a backtrace, name writer, root-cause fix.
