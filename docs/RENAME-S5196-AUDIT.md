# Session 5196 symbol audit — `sprintf`

Candidate: `sprintf = 0x80033CC4`.

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. The companion `libultra.txt` symbol map independently
names `0x80033CC4` as `sprintf`. The generated tree contains the
`sprintf_recomp` body in `RecompiledFuncs/funcs_8.c`, beginning at
`0x80033CC4`; its return sequence ends at `0x80033D1C`, giving an exact
`0x5C` span. `recomp_overlays.inl` independently records
`sprintf_recomp` at offset `0x33884` with `rom_size = 0x5C`, followed by
`_VirtualToPhysicalTask` at `0x80033D20`.

The generated tree contains many independent `sprintf_recomp` call sites in
addition to its definition. This is a correctly named libultra/ABI entry, not
an actionable placeholder rename. Preserve the name and continue at
`_VirtualToPhysicalTask = 0x80033D20`.

No runtime build or soak was warranted for this naming-only classification.
