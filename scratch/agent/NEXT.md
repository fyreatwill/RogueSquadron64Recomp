# NEXT work unit — attribute writers of zero PCM source spans

HYPOTHESIS-ID: m5-port-zero-pcm-source

Do exactly one bounded M5 writer census next iteration. Do not modify output,
waits, slots, status handling, consumer dispatch, or PCM writeback.

Competing hypotheses:

- `H-PortSourceWriterAbsent`: no guest store populates RDRAM `0x1797B0` or
  `0x1798B0` on the target route.
- `H-PortSourceWriterZero`: a guest writer reaches those spans but stores only
  zero, so the zero source is produced upstream.
- `H-PortSourceVisibility`: nonzero writer activity exists, but the port source
  DMA reads a different or stale span.

Discriminating measurement: first ask the retail oracle for writer-PC
histograms on physical `0x1797B0:0x1798B0` with a whole-RDRAM positive control
and the canonical title/hangar schedule. Then batch a phase-scoped port store
census for those same spans, joined to the source-DMA route ordinal/row. No
writer selects `H-PortSourceWriterAbsent`; only-zero writer values selects
`H-PortSourceWriterZero`; nonzero writer values with zero source-DMA payload
selects `H-PortSourceVisibility` or a stale/ordering edge.

Before building, verify oracle watch indices and existing generated-store hook
coverage. Keep phase, audio-task/ABI, PCM, image-stage/DMA, title, and hangar
controls live. If code under `lib/` changes, run
`./submodule-patches/export.sh` in the same iteration.

Run from `build/` with the validated route and canonical Start schedule; phase
gate on VI 512 via `probe.sh`, use a non-dot-prefixed capture path, and kill
with SIGKILL. Record the result in a new scratch evidence file, update the
ledger and CURRENT-TRUTH, then commit.
