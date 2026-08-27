# NEXT work unit (s2696) — audit the unresolved post-mix callback

HYPOTHESIS-ID: m5-mort-publication-postmix-boundary

## Work unit

Source-read the callback target loaded at `0x80091670`/invoked at
`0x80091684` in `musyxSynthFrame`, plus its immediate named/indirect
consumers. Do not repeat the completed renderer, mixer, post-mix maintenance,
AI-submit, cache, acquire, or direct-caller bodies. Trace whether this
callback receives or publishes the per-frame output block into the AI source,
including writer, destination, payload legitimacy, queue/service signal, and
ordering relative to `osAiSetNextBuffer`.

## Competing hypotheses and discriminator

- `H-callback-publishes`: the callback target is a legitimate output-block or
  AI-source publisher; its source, destination, and ordering select the edge.
- `H-callback-service`: the callback hands data to a queue/service consumer
  that performs publication asynchronously.
- `H-callback-unrelated`: the callback only services streamed voice/control
  state and does not touch the synth output or AI source.

The discriminator is a complete callback target/consumer table: target
identity, all arguments, output-block reads/writes, payload copy/transform and
destination, queue/service signal, and ordering edge to `osAiSetNextBuffer`.
A named legitimate copy selects `H-callback-publishes`; a queued handoff
selects `H-callback-service`; a state-only path selects `H-callback-unrelated`
and retains `H-unresolved-address`. If the target remains unresolved, record
that limitation and do not add a runtime watch, writeback, remap, or
mitigation.

## Exact commands

1. Locate the callback-table writer and target consumers:
   `rg -n "0x80091670|0x80091684|0x801499DC|0x8000794C|findAndZeroTableSlotMatching|serviceStreamedVoices|flushStreamedVoiceBuffers" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files`
2. Read bounded windows around the target definition, callback-table
   initialization, and immediate callers. Record the complete table in
   `scratch/agent/s2696_mort_callback_boundary/audit.md`.
3. Do not build or run unless the static table identifies a concrete runtime
   discriminator with a named destination and ordering edge.
