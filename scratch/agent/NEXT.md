# NEXT work unit (s2700) — bounded M5 queue-publication audit

HYPOTHESIS-ID: m5-cpu-publication-boundary

## Work unit

Audit the complete in-tree sender/receiver chain for the audio queue at
`0x80149990` (`0x80150000 - 0x6670`), centered on
`factor5QueueSignal` (`0x800920D0`) and its direct receiver(s). Classify every
message payload and immediate consumer as rendered-PCM publication,
stream/descriptor service, scheduler-only, or unresolved. Do not add runtime
instrumentation or change behavior unless the source audit names a legitimate
PCM destination and ordering edge.

## Competing hypotheses and discriminator

- `H-queue-publishes`: the queue message or its immediate consumer carries a
  rendered payload into the AI-source allocation or another named PCM span.
- `H-queue-services`: the queue only signals scheduler/stream/descriptor work;
  no payload or AI-source relation exists.
- `H-queue-unresolved`: an indirect callback or opaque message field prevents
  a complete classification, so a new source boundary is selected without a
  runtime watch.

The discriminator is the complete queue table: every send/receive site,
message address/length, payload reads/writes, downstream calls, and any join
to `0x801496B0` or `osAiSetNextBuffer`. A named payload-to-AI edge selects
`H-queue-publishes`; exhaustive service-only operations select
`H-queue-services`; an unresolved indirect/body edge selects
`H-queue-unresolved`.

## Exact commands

1. `rg -n -- "-0X6670|-0x6670|factor5QueueSignal|0x800920D0|80149990|801496B0|osAiSetNextBuffer" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows around every hit and write the classified table to
   `scratch/agent/s2700_m5_queue_boundary/audit.md`.
3. No build or game run: this is a source-level boundary audit, not a runtime
   measurement. The independent retail positive control remains required
   before any future narrow watch.
