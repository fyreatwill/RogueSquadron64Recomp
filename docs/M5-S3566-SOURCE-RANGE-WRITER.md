# M5 session 3566 — source-range writer ordering

The retail ground-truth check passed its positive control: the whole-RDRAM
watch received 10,290 callbacks in 12 seconds, and the exact physical source
span `0x1797B0:0x179930` received 290 writes. The short retail run did not reach
the target VI, so its writer PCs are independent context rather than a
target-phase comparison.

The final port capture used the validated real-audio/LLE-solo/spin-yield/
autopilot route. Title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` both
fired, as did image-stage, source-DMA, audio-return, and phase controls. The
new exact-span RSP write hook recorded 9 hangar rows. They were DMEM-to-RDRAM
writebacks from `0xC30`/`0xCB0` into `0x1797B0`/`0x1798B0`; every overlapping
payload and post-write hash was zero. The first was route ordinal 1176 at
event 5575, followed by route ordinals 1177–1179. No other DMEM-to-RDRAM
writer overlapped the span.

The CPU writer census recorded 244 target-phase source-span rows, all from
guest PC `0x800078EC`, all with zero-valued byte stores. Their shared events
were earlier than the RSP writebacks (the first target rows were events
4776+). Stage rows were live (2,373 total; 2,371 stage-2/3 rows had zero
DMEM payload), and the required title/hangar controls were positive.

This selects `H-SourceRangeDmaWriter`: the immediate writer that establishes
the zero source read by the later stage DMA is the RSP DMEM-to-RDRAM writeback,
with zero payload. It refutes `H-SourceRangeStaleOrUnwritten` for this route
and does not identify why the DMEM source is zero. `H-SourceRangeCpuWriter`
remains a preceding zero-store producer, not the immediate writer for the
stage-task source read. Evidence is single-source for target-phase port
ordering; the retail run independently proves the oracle watch path and
retail span activity. No game-state mitigation was added.

Artifacts: `scratch/agent/s3566_oracle_ground_truth/oracle.log` and
`scratch/agent/s3566_source_range_writer/final/run.log`.
