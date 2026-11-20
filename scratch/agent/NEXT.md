# NEXT (s7708)
HYPOTHESIS-ID: loop-contract-carryover

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.

Context: s7707 found the census gate sweep RED 13 for five sessions (s7702-s7706). stop_gate --verify blocked every one of them, but
tools/agent/loop.sh:690 breaks out after MAX_CONTRACT_RETRIES=2, logs "contract still unmet", and the next iteration starts with no
signal that a contract is still owed (NEXT.md is agent-written and did not mention it).

Work unit (bounded tooling change):
1. In loop.sh, when the contract is still unmet after the retries, write the verdict to scratch/agent/CONTRACT-CARRY.md (overwrite).
   At the start of the next iteration, if that file exists, prepend "## Unmet contract from the previous iteration (fix FIRST)" plus
   its content to the prompt; delete it once stop_gate --verify passes.
2. Test: extend or add tools/agent/test_*.sh with a fake stop_gate that fails twice then passes: file is written after the first failed
   iteration, appears in the second prompt, is removed after a pass. Mutation control: drop the prepend -> test fails.
Hypotheses: H-carry (the carry file makes the next iteration fix the gate: test passes) vs H-noise (retries already show the verdict and
the agent ignored it; then the carry needs to be a hard block in stop_gate instead: decide by reading the s7702-s7706 retry prompts in
loop.log around line 942316).
If done early: run `python3 tools/s7651_gate_sweep.py --jobs 2` (expect 130 GREEN, 0 RED).
