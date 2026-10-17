# Generated-symbol audit — Session 5305

Candidate: `freeNpcSlotArray = 0x8003FBF8`.

The bounded helper reported `already-synchronized` and renamed zero references
in zero files. Independent inspection found the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, its declaration in `funcs.h`, the
overlay record in `recomp_overlays.inl`, and a direct caller in `funcs_42.c`.
The body starts at `0x8003FBF8` and the overlay record has size `0x30`.
There was no `func_8003FBF8` placeholder or conflicting generated fragment.

Conclusion: H1 is selected; H2 and H3 are ruled out. No build or soak was
warranted. The next bounded candidate is
`findFirstActiveNpcChildInChain = 0x8003FCBC`.
