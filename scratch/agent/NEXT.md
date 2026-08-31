# NEXT work unit — exact attribution of the second callback-table registration

HYPOTHESIS-ID: m5-callback-occupant-exact-caller

Session 3335 selected generated runtime population at the class level, but the
1-ms snapshot's `0x80007A68` marker is not an exact store PC. Identify the
generated callsite that registers the second/third `0x8009123C` occupant.

## Competing hypotheses

- `H-PortSecondRegistrationCallsite`: a generated callsite invokes
  `registerSiCallback(0x8009123C)`; direct callsite instrumentation will name it.
- `H-PortCallbackOccupantIsOverlayData`: overlay load/DMA or data initialization
  populates an occupant without a registration call.
- `H-PortCallbackOccupantIsTransient`: the table changes between snapshots and
  the callsite census needs finer phase gating or a direct store hook.

## Discriminator

Ask the independent retail oracle first, retaining whole-RDRAM, callback-table
write, and the existing retail callback PCs. Then build one port instrument
that marks every generated `registerSiCallback` callsite, including the
existing `0x80002FDC` and `0x8009BC50` edges, alongside the full-table census
and task/host controls. A marked call with argument `0x8009123C` before the
occupant transition selects `H-PortSecondRegistrationCallsite`; a clean call
census with a table transition and overlay/DMA evidence selects
`H-PortCallbackOccupantIsOverlayData`; a positive-control run with a table
transition but no marked call selects `H-PortCallbackOccupantIsTransient`.
Any missing positive control invalidates the run and requires a fixed rerun.

Exact prior-arm commands are in
`scratch/agent/run_s3334_m5_callback_writer_attribution.sh`; extend that one
script only after the new writer instrument is built. No Step 3 contract
change or mitigation is authorized.
