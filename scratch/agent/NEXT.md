# Next work unit: M5 source-producer context census, retail route repair

HYPOTHESIS-ID: m5-image-source-producer-context

Run one retail-gated census of the guest source-span writer at `0x800078EC`
and its caller/input context. Do not change the image, wait, cap, predicate,
slot state, guest behavior, or host writeback.

Competing hypotheses and the discriminator:

- H-port-writer-legitimate-zero: retail and port agree on writer destination,
  value, loop/input context, and ordering; the zero is an upstream producer
  gap.
- H-port-writer-context-split: the port writer's arguments, destination,
  value, loop bound, or ordering diverges from retail; that first split is the
  next contract edge.
- H-route-invalid: the retail whole-RDRAM/title/hangar controls or the
  phase-keyed port source-span join is absent.

The single discriminating measurement is one phase-keyed writer-context table
joining retail PC/value/destination/field context and port guest-store
arguments, source-span hashes, ordering, and title/hangar phase. Matching
zero-valued context selects H-port-writer-legitimate-zero; a qualified
argument/context split selects H-port-writer-context-split; missing controls
selects H-route-invalid.

Before building, run the retail oracle with whole-RDRAM positive control,
title/hangar VI gates, `--watch-pc 0x800078EC`, post-store value/field context,
and the source-span watches. Use the VI-traced launch ordering that has
previously qualified both target phases; if hangar is absent, stop inference
and record H-route-invalid.

Then build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the image arm from `build/` with LLE/solo/ungated/spin-yield, canonical
AUTOPILOT, `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and
`ROGUESQ_LOG_M5_SOURCE_PRODUCER=1`, `ROGUESQ_LOG_M5_SOURCE_WRITER=1`,
`ROGUESQ_LOG_M5_INPUT_WRITER=1`, `ROGUESQ_LOG_M5_SOURCE_TRANSITION=1`,
`ROGUESQ_LOG_M5_TASK_CONTRACT=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, and
`ROGUESQ_LOG_PCM_BOUNDARY=1`. SIGKILL after hangar or the phase timeout.
Report the complete writer-context table, not only writer counts.
