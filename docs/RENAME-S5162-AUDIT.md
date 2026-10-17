# Session 5162 symbol audit

Candidate: `__osPfsRequestOneChannel = 0x80030944`

The bounded generated-tree search found no `__osPfsRequestOneChannel`,
`func_80030944`, or `fake_func_80030944` reference in `funcs_*.c`, `funcs.h`,
or `recomp_overlays.inl`. The bounded rename helper reported
`already-synchronized` and changed zero references in zero files.

Classification: unmaterialized libultra/ABI entry. There is no generated body,
placeholder, overlay record, or direct generated caller at the companion
address. Preserve the ABI name; the rename gates cannot be satisfied.

This is single-source generated-tree evidence plus the helper's independent
zero-edit decision. No runtime build or soak was warranted for a naming-only
classification.
