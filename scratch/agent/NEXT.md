# NEXT work unit (s2682) — audit renderer and AI address arithmetic

HYPOTHESIS-ID: m5-cpu-renderer-ai-publication-join

## Work unit

Perform one bounded static audit of the retail/recompiled implementations and
callers for `0x8009DB2C` and `0x8002A0B8..0x8002A0D8`. Recover the exact base
pointer, offsets, transfer width, and call ordering for each site. Do not build
or change runtime behavior unless the audit identifies a concrete named
publication writer.

## Competing hypotheses and discriminator

- `H-renderer-direct`: `0x8009DB2C` writes the AI source directly or via a
  named fixed copy that the AI-side sequence consumes.
- `H-copy-edge`: `0x8009DB2C` writes an intermediate and a distinct named copy
  or DMA writer publishes the AI source before `0x8002A0B8`.
- `H-unresolved-address`: the available code/symbol evidence cannot recover a
  legitimate publication writer, so another runtime watch would be premature.

The discriminator is the recovered pointer/offset/order table. A direct match
selects `H-renderer-direct`; a distinct but ordered named writer selects
`H-copy-edge`; absent or ambiguous address arithmetic selects
`H-unresolved-address` and parks runtime instrumentation.

## Ground-truth prerequisite

The s2681 retail control already passed for both hangar origins. If a new
runtime watch becomes necessary after the audit, repeat the whole-RDRAM
positive control and phase gate before interpreting it.

## Exact commands

1. Locate the two addresses in the companion symbols/decomp and generated
   output with bounded `rg` searches; inspect at most 60-line windows around
   each implementation and caller.
2. Write the address/offset/order table to
   `scratch/agent/s2682_renderer_ai_static_audit/RESULT.md`.
3. Do not run a port build or soak unless a concrete writer is identified.
