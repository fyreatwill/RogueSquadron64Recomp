# NEXT (s7744)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7743. s7743 = overlay ucode files are fixup inputs + s7091 oracle (tools/s7743_ovl_consumers.py,
in the sweep). Do not delete them.

Candidate bounded item if nothing above applies: CURRENT-TRUTH is ~59.6 KB, just under the 60 KB maintenance trigger and far over
the ~35 KB cap. Next iteration that finds it >60000 is maintenance; otherwise take the first open ladder rung (ITERATION 3c) whose
item is not "owner look" - e.g. a G6c stand-ins coverage check at dd4 on a level not yet sheeted - and write the hypotheses first.
