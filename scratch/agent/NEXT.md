# NEXT work unit (s2460) — audit the pre-target dispatch boundary

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Perform one bounded static audit of the complete generated call/return idiom
leading to the pre-target failures at `last-guest-pc=0x8000834C` and
`0x80007904`, including callers, continuation blocks, and resolver boundary.
Do not add guards or change dispatch/audio behavior.

## Competing hypotheses and discriminator

- H-PreTargetBoundary: one pre-target path aborts or starves the qualified route.
- H-UnrelatedFailure: both failures are separate activity and do not explain
  absent target-phase alternate rows.
- H-GeneratedContinuationMismatch: generated lowering changes control flow
  before target capture.

The discriminator is a complete site table: each failure PC's generated
caller, guest continuation/return target, resolver operation, and whether it
can terminate or starve the phase-gated route. An explicit termination edge
selects H-PreTargetBoundary; no such edge selects H-UnrelatedFailure; an
inconsistent continuation selects H-GeneratedContinuationMismatch.

## Exact commands

1. Use `rg -n` for `0x8000834C`, `0x80007904`,
   `matchKeywordWithPriority`, and `slotDispatcherIter`; inspect bounded
   windows around every generated and runtime boundary.
2. Compare generated continuation/return forms against retail context and
   record all sites in one table.
3. Require an explicit control-flow edge before selecting a hypothesis; keep
   behavior frozen if no edge can be proven.
