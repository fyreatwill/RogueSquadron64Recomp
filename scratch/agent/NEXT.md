# NEXT work unit (after s712: fetch-pointer lifecycle has no stale/reload edge)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Perform one bounded static command-dispatch/advance audit for backlog item 1.
Map every Factor 5 command-table entry which can reach a `r17` advance to its
generated label and compare its total advance (including conditional inline
data) with `docs/F5-UCODE-REFERENCE.md`.  s712 closed a stale root or
unmodelled return as the cap mechanism; this unit tests decode
desynchronization directly.  Do not rerun the recovery recipe: s694--s696
exhausted unchanged unqualified rerolls.

## Competing hypotheses

- **H-advance-conformant:** every mapped command has the reference advance;
  the capped stream is not caused by a generated Factor 5 pointer bug.
- **H-advance-mismatch:** a mapped inline-data command resumes at the wrong
  address, manufacturing the long command chain that reaches the cap.
- **H-dispatch-table-opaque:** a cap-reachable table entry is dynamically
  populated or cannot be mapped to a generated handler, so static mapping is
  incomplete and the next unit must capture that entry at runtime.

## Discriminating measurement

Record one complete table of Factor 5 command opcode, command-table target,
generated label, `r17` writes/total advance, and reference advance.  Positive
control: the table must account for every static write to both dispatch tables
(`DMEM[0x64]` and `DMEM[0xD6]`) and every one of the six reference inline-data
commands.  Any unequal advance selects H-advance-mismatch; an unmappable or
runtime-populated entry selects H-dispatch-table-opaque; a complete equal table
supports H-advance-conformant and rules out this generated-pointer class.

## Commands

    rg -n -C 5 'RSP_MEM_H_(STORE|LOAD).*0X(64|D6)|0X64|0XD6|L_10C8:|L_1090:' \
      build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'MoveMem|TriGen|Tri\b|TexrectGen|SetOtherMode|inline data|Opcode' \
      docs/F5-UCODE-REFERENCE.md
    rg -n -C 4 'r17 = RSP_ADD32\(r17' \
      build/factor5_ucode/factor5_ucode_recompiled.c

Append the complete table and verdict to `docs/F5-UCODE-REFERENCE.md`.  If
the generated advance is wrong, correct its regeneration-safe fixup in
`tools/fixup_factor5_ucode.py`, regenerate, and run the existing phase-gated
controls in that same iteration.
