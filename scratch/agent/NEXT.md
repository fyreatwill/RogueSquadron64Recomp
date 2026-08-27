# NEXT work unit (s2703) — audit indirect AI-worker registration and calls

HYPOTHESIS-ID: m5-cpu-publication-boundary

## Work unit

Perform one bounded source audit of the indirect registration/call path for
`runAiAudioStreamPlaybackLoop` (`0x8008ED70`) and
`serviceAudioOutputBuffers` (`0x8008ED6C`). Enumerate all function-pointer
stores, loads, thread-entry/service-worker registrations, direct calls, and
dispatch tables that can reach either body. Classify each edge as startup
registration, AI-buffer consumer, payload producer, opaque/external, or dead.
Do not repeat the completed allocation, queue, renderer, mixer, DMA-service,
or host-body audits; do not add runtime instrumentation or behavior changes.

## Competing hypotheses and discriminator

- `H-ai-no-indirect-producer`: all registrations/calls are the known AI loop
  and its zero-clear/submission path; no opaque producer is reachable.
- `H-ai-service-produces`: the adjacent service body or a named caller writes
  rendered/stream data into the AI aliases before submission.
- `H-ai-external-producer`: a registered callback, thread entry, or indirect
  target leaves the producer body outside the generated snapshot.
- `H-ai-dead-registration`: the apparent entry is not reachable in the live
  route or its overlay registration is stale/mismatched.

The discriminator is a complete pointer-edge table with store/load PC,
resolved target, caller/registration, destination/source relation, and
ordering before `osAiSetNextBuffer`. A complete known zero-clear path selects
`H-ai-no-indirect-producer`; a named payload writer selects
`H-ai-service-produces`; an unresolved external target selects
`H-ai-external-producer`; unreachable or mismatched registration selects
`H-ai-dead-registration`.

## Exact commands

1. `rg -n -- 'runAiAudioStreamPlaybackLoop|serviceAudioOutputBuffers|0x8008ED6C|0x8008ED70|0x0008E92C|0x0008E930|create.*thread|thread.*entry|service.*worker|callback|func_map|get_function' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/src`
2. Read bounded windows around every candidate and write the complete table to `scratch/agent/s2703_m5_ai_indirect_path/audit.md`.
3. No build or game run. A future runtime watch still requires the retail whole-RDRAM positive control and a named legitimate destination/order edge.
