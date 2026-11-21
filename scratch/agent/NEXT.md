# NEXT (s7770)
HYPOTHESIS-ID: generated-symbol-renaming-sweep
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines. A recurrence of the FPS60 half-rate (item 29, closed s7769): run
`python3 tools/s7769_ring_genrate.py <ring>` and `python3 tools/s7768_fps60_rate.py <log>` on it before anything else.
Otherwise every ladder rung (G1-G6) is closed or awaiting the owner's look, so take strategic item 4 (renaming sweep):
1. `grep -n '^## Session ' PORTING-STATE.md | tail -15` - if all 15 are sweep sessions this is a REVISIT (see ITERATION item 4).
2. Count remaining placeholders: `grep -c 'func_0x' tools/rename*` / the generated symbol list; pick the 20 most-called
   func_0x... (callers from RecompiledFuncs), name each from its body + callers, two lines of evidence per name.
3. Regen order make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake; `python3 tools/s7719_regen_gate.py --strict` and the
   sweep must stay GREEN. Note: a rename-only iteration counts as churn for the pivot counter - pair it with a code/tool change.
Do NOT queue more FPS60 rate, latency, coverage or crash-hunt soaks.
