# NEXT (s7737)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7736 census/replay passes (s7736: the 18 live-only readers split; s6201 g1d-alloc restored to RS64_REPLAY,
13 accepted dead text).

Candidate bounded item if nothing above applies: the same order-dependent anchor failure (an inline fixer apply_* call returning 0
silently because a later patch changed its anchor) may hit other inline calls. Discriminator: in fixup_game_funcs_vendored.py, list
every inline `text, _nX = _aY.apply...(text)` call whose report line ("<file>: sNNNN ... xN") is ABSENT from a fresh replay log
(scratch/s7736/gate/replay.log) while its PATCH tag IS present in the live tree. H-none (0 such calls) vs H-more (each one is a probe or
fix the next regen loses; restore it like s7736). The reverse scan's DIAG/REGEN-FUNC rows are where the hits would show.
