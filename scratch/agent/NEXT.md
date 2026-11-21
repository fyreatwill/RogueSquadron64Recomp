# NEXT (s7742)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7741. s7740 = strict RecompiledFuncs regen gate; s7741 = strict ucode regen gate
(tools/s7741_ucode_regen_gate.py --controls, in the sweep). Any fixup_factor5_ucode.py edit must be followed by
`zsh tools/ucode_regen.sh snapshot` or the sweep reds.

Candidate bounded item if nothing above applies: does fixup_factor5_ucode.py's own output still match the live tree on the file
it CAN rebuild? H-same (run the fixup on a copy of the snapshot-regenerated tree: idempotent, 0 diff) vs H-nonidempotent (it
re-applies a block -> a regen that runs the fixup after restore double-inserts; classify rows). Proof: diff count on a scratch copy
with a planted pre-fixup file as a positive control (fixup must change it).
