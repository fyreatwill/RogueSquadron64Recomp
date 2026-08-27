# NEXT work unit (s2684) — audit the indirect voice-stage destination boundary

HYPOTHESIS-ID: m5-cpu-renderer-ai-publication-join

## Work unit

Perform one bounded static audit of the indirect call setup that supplies the
caller-owned arrays to `updateVoiceChannelParams` and of consumers of the
voice object `+0x140` output. Recover every reachable `jalr`/function-pointer
setup, its base arithmetic, and any destination or ordering edge toward the
AI source. Do not build or change runtime behavior unless a concrete named
publication writer is identified.

## Competing hypotheses and discriminator

- `H-renderer-buffer`: the indirect caller resolves the renderer arrays or
  `voice+0x140` to the AI source consumed directly.
- `H-copy-edge`: a distinct named copy/DMA writer consumes that output and
  publishes the AI source before the AI device sequence.
- `H-unresolved-address`: caller setup or destination arithmetic remains
  ambiguous, so another runtime watch is premature.

The discriminator is the recovered pointer/offset/order table. A direct base
match selects `H-renderer-buffer`; a distinct ordered named writer selects
`H-copy-edge`; absent or ambiguous arithmetic selects `H-unresolved-address`
and parks runtime instrumentation.

## Ground-truth prerequisite

The s2681 retail control already passed for both hangar origins. If a new
runtime watch becomes necessary after the audit, repeat the whole-RDRAM
positive control and phase gate before interpreting it.

## Exact commands

1. Locate all `jalr`/function-pointer loads near the voice-stage functions and
   all references to `+0x140`, `+0x168`, `+0x178`, and `+0x188` with bounded
   `rg` searches; inspect at most 60-line windows around each hit.
2. Cross-check names and addresses in `../rogue_squadron64/symbol_files` and
   write the address/offset/order table to
   `scratch/agent/s2684_voice_destination_audit/RESULT.md`.
3. Do not run a port build or soak unless a concrete writer is identified.
