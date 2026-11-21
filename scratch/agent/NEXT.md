# NEXT (s7739)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything), then any owner
report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, background, CPU cap 2).

Closed, do not repeat: s7726-s7738 census/replay passes. s7738: the s7736 replay tree links (tools/s7738_link_replay.sh) and plays
L4 like live (H-swap-safe); build_replay/RogueSquadron64Recomp is that binary.

Candidate bounded item if nothing above applies: ADOPT the replay as the live tree, so the drift (stale s6826 hooks, double s6314
EDGE_FADE_TEST2 block, funcs_50.c, data_gap funcs, always-on [desc-st] print) disappears. Hypotheses: H-clean (fresh regen in the
hard order make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake reproduces the s7736 replay byte-for-byte and the gate sweep
stays GREEN) vs H-new-drift (the live regen differs from the replay: diff the trees before building). Back up
../N64Recomp/RecompiledFuncs to scratch/s7739/live_backup first (it is outside git). Proof: tree diff = 0 vs replay, build/ rebuilt,
gate sweep GREEN, one L4 + one L1 owner-recipe hold alive 0 crash 0 stall. Do not touch build/saves.
