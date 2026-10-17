# Generated-symbol audit — Session 5306

Candidate: `findFirstActiveNpcChildInChain = 0x8003FCBC`.

The bounded helper reported `already-synchronized` and renamed zero references
in zero files. Independent inspection found the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, its declaration in `funcs.h`, and the
overlay record in `recomp_overlays.inl`. There was no
`func_8003FCBC` placeholder or conflicting generated fragment. No direct named
caller was found in the generated tree; the function remains a valid overlay
entry.

Conclusion: H1 is selected; H2 and H3 are ruled out. No build or soak was
warranted. The next bounded candidate is
`destroyNpcContextArrays = 0x8003FDD8`.
