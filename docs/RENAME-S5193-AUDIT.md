# Session 5193 symbol audit

Candidate: `__osSiRawReadIo = 0x80033C00`

The bounded generated-tree search found no `__osSiRawReadIo`,
`func_80033C00`, or `fake_func_80033C00` reference in `funcs_*.c`, `funcs.h`,
or `recomp_overlays.inl`. The bounded rename helper reported
`already-synchronized` and changed zero references in zero files.

Classification: unmaterialized libultra/ABI entry. There is no generated body,
placeholder, overlay record, or direct generated caller at the companion
address. The symbol map places `__osSiRawWriteIo = 0x80033C50` next, giving a
nominal `0x50` span, but there is no body to validate. Preserve the ABI name;
the rename gates cannot be satisfied.

This is single-source generated-tree evidence plus the helper's independent
zero-edit decision. No runtime build or soak was warranted for a naming-only
classification.
