# M5 Session 3568 — source-range producer census

The existing regeneration-safe source-range hooks were run on one standalone
image arm from `build/`, using the validated real-audio/LLE-solo/spin-yield/
autopilot route. The oracle was checked first, but the debugger-enabled
`libmupen64plus.dylib` was absent in this checkout, so this result is port-only.

The run reached title VI 1024 at origin `0x00790400` and hangar VI 512 at
origin `0x006AB400`. The RSP-source positive control fired in both phases
(`source_control=2`, `source_rows=1024`), and the source-range DMA-writer
instrument fired in hangar (`writer_rows=512`). No crash marker appeared.

In hangar, the first writer rows were:

```text
route_ordinal=1196: dmem_to_rdram dram=0x1798B0 len=0x198 dmem=0xCB0 payload_nz=0 post_nz=0
route_ordinal=1197: dram=0x1797B0 len=0x30 dmem=0xC30 payload_nz=0 post_nz=0
route_ordinal=1197: dram=0x1798B0 len=0x198 dmem=0xCB0 payload_nz=0 post_nz=0
```

The same pattern continued through the capped table: the DMA payload and
post-write source-range bytes were zero. The corresponding later
`m5-rsp-source` rows read `0x1797B0` and `0x1798B0` with zero hashes and zero
nonzero counts. CPU source-range candidates and source-range memset rows were
absent (`candidate_rows=0`, `memset_rows=0`); phase and RSP controls were live,
so these nulls are evaluable for this route.

This selects `H-SourceRangeOtherDma` as the immediate writer: a
`dmem_to_rdram` image/audio-task writeback overwrites the source span before a
later RDRAM-to-DMEM read. It refutes a matching immediate CPU writer and a
stale-only explanation at this boundary. It does not identify the producer of
the zero DMEM payload consumed by that writeback; that is the next boundary.
No behavior change was made.

