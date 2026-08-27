# NEXT work unit (s2750) — resolve the M5 streaming callback edge

HYPOTHESIS-ID: m5-service-streaming-callback-edge

## Work unit

Resolve the indirect callback loaded from `voice + 0x194` at guest
`0x8009C040`. Trace every writer of descriptor `+0x194`, its immediate
initializers, and each possible target in the named companion or generated
tables. Enumerate callback arguments, payload destinations, AI/PI/queue
calls, and ordering. Do not repeat the completed streaming body or the
already closed queue, renderer, mixer, AI-worker, PI-service, host-AI, or
voice-pool surfaces. Do not add a runtime watch.

## Competing hypotheses and discriminator

- H-callback-publishes: the callback writes or transforms legitimate payload
  into an AI-visible destination and supplies the missing publication edge.
- H-callback-services: the callback only performs state, timing, or queue
  work; no AI publication is present.
- H-callback-unresolved: the callback target or writer remains data-driven,
  so publication cannot yet be discriminated.

The discriminator is a complete writer-to-target table for `+0x194`, with
callback arguments and downstream writes/calls. An explicit payload-to-AI
and ordering edge selects H-callback-publishes; only state/timing/queue work
selects H-callback-services; an unresolved target or writer selects
H-callback-unresolved. If no outcome can be distinguished, stop and do not
add instrumentation.

## Exact commands

1. `rg -n -C 8 '0X194|0x194|serviceStreamingVoice|initMusyXVoiceSlot' ../N64Recomp/RecompiledFuncs/funcs_*.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl`
2. Enumerate all stores to `+0x194`, descriptor initializers, and callback
   target/table references with bounded `sed` windows; record the complete
   writer-to-target table in
   `scratch/agent/s2750_m5_streaming_callback/audit.md`.
3. Append the result to `PORTING-STATE.md`, update `docs/CURRENT-TRUTH.md`,
   and prepare the next single work unit.
