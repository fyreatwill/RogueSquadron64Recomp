# Session 5195 symbol audit — `proutSprintf`

Candidate: `proutSprintf = 0x80033CA0`.

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found a
generated body in `RecompiledFuncs/funcs_8.c` beginning at `0x80033CA0` and
ending at the `jr`/delay-slot pair at `0x80033CC0`, so the body span is
exactly `0x24` bytes. `recomp_overlays.inl` independently records
`proutSprintf` at offset `0x33860` with `rom_size = 0x24`, followed by
`sprintf` at `0x80033CC4`.

The generated tree has no independent caller for `proutSprintf`; the only
match is its definition. This is a correctly named libultra/ABI entry, not an
actionable placeholder rename. Preserve the name and continue at
`sprintf = 0x80033CC4`.
