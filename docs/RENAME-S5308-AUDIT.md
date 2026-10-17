# Generated-symbol audit — Session 5308

Candidate: `spawnNpcWithSubtype = 0x8003FE9C`.

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent inspection found the companion
`main_overlay.txt` record, the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, its `funcs.h` declaration, and its
`recomp_overlays.inl` entry. A named caller in `funcs_15.c` invokes the same
symbol. No `func_8003FE9C` placeholder or conflicting generated fragment was
found.

This selects H1 (already synchronized) and rules out H2 (placeholder rename)
and H3 (typed data or ABI-boundary preservation). No build or soak was
warranted.
