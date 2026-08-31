# NEXT work unit — identify the pre-existing callback-table occupant writer

HYPOTHESIS-ID: m5-callback-occupant-writer

Session 3334 showed the port reaches `initMusyXVoiceTable` and calls
`registerSiCallback` with `0x8009B5A8`, but `0x80007928` never stores because
the table is already full of `0x8009123C` occupants. Identify the writer or
loader that populated those occupants before considering behavior change.

## Competing hypotheses

- `H-PortCallbackOccupantIsRuntime`: a generated runtime writer stores
  `0x8009123C` before `initMusyXVoiceTable` reaches the full table.
- `H-PortCallbackOccupantIsOverlayData`: overlay load/DMA or data initialization
  populates the three entries without a generated store in the live path.
- `H-PortCallbackOccupantIsTransient`: the current state poll misses a transient
  writer, so a write watch or finer-grained entry capture is required.

## Discriminator

Ask the independent retail oracle first, retaining whole-RDRAM, callback-table
write, and the existing retail callback PCs. Then build one port instrument
with a phase-gated write census for the full callback-table range, plus entry
marks for every generated function that writes or copies the table and the
existing task/host controls. A runtime writer row with value `0x8009123C`
selects `H-PortCallbackOccupantIsRuntime`; a clean full-table range with no
generated writer but an overlay/DMA event selects `H-PortCallbackOccupantIsOverlayData`;
a positive-control run with a state change but no retained writer row selects
`H-PortCallbackOccupantIsTransient`. Any missing positive control invalidates
the run and requires a fixed rerun in that iteration.

Exact prior-arm commands are in
`scratch/agent/run_s3334_m5_callback_writer_attribution.sh`; extend that one
script only after the new writer instrument is built. No Step 3 contract
change or mitigation is authorized.
