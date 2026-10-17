# Session 5132 rename audit

Candidate: `__osGetSR = 0x8002C230`.

The bounded helper was run over `0x8002C230..0x8002C500` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `__osGetSR`, `__osDisableInt`, `__osRestoreInt`, `osInvalDCache`,
`osInvalICache`, and `osJamMesg`.

The independent generated-tree inspection found no candidate placeholder, no
generated body or declaration, no overlay record, and no direct generated
caller for `__osGetSR`. The companion map places the next entry at
`__osDisableInt = 0x8002C240`; the generated overlay table has no record for
the candidate range. This is a host-wrapper/ABI-boundary or unmaterialized
libultra entry. Preserve the existing ABI naming; no build or soak is needed.
