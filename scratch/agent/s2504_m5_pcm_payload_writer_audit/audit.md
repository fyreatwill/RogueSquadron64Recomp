# Session 2504 — M5 nonzero PCM payload writer census

## Scope and discriminator

This was a static-only work unit over the 51-file active generated tree
`../N64Recomp/RecompiledFuncs`; backup `RecompiledFuncs.s*` trees were
excluded. The corrected table root is `D_801496B0`, with sixteen heap-backed
entries separated by `0x300` bytes. The discriminator was a
producer-to-consumer table keyed by guest PC, operation/callee, destination
expression, and buffer derivation.

## Producer-to-consumer table

| guest PC / site | operation | destination or argument | derivation | classification |
|---|---|---|---|---|
| `0x8008ED70` | `rs_malloc(0x3000)` | returned heap block | base for sixteen buffers | allocation only |
| `0x8008EDA4` | `sw` | `D_801496B0` | stores allocation result as table root | initialization |
| `0x8008EDB8` | sixteen `sw` iterations | `D_801496B0 + 4 + i*4` | stores `root + i*0x300` | initialization/layout |
| `0x8008EDDC` | `rs_memset` | `D_801496B0[0]`, length `0x3000`, fill `0` | clears all sixteen blocks | initialization; not payload |
| `0x8008EE00` | `osAiSetNextBuffer` | `D_801496B0[0]`, length `0x300` | first AI consumer | consumer |
| `0x8008EE84` | `osAiSetNextBuffer` | `D_801496B0[index]`, length `0x300` | rotating index plus root table | consumer |
| `0x8009BE14` | `synchronousDmaTransfer` | caller-provided `a3` destination | voice/sample DMA; no static target join | unrelated |
| `0x8009D7D0` onward | direct loads/stores | voice/sample filter state from `a0` | no root-table derivation | unrelated |
| `0x8009DC98` onward | sample mixing/companding | voice-local fields from `a0` and registers | no root-table derivation | unrelated |

The active generated source contains zero literal `801496B0` references. The
root is represented by `lui 0x8015; addiu -0x6950`, resolving to
`0x801496B0`; that form occurs in the playback loop for the root/table
producer and consumers. No active generated store, `memcpy`, `memmove`, or
nonzero-producing call was joined to the root or a derived
`root + i*0x300` buffer after the clear.

Companion symbols independently name `runAiAudioStreamPlaybackLoop` at
`0x8008ED70` and `D_801496B0` at `0x801496B0`. The named voice/sample decode,
filter, mix, and DMA routines have no target-table reference in active
generated output. Host `queue_audio_buffer`/`queue_samples` paths consume
guest data but do not write the guest AI blocks. Existing RSP-DMA bookkeeping
observes image-DMA destinations, but this census found no statically joined
destination equal to the AI table.

## Result

Selected: **`H-payload-unresolved`** at the static boundary.

The generated tree proves allocation, zero initialization, and two consumers,
but no non-initialization payload writer. The host consumer is not itself a
writer, and no host/RSP destination has been joined to these buffers. Thus the
result does not select `H-payload-host`; an indirect/RSP output writer remains
open. No build, runtime behavior, address remap, or mitigation changed.
