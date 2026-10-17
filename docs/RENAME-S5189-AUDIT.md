# Session 5189 symbol audit

Candidate: `__osSiGetAccess = 0x800338F0`

The bounded generated-tree search found no `__osSiGetAccess`,
`func_800338F0`, or `fake_func_800338F0` reference in `funcs_*.c`, `funcs.h`,
or `recomp_overlays.inl`. The bounded rename helper reported
`already-synchronized` and changed zero references in zero files.

Classification: unmaterialized libultra/ABI entry. There is no generated body,
placeholder, overlay record, or direct generated caller at the companion
address. The symbol map places `__osSiRelAccess = 0x80033934` next, giving a
nominal `0x44` span, but there is no body to validate. Preserve the ABI name;
the rename gates cannot be satisfied.

This is single-source generated-tree evidence plus the helper's independent
zero-edit decision. No runtime build or soak was warranted for a naming-only
classification.
