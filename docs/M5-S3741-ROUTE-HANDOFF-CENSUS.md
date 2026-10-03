# M5 session 3741 — qualified-route predecessor and handoff census

The independent retail oracle was run before the port build. Its whole-RDRAM
positive control fired 200 times, and it reached title `1024 @ 0x00790400`
and hangar `512 @ 0x006AB400`. The shortened preliminary oracle run was
discarded because it stopped before hangar; the fixed run reached both phases.

The rebuilt port capture enabled the existing route-candidate, route-prepare,
and route-handoff hooks in the same real-audio/silent pair. Both port arms
reached title; the real arm also reached hangar. The real arm produced 512
qualified source-range DMA rows, all with `0x1798B0 -> DMEM 0xCB0`,
`FNV=0x762B22A5`, and `payload_nz=0`. The silent arm produced no source-DMA
rows. There were no crashes or aborts.

At both target origins, the first qualified route-preparation rows at
`0x80019CD8` reported `source_word=0`, `source_byte=0`, and
`branch_state=0`. The actual route handoff called from `0x8000C628` with
`s0=0`, `a0=0`, `a1=0`, `a2=1`, and `v0=0`, followed by an entry with the
same zero value fields. This was repeated in both title and hangar; the
shared setup call with `s0=0x80790000` and `a0=0x1C0` is a separate earlier
edge and is not the qualified source producer.

This selects `H-RouteHandoffValueAbsent` for the measured route edge. It rules
out `H-RouteHandoffDropsValue` at this edge because no nonzero predecessor
value was observed, and rules out `H-RouteHandoffAfterClear` at this edge
because the handoff was already zero before the zero source DMA. The result
does not identify the earlier legitimate writer of the zero state and does
not authorize suppressing `0x800078EC`.

Evidence: `scratch/agent/s3737_m5_retail_writer_join_fixed/` and
`scratch/agent/s3741_oracle_groundtruth/oracle_fixed.log`.
