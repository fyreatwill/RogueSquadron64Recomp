# M5 Session 3670 — remaining source-span stores are initialization

The corrected retail-oracle capture retained the whole-RDRAM positive control,
all four descriptor watches, title and hangar VI controls, and the type-2 task
control. It reached 3043 VI (`~50.7` emulated seconds), recorded 299,812
whole-RDRAM writes, 674 source-span writes, and 820 valid type-2 task rows with
zero invalid pointers or overflow.

The bounded exact-store arm covered all 290 non-primary source-span stores:
`0x80007670` 172, `0x8001E2C0` 11, `0x8001FACC` 11,
`0x8001FADC` 11, `0x8001FAE4` 11, `0x8001FAEC` 10,
`0x8001FAF0` 11, `0x8001FAF8` 11, `0x8001FB10` 11,
`0x8001FB14` 11, `0x8001FBE4` 10, and `0x8001FD2C` 10.
There was no row overflow.

Independent static disassembly identifies `0x80007670` as the `sb` in
`rs_strncpy`, which writes zero padding after a source string terminates. The
`0x8001FAxx`/`0x8001FBxx` sites populate a texture-data table record and the
`0x8001FBE4`/`0x8001FD2C` pair writes adjacent record fields. The exact-store
contexts match those roles: the `0x80007670` rows use decrementing byte counts
and destinations across the source span, while the smaller sites use fixed
record-field offsets and table-derived bases.

This selects `H-RemainingInitialization` for the 290 stores and refutes their
being object-specific audio payload owners. It does not expose the source-DMA
ordering or prove which later task consumes each initialized record. The
oracle evidence is independent of the port; the static interpretation is a
second line of evidence for the instruction roles.

ORIGIN: diagnostic-only retail execution and physical-write watches; no guest
or host state was rewritten, skipped, or guarded.

Evidence: `scratch/agent/s3670_m5_remaining_store_join/oracle.log`,
`scratch/agent/run_s3670_m5_remaining_store_join.sh`, and the companion
generated disassembly around `rs_strncpy` and the texture-data record writer.
