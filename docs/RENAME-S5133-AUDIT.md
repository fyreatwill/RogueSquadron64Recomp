# Session 5133 rename audit

Candidate: `__osDisableInt = 0x8002C240`.

The bounded helper was run over `0x8002C240..0x8002C500` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `__osDisableInt`, `__osRestoreInt`, `osInvalDCache`, `osInvalICache`, and
`osJamMesg`.

Independent generated-tree inspection found the ABI declaration and one
generated caller at `funcs_24.c:7167`, but no generated function body or
placeholder to rename. The overlay table records
`__osDisableInt_recomp` at offset `0x2BE00` with `rom_size = 0`, matching a
host-wrapper/ABI-boundary entry. Preserve the ABI name; no build or soak is
needed.
