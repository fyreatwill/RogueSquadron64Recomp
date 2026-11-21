# NEXT (s7740)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7739. s7739 adopted the regen replay as the live tree (live == replay byte-for-byte, sweep GREEN,
L4/L1 holds clean). Old tree in scratch/s7739/live_backup (restore recipe in tools/s7739_adopt_replay.sh header).

Candidate bounded item if nothing above applies: make the s7719 regen gate STRICT now that the baseline is zero. Since s7739 the
s7423 class counts are {} in both directions, so any non-empty class count (or any `diff -rq` line between live sources and the fresh
replay) means someone hand-edited the live tree or a fixup stopped reproducing. H-zero (a fresh gate run still shows {} / 0 lines ->
add a strict mode that fails on ANY row, with a planted one-line live edit as the positive control) vs H-nondeterministic (two
replays differ, e.g. ordering/timestamps -> fix the source of nondeterminism first). Proof: gate strict mode GREEN on the live
tree, RED with the planted edit (restored after), wired into the sweep.
