# Session 5295 symbol audit

Candidate: `reinsertNpcIntoSortedFreeList = 0x8003EC10`.

The companion symbol file defines the named callable at that address. The
bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found
the named body in `funcs_8.c`, its declaration in `funcs.h`, its overlay record
in `recomp_overlays.inl`, and direct callers. No `func_8003EC10`,
`fake_func_8003EC10`, or conflicting callable fragment was found.

Conclusion: preserve the existing name. This work unit required no build or
soak.
