# Generated-symbol audit — Session 5309

Target: `destroyTransientNpcSlots = 0x8004028C`.

The bounded helper reported `already-synchronized`, with zero references
renamed in zero files. Independent inspection found the companion
`main_overlay.txt` entry, the named `RECOMP_FUNC` body in `funcs_9.c`, the
declaration in `funcs.h`, the overlay record in `recomp_overlays.inl`, and a
named caller. No generated `func_8004028C` placeholder or conflicting fragment
was present.

Conclusion: H1 is selected. Preserve the existing name; no generated source or
fixup mapping changed. H2 and H3 are ruled out for this candidate.
