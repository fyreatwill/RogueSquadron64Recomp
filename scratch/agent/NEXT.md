# NEXT (s7315): backlog item 13 - next open ITERATION.md 3c rung
HYPOTHESIS-ID: generated-symbol-renaming-sweep
Context: CURRENT-TRUTH Next steps 1-11 are owner looks/decisions or closed; 12 (harness one-game) CLOSED s7314.
1. First check SOAK-RESULTS for any "leftover"/"foreign game killed"/"outlived" line (s7314 guard): if present, name which
   arm/tool failed to reap its game and fix that tool (this outranks the sweep).
2. Otherwise per ITERATION.md item 4: `grep -n '^## Session ' PORTING-STATE.md | tail -15`; if all 15 are sweep titles do the
   REVISIT instead. Else resume the renaming sweep (tools/apply_symbol_renames.py, s7080): count remaining func_0x... names,
   take the next address-ordered batch, confirm each name from the code (two lines of evidence: callers + body), regen in order
   make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake, build, boot to attract as the positive control.
   Note iron rule 14: a rename-only iteration counts as no engineering change; prefer pairing it with an idiom-class audit
   (grep-enumerate one class, classify every site, guard or prove dead) if one is nameable.
