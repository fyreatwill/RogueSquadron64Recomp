# NEXT work unit (s2702) — enumerate AI-source allocation writers

HYPOTHESIS-ID: m5-cpu-publication-boundary

## Work unit

Perform one bounded source audit of every generated-function write and alias
that can target the AI worker allocation at `0x801496B0` (the `0x3000` span
used by `0x8008ED70`). Start from the allocation setup and all derived base
pointer uses, then classify each store/copy/clear as initialization, stream
input, rendered output, or unresolved. Include direct callers and immediate
consumers, but do not repeat the already audited queue, renderer, mixer,
service, or host bodies. Do not add runtime instrumentation or behavior
changes unless a legitimate rendered-payload writer and ordering edge are
identified.

## Competing hypotheses and discriminator

- `H-ai-clear-only`: every writer is initialization/clear or allocator state;
  no legitimate rendered payload reaches the AI span.
- `H-ai-stream-writer`: a named writer supplies streamed/sample data but not
  the rendered MORT output, selecting the stream boundary for the next audit.
- `H-ai-render-writer`: a named writer copies or transforms rendered output
  into the AI span and its ordering/consumer edge is visible.
- `H-ai-unresolved-writer`: an alias or indirect body prevents complete
  classification, selecting that unresolved edge without a runtime watch.

The discriminator is a complete writer table: writer PC/function, effective
destination range, source pointer/range, operation and length, caller, and
ordering/consumer. A legitimate rendered-to-AI row selects
`H-ai-render-writer`; exhaustive clear-only rows select `H-ai-clear-only`; a
named stream-only row selects `H-ai-stream-writer`; any opaque alias/body
selects `H-ai-unresolved-writer`.

## Exact commands

1. `rg -n -- "801496B0|801496[0-9A-Fa-f]{2}|0x1496B0|0x149[0-9A-Fa-f]{3}|-0x6950|-0X6950|osAiSetNextBuffer|rs_memset|rs_memcpy|memcpy|bzero" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows around every candidate and write the complete table to `scratch/agent/s2702_m5_ai_source_writers/audit.md`.
3. No build or game run. A future narrow watch requires the retail whole-RDRAM positive control and a named legitimate destination first.
