# NEXT work unit (after s729 maintenance: compact `0x06` provenance retained in PROJECT-OVERVIEW §28)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Statically audit the complete `0x06` display-list dispatch/push idiom that
feeds the cap rows. This is one bounded enumeration/classification work unit;
do not rerun the L_1DB0 continuation capture.

## Competing hypotheses

- **H-dl06-legitimate-chain:** every cap-reachable push is the documented
  `0x06 → L_12A0` child-DL path, with a paired EndDL parent restore; cap rows
  represent a legitimate-but-unbounded command chain.
- **H-dl06-unpaired-site:** one generated dispatch or indirect return site can
  push a child without the documented parent-PC/frame lifecycle.
- **H-dl06-opaque-overlay:** a DMA-populated dispatch-table entry reaches a
  push-like path not visible in the resident generated code.

## Discriminating measurement

Enumerate every generated call/jump into `L_12A0`, every producer of its
caller/return target, and every `0x654+depth` save/restore access. Join each
site to the Factor 5 reference's `0x06`/EndDL lifecycle. A complete finite
table with only the documented dispatcher push and `L_12C4/L_12DC` restore
supports H-dl06-legitimate-chain and refutes the other two; any extra entry,
unpaired frame access, or DMA-table-only push selects its matching alternative.
This static result needs the independent command reference as its second line
of evidence; do not call it a runtime explanation without a later qualified
cap-row trace.

Expected outcomes: the sole documented push plus paired `L_12C4/L_12DC`
restore closes H-dl06-unpaired-site and H-dl06-opaque-overlay for generated
code; any additional site keeps the matching hypothesis open and names the
next bounded trace. Before any build, retain these hypotheses and this
discriminator in this file as required by the iteration contract.

## Commands

    rg -n -C 8 'L_12A0:|goto L_12A0|r31 = 0x12A0|0X654|0x654|L_12C4:|L_12DC:' build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 5 '0x06|F3DSWRS_DList|EndDL|L_12A0|L_12C4|L_12DC' docs/F5-UCODE-REFERENCE.md docs/CURRENT-TRUTH.md
    rg -n 'L_12A0|L_12C4|L_12DC|0X654' tools/fixup_factor5_ucode.py
