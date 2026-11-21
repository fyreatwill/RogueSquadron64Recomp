# NEXT (s7741)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7740. s7740 made the s7719 regen gate strict (live == fresh replay byte-for-byte; replays
deterministic; RED on a planted comment line that s7423 cannot see). Any hand edit to ../N64Recomp/RecompiledFuncs now reds the
sweep: put such edits in a fixup/apply script registered in RS64_REPLAY.

Candidate bounded item if nothing above applies: the same strictness for build/factor5_ucode (the ucode regen). H-zero
(`tools/ucode_regen.sh verify` output == live factor5_ucode byte-for-byte -> add a strict byte compare with a planted-line
control to that gate) vs H-drift (files differ -> classify each row: a fixup_factor5_ucode.py step missing, or a hand edit to
fold into the fixup). Proof: strict GREEN on the live ucode tree, RED with a planted line in a scratch farm, wired into the sweep.
