# NEXT (s7711)
HYPOTHESIS-ID: owner-items-standing

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8 (s7709 gate).

s7710 closed the owner-setting NAME census (tools/s7710_optins_census.py, gated). Candidate next bounded owner-facing unit:
the VALUE side - for each OWNER-OPT-INS row that shows `ROGUESQ_X=V`, check the code's parser accepts V with the documented
meaning (e.g. ASPECT 16:9/21:9/auto, RUMBLE_SCALE 0..2, DRAW_DISTANCE 2/4/8, =0 restores old). Hypotheses: H-clean, H-syntax
(a documented value is rejected or clamped to something else), H-default (an "=0 old" lever's 0 is not the old path).
Discriminator: launch-free where possible (a unit harness over the parse helpers, like tools/test_settings.cpp), else one
build with a `[s7711] parsed` print per variable and one boot per documented value set, with a planted bad value as control.
Otherwise take the first open G-rung in ITERATION.md 3c not waiting only on the owner (Next steps item 4: do not flip defaults).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2` (expect 131 GREEN, 0 RED).
