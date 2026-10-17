# Session 5134 rename audit

Candidate: `__osRestoreInt = 0x8002C260`.

The bounded helper was run over `0x8002C260..0x8002C500` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `__osRestoreInt`, `osInvalDCache`, `osInvalICache`, and `osJamMesg`.

Independent generated-tree inspection found the ABI declaration and one
generated caller at `funcs_24.c:7201`, but no generated function body or
placeholder to rename. The overlay table records
`__osRestoreInt_recomp` at offset `0x2BE20` with `rom_size = 0`, matching a
host-wrapper/ABI-boundary entry. The companion map independently places the
next entry at `__osLeoInterrupt = 0x8002C500`.

Classification: host-wrapper/ABI boundary or unmaterialized libultra entry;
preserve the ABI name. No build or soak is needed.
