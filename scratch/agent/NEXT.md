# NEXT work unit — ground the upstream route divergence in retail

HYPOTHESIS-ID: m5-audio-route-upstream-boundary

## Single work unit

Use one static audit of the MIPS `__osViSwapContext` boundary to identify a
genuinely different named handoff for the next retail oracle run. The exact
`0x800356A8` candidate was absent in retail even though title/hangar controls
were valid, so do not repeat it or the closed `0x80034F38:0x800356AC` range.
Session 3126's port probe had valid controls (VI-context 8 rows and host
voice-audit 1 row), but the port reached only VI 640 and had zero rows from
the retail-live continuation. Audio and route behavior remain out of scope.

## Competing hypotheses

- H-NewStaticHandoff: the audit identifies a distinct branch/call/return PC at
  the VI consumer boundary that can be phase-gated in the retail oracle.
- H-NoDistinctHandoff: the audited instructions are already covered or have
  no independent execution edge; choose the highest-information non-consumer
  boundary instead.
- H-RetailControlInvalid: the whole-RDRAM positive control or title/hangar
  phase markers fail, so the oracle result is unevaluable.

## Discriminating measurement

The audit must produce one exact guest PC not already covered by the closed
consumer watches and explain why it is an independent handoff. The following
oracle run must pass the whole-RDRAM control and reach title/hangar; a
target-phase row selects H-NewStaticHandoff, no row with valid controls
selects H-NoDistinctHandoff, and missing controls select
H-RetailControlInvalid.

## Exact commands

1. Audit the linked retail ELF/disassembly for `__osViSwapContext`
   `0x80035550:0x800358AC`; record one distinct branch/call/return PC and its
   relation to `0x800356AC`.
2. Rewrite this file with that candidate and the same competing outcomes,
   then run one oracle capture with all-RDRAM control and explicit title/
   hangar phase buckets.
3. Record the control, title/hangar phases, watched PC rows, and selected
   hypothesis; do not add a port instrument until the writer/consumer PC is
   named.
