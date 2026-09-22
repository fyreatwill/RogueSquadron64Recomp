# M5 s3691 — stale input payload boundary

The independent retail control reached title and hangar. Its whole-RDRAM
watch visibly fired 960 times, and the hangar phase produced 15 type-2 task
rows. Narrow memory watches were armed but remained non-observable under the
oracle memory-write callback; they are not used as null evidence.

The qualified port run used real-audio and silent arms in one build/run. The
real-audio arm reached 512 hangar source rows, 3,729 stage/join rows, and no
crash or abort. For every one of the 512 hangar source rows, input-DMA
payload FNV/nonzero equaled post-DMA source FNV/nonzero, both payloads were
zero, post-DMA DMEM also matched, and input and source task-data pointers were
both `0x80171E70`.

This selects `H-StaleInputPayload`: the earlier input task already carries the
zero payload observed by the source witness. It refutes
`H-SourceOverwrittenAfterInput` and `H-StaleTaskPointerOnly` for all 512
measured hangar rows. The input fields propagated into 3,729 stage/join rows.
This remains port-side payload evidence; retail independently validates the
phase and task route, not the payload hash.

ORIGIN: diagnostic pre-copy input-DMA witness; the input DMA and zero payload
are legitimate observed runtime activity, and the change records hashes,
pointers, and lengths without changing guest or RDRAM state.

Evidence: `scratch/agent/s3691_groundtruth/oracle_controls.log`,
`scratch/agent/s3691_m5_stale_input_payload/real.log`, and
`scratch/agent/s3691_m5_stale_input_payload/silent.log`.
