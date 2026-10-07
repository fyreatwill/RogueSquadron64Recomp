# Next work unit: M5 source-producer context census

Run one retail-gated census of the guest source-span writer at `0x800078EC`
and its caller/input context. Do not change the image, wait, cap, predicate,
slot state, guest behavior, or host writeback. Use the existing source-writer
instrumentation with the canonical AUTOPILOT and phase gates; correct the
existing recipe if non-canonical drain-tick or launch ordering invalidates the
route.

HYPOTHESIS-ID: m5-image-source-producer-context

Competing hypotheses and discriminator:

- H-port-writer-legitimate-zero: retail and port agree on the writer's
  destination, value, loop/input context, and ordering; the zero is an
  upstream producer/input contract gap.
- H-port-writer-context-split: the port writer's arguments, destination,
  value, loop bound, or ordering diverges from retail; that first split is the
  next contract edge.
- H-route-invalid: the retail whole-RDRAM/title/hangar controls or the
  phase-keyed port source-span join is absent.

The single discriminating measurement is one phase-keyed writer-context table
joining retail PC/value/destination/field context and port guest-store
arguments, source-span hash, ordering, and title/hangar phase. Matching
zero-valued context selects H-port-writer-legitimate-zero; a qualified
argument/context split selects H-port-writer-context-split; missing controls
selects H-route-invalid.

Before any build, verify the existing writer switches and driver:

`rg -n '800078EC|M5_SOURCE_PRODUCER|M5_SOURCE_WRITER|M5_INPUT_WRITER|M5_SOURCE_TRANSITION' src tools scratch/agent --glob '!*.log' --glob '!*.md'`

Ask ground truth first with the oracle recipe: whole-RDRAM positive control,
title/hangar VI gates, `--watch-pc 0x800078EC`, post-store value/field context,
and the same source-span watches. Build once with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the image arm from `build/` with LLE/solo/spin-yield, canonical AUTOPILOT,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and these logs:
`ROGUESQ_LOG_M5_SOURCE_PRODUCER=1`, `ROGUESQ_LOG_M5_SOURCE_WRITER=1`,
`ROGUESQ_LOG_M5_INPUT_WRITER=1`, `ROGUESQ_LOG_M5_SOURCE_TRANSITION=1`,
`ROGUESQ_LOG_M5_TASK_CONTRACT=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, and
`ROGUESQ_LOG_PCM_BOUNDARY=1`. Run the fixed silent control only if needed for
the no-write positive control. SIGKILL after hangar or the phase timeout.
Report the complete writer-context table; a writer counter alone is not a
control.
