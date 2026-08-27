# NEXT work unit (s2683) — trace renderer buffer bases to PCM service

HYPOTHESIS-ID: m5-cpu-renderer-ai-publication-join

## Work unit

Perform one bounded static audit of the caller contracts around
`updateVoiceChannelParams` (`0x8009C4E8`), `consumeVoiceSamples`
(`0x8009C240`), and `serviceStreamingVoice` (`0x8009BF14`). Recover where the
renderer `a1/a2` sample bases originate, which fields/ring are consumed, and
whether a named copy/DMA writer orders data into the AI source. Do not build or
change runtime behavior unless the audit identifies a concrete named
publication writer.

## Competing hypotheses and discriminator

- `H-renderer-buffer`: renderer `a1/a2` resolve to a persistent voice buffer
  that the PCM service consumes directly.
- `H-copy-edge`: a distinct named copy/DMA writer consumes the renderer buffer
  and publishes the AI source before the AI device sequence.
- `H-unresolved-address`: the available code/symbol evidence cannot recover a
  legitimate source or publication writer, so another runtime watch is
  premature.

The discriminator is the recovered pointer/offset/order table. A direct
renderer-to-consumer base match selects `H-renderer-buffer`; a distinct but
ordered named writer selects `H-copy-edge`; absent or ambiguous arithmetic
selects `H-unresolved-address` and parks runtime instrumentation.

## Ground-truth prerequisite

The s2681 retail control already passed for both hangar origins. If a new
runtime watch becomes necessary after the audit, repeat the whole-RDRAM
positive control and phase gate before interpreting it.

## Exact commands

1. Locate the three functions and all callers in the companion symbols/decomp
   and generated output with bounded `rg` searches; inspect at most 60-line
   windows around each implementation and caller.
2. Write the address/offset/order table to
   `scratch/agent/s2683_renderer_buffer_audit/RESULT.md`.
3. Do not run a port build or soak unless a concrete writer is identified.
