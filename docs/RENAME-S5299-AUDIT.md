# Session 5299 symbol audit

Candidate: `relinkNpcSlotToNewParentGroup = 0x8003EFDC`.

The companion symbol file defines the named callable at that address. The
bounded rename helper, run over the one-address range with `python3`, reported
`already-synchronized` and renamed zero references in zero files. Independent
searches of the generated tree found the named body in `funcs_8.c`, its
declaration in `funcs.h`, its overlay record in `recomp_overlays.inl`, and
direct callers. No `func_8003EFDC`, `fake_func_8003EFDC`, or conflicting
callable/data fragment was found.

Conclusion: preserve the existing name. This work unit required no build or
soak.
