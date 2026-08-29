# NEXT work unit — audit the port-side target VI/output boundary

HYPOTHESIS-ID: m5-port-output-boundary-audit

The free-list guard validation cannot run in this checkout. The next unit is
therefore a bounded, build-independent audit of the already-present port
`osViSwapBuffer`/VI-commit evidence against Session 3241's retail relation.
This does not authorize an M5 behavior change; the guard validation remains an
open dependency for that change.

## Competing hypotheses

- `H-PortRowPresent`: the port already records a target-phase row with the
  expected framebuffer, VI origin, caller, and ordering.
- `H-PortRowMissing`: the port reaches neither the target-phase swap nor commit
  row, so parity is unevaluable and needs a new phase-gated capture.
- `H-PortMismatch`: both rows exist but disagree with retail's
  `a0=0x80790000` / physical `0x00790000` and origins
  `0x00790400/0x00790800`; this identifies a boundary mismatch without yet
  selecting a fix.

## Discriminator

Trace the source contract and any checked-in bounded-run artifact for
`osViSwapBuffer_recomp`, `[m5-port-retail-target]`, and `[m5-route-transition]`.
The complete row selects `H-PortRowPresent`; absence after a valid dispatch
and VI positive control selects `H-PortRowMissing`; a like-for-like differing
row selects `H-PortMismatch`. A source-only result must be labeled
single-source and cannot authorize M5 Step 3.

## Exact commands

1. `rg -n -C 6 'm5-port-retail-target|m5-route-transition|osViSwapBuffer_recomp' src/main lib/N64ModernRuntime/librecomp/src`
2. Locate the most recent bounded capture with `rg -n 'm5-port-retail-target|m5-route-transition|\\[phase\\]' scratch/agent/soak_results scratch/agent --glob '*.log' --glob '*.txt' | head -200`.
3. Record the row fields, controls, and outcome in the ledger. Do not modify
   audio/output behavior; the free-list validation still gates any M5 change.

## Open dependency

On a host containing the configured MIPS GCC/LD and Debug N64Recomp, run the
original guard validation from the prior NEXT. Do not substitute Clang or the
stale `patches.map`.
