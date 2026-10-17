# Session 5123 rename audit: `osCreateMesgQueue`

Candidate: companion symbol `osCreateMesgQueue = 0x8002B300`.

The companion map marks the symbol as defined, but the generated snapshot has
only the ABI declaration and 28 calls from 9 generated files. Its overlay entry
at offset `0x0002AEC0` has `rom_size = 0x00000000`; no generated prologue/body
or exact generated span exists to rename. The next companion entry is
`osCreateThread = 0x8002B330`.

The bounded rename helper reported:

```text
renamed 0 references in 0 files
candidate 0x8002B300 osCreateMesgQueue: already-synchronized
```

This selects the host-wrapper/ABI-boundary outcome. Preserve
`osCreateMesgQueue_recomp`; no source rename, build, or soak was warranted.
Independent companion-map, generated-tree, overlay-record, and caller-count
checks agree.

