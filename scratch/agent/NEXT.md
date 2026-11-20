# NEXT (s7709)
HYPOTHESIS-ID: loop-contract-carryover

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If scratch/agent/CONTRACT-CARRY.md exists it heads your prompt: fix that first (s7708).

Work unit (bounded tooling change): agent-tooling tests are run by hand only, so a loop.sh edit can break the soak gate, crash gate or
the s7708 carry without anyone noticing.
1. Add tools/agent/run_tests.sh: runs every tools/agent/test_*.sh, prints one PASS/FAIL line each, exits nonzero on any FAIL.
2. In stop_gate.sh (NOT the hook config, CLAUDE.md rule): if the iteration's diff touches tools/agent/*.sh or *.py, require
   run_tests.sh rc 0 (verdict "agent tool tests FAIL: <names>").
3. Controls: plant a failing test in a temp copy -> gate verdict names it; clean tree -> gate passes.
Hypotheses: H-green (all 7 current tests pass as they stand, the gate just adds coverage) vs H-rot (some test already fails on the
current loop.sh / stop_gate: fix the test or the tool it caught, which is the bigger find).
Then: `python3 tools/s7651_gate_sweep.py --jobs 2` (expect 130 GREEN, 0 RED).
