# NEXT (s7743)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7742. s7742 = fixup_factor5_ucode.py contract gate (tools/s7742_fixup_idem_gate.py --controls).
Any fixup_factor5_ucode.py edit: rerun that gate and s7741; if live output changes, `zsh tools/ucode_regen.sh snapshot`.

Candidate bounded item if nothing above applies: the 9 overlay ucode files (factor5_ucode_ovl*_recompiled.c, their tomls, and the
ovl20 patch in tools/ucode_fixed) are not compiled (s7742: no reference in CMakeLists.txt or src/). H-dead (nothing consumes them;
only the regen gates carry them) vs H-tool-input (an offline census, e.g. s7093/s7507/s7508/s7509, reads them as its oracle, so they
must stay byte-true). Measure: grep every tools/*.py for ovl file names + run the censuses with the overlays moved to a temp
dir (positive control: a census that lists them must change output). Report only; deleting them is an owner-scale decision.
