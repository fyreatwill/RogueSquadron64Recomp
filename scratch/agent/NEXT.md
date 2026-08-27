# NEXT work unit (s2688) — identify the next downstream M5 PCM consumer

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit outside the already-closed mixer-table boundary:
start from the named consumers of `voice+0x140` and the audio service functions
that call `osAiSetNextBuffer`, then identify the first named function that can
copy or publish those mixed words toward the AI source. Use companion
address/name evidence and generated callers. Do not repeat the mixer-table,
filter, persistent-object, task-field, ring, shared-stack, DMA callback, or
update/renderer audits. Do not add runtime watches, writeback, remaps, or
mitigation from unresolved pointer shapes.

## Competing hypotheses and discriminator

- `H-direct-publish`: a named downstream function copies the legitimate
  `voice+0x140` output into a PCM/AI destination and its ordering is visible.
- `H-service-boundary`: a named service/slot boundary is reached, but the
  publication destination remains outside that caller.
- `H-unresolved-address`: all reachable downstream callers remain unrelated
  to the rendered voice object or end at unresolved indirect state.

The discriminator is a complete caller/destination table for every named
downstream consumer: each outcome must identify writer, destination, payload
polarity, and ordering relation, or explicitly show which field is absent.

## Ground-truth prerequisite

No runtime watch, build, or soak is authorized until the static table names a
ground-truth target.

## Exact commands

1. `rg -n -H 'voice\\+0x140|osAiSetNextBuffer|audioMixStereoBlock8|renderVoiceAudioBlock|dmaVoiceSampleAndSignal|consumeVoiceSamples' ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows for each unique caller and follow only named calls or direct stores/copies.
3. Record the complete downstream destination/order table and selected hypothesis in the ledger.
