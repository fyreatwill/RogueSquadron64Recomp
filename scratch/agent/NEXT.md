# NEXT work unit — trace the selected direct-writer edge

HYPOTHESIS-ID: m5-port-zero-pcm-source

Do exactly one bounded M5 direct-writer edge census next iteration. Do not
modify output, waits, slots, status handling, consumer dispatch, or PCM
writeback.

Competing hypotheses:

- `H-PortDirectWriterMissing`: the port never reaches the retail direct-writer
  edge `0x8002BEEC -> 0x800078EC`.
- `H-PortWriterDispatchAlias`: the port reaches the same writer through a
  translated/aliased caller edge that is currently hidden by the host probe.
- `H-PortWriterBytesDiffer`: the port reaches the edge but target bytes differ
  before the writer, so the zero PCM source is produced there.

Discriminating measurement: ask the retail oracle for phase-gated execution
rows at `0x8002BEEC` and `0x800078EC`, including predecessor and target bytes;
batch one port writer-entry census keyed by caller/return edge, target bytes,
phase, and audio-task ordinal/row. No port `0x8002BEEC` edge selects
`H-PortDirectWriterMissing`; a matching writer with a different caller selects
`H-PortWriterDispatchAlias`; a matching caller with zero/different bytes
selects `H-PortWriterBytesDiffer`.

Before building, verify oracle watch indices and existing port writer hooks.
Keep phase, audio-task/ABI, PCM, image-stage/DMA, title, and hangar controls
live. If code under `lib/` changes, run
`./submodule-patches/export.sh` in the same iteration.

Run from `build/` with the validated route and canonical Start schedule; phase
gate on VI 512 via `probe.sh`, use a non-dot-prefixed capture path, and kill
with SIGKILL. Record the result in a new scratch evidence file, update the
ledger and CURRENT-TRUTH, then commit.
