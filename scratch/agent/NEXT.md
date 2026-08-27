# NEXT work unit (s2749) — audit the fresh M5 streaming-voice boundary

HYPOTHESIS-ID: m5-service-streaming-voice-boundary

## Work unit

Perform one bounded static audit of `serviceStreamingVoice` at guest
`0x8009BAD4` (`../N64Recomp/RecompiledFuncs/funcs_27.c:369`) and its immediate
named callers/consumers. Enumerate every payload pointer, load/store or copy,
transform, slot/queue signal, AI destination, and ordering edge. Do not repeat
the already closed `serviceVoicePoolFrame`, queue, renderer, mixer, AI-worker,
PI-service, or host-AI surfaces. Do not add a runtime watch or mitigation.

## Competing hypotheses and discriminator

- H-streaming-publishes: the service directly copies or transforms legitimate
  rendered/audio payload into an AI-visible destination.
- H-streaming-services: it only advances slot/descriptor state or signals a
  worker, with no payload publication.
- H-streaming-opaque-edge: a named indirect callback or data-driven pointer
  leaves the immediate surface unevaluable and is the only next target.

The discriminator is a complete source-level table of all direct callers,
callee edges, pointer origins/destinations, writes/copies, and queue/AI calls.
An explicit payload-to-AI/order edge selects H-streaming-publishes; only
state/cadence operations select H-streaming-services; an unresolved named
indirect/data-driven edge selects H-streaming-opaque-edge. If no outcome can
be distinguished, stop and do not add instrumentation.

## Exact commands

1. Inspect only bounded windows around the definition and direct references:
   `rg -n -C 35 'serviceStreamingVoice' ../N64Recomp/RecompiledFuncs/funcs_27.c ../N64Recomp/RecompiledFuncs/funcs.h ../N64Recomp/RecompiledFuncs/recomp_overlays.inl`
2. Enumerate nearby calls, stores, queue symbols, AI symbols, and pointer
   fields with `rg`; record the complete table in
   `scratch/agent/s2749_m5_service_streaming_voice/audit.md`.
3. Append the result to `PORTING-STATE.md`, update `docs/CURRENT-TRUTH.md`
   next steps, and prepare the next single work unit.
