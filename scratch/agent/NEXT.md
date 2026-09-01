# NEXT work unit — identify the zero DMEM payload producer

HYPOTHESIS-ID: m5-image-task-dmem-payload-producer

Session 3568 selected `H-SourceRangeOtherDma`: target-valid hangar tasks used a
zero-payload `dmem_to_rdram` writeback for `0x1797B0`/`0x1798B0`, followed by
zero RDRAM-to-DMEM reads. The next bounded unit is one phase/task-keyed census
of what leaves the writeback DMEM payload zero.

Competing hypotheses and discriminator:

- H-DmemPayloadCpuStore: CPU stores populate the writeback DMEM source window,
  with a matching PC and nonzero/hash transition before `dmem_to_rdram`.
- H-DmemPayloadVectorStore: RSP vector stores populate it, with a matching
  task ordinal and nonzero post-store window hash before the writeback.
- H-DmemPayloadClearOrStale: no productive store occurs after the relevant
  clear/task boundary, so the zero payload is inherited or explicitly cleared.

The single discriminator is a shared-event table keyed by image-task ordinal
and route row. Reuse `[m5-dmem-source-writer]`, `[m5-source-window]`,
`[m5-preclear]`, and `[m5-source-range-writer]` rows to record every CPU,
vector, clear, and writeback event affecting DMEM `0x6F0..0x9F0` or
`0xCB0..0xE48`, including post-store hash/nonzero count, then pair it with the
same-ordinal writeback. A productive CPU/vector row selects its hypothesis;
absence after a matching clear/task boundary selects
`H-DmemPayloadClearOrStale`.

Before building, check `wc -c < docs/CURRENT-TRUTH.md` and the retail oracle
paths. Reuse the existing hooks; add only a task-ordinal join if current rows
cannot pair the events. Rebuild once if needed, then run one standalone image
arm from `build/` with the validated real-audio/LLE-solo/spin-yield/autopilot
route. Require title 1024, hangar 512, image-stage, source-DMA, and positive
writer controls. Use SIGKILL and retain the full log under `scratch/agent/`.
