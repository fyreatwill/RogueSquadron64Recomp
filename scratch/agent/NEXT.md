# NEXT (s7712)
HYPOTHESIS-ID: owner-items-standing

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8 (s7709 gate).

s7711 closed the documented-VALUE census statically (tools/s7711_optval_census.py, 127/127, gated). It is single-source.
Candidate bounded unit: the RUNTIME witness for it. One boot (title only, ~40 s, SIGKILL; owner save read-only as runner.sh
exports) with documented non-trivial values set at once, e.g.
  env ROGUESQ_STICK_GATE=95,80 ROGUESQ_RUMBLE_SCALE=0.5 ROGUESQ_DD_FOG_ALT=1,3,1 ROGUESQ_DRAW_DISTANCE=6 ROGUESQ_DD_UNSAFE=1 \
      ROGUESQ_G5G_LENS=34 ROGUESQ_OSMEM_MB=12 ./RogueSquadron64Recomp   (from build/, ROM beside it)
and grep the readers' own parse prints ([stick-gate] card=95 diag=80, [s7302] fog alt ks=1 ke=3 all=1, [s7358-env], [g5g], ...).
Control: a second arm with a planted bad value (STICK_GATE=95 alone -> must print card=85, i.e. the census's "list" rule is real).
Hypotheses: H-clean (prints match the static verdicts), H-late (a reader runs before settings apply / re-exec, so the value is
not seen), H-print-lies (the print shows the raw string, not the parsed value). Two arms in one iteration (iron rule 13).
Otherwise take the first open G-rung in ITERATION.md 3c not waiting only on the owner (Next steps item 4: do not flip defaults).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2` (expect 132 GREEN, 0 RED).
