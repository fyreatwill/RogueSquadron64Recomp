# NEXT (s7316): backlog item 14 - next open ITERATION.md 3c rung
HYPOTHESIS-ID: generated-symbol-renaming-sweep
Context: CURRENT-TRUTH Next steps 1-11 are owner looks/decisions or closed; 12 (harness one-game) closed s7314; 13 (retail RAM-bound
idiom class) closed s7315.
1. First check SOAK-RESULTS for any "leftover"/"foreign game killed"/"outlived" line (s7314 guard): if present, name which arm/tool
   failed to reap its game and fix that tool (this outranks everything below).
2. Otherwise pick another nameable idiom class to audit (iron rule 14 prefers it to a bare rename). Candidate: retail pointer
   tests on DATA-word bounds (the s7315 method limit): grep `lw` of heap-end/arena-top globals (rs_malloc arena end, 0x801163E4
   FB-partition top written by partitionFramebufferMemory 0x80000ED8) followed by sltu against a pointer; classify every site,
   and check that the spill arena (0x80800000/0x81000000) is not rejected. H-reject (a site treats spill pointers as invalid)
   vs H-clean. Discriminator: per-site static read; for any H-reject site, a same-binary dd2 vs dd1 log of the branch.
3. If no class is nameable: renaming sweep (tools/apply_symbol_renames.py, s7080), next address-ordered batch, two lines of
   evidence per name, regen make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake, boot to attract as control.
