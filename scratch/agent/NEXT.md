# NEXT work unit — audit the two surviving retail handoff callers

HYPOTHESIS-ID: external-retail-wrapper-chain-static-audit

## Single work unit

Perform one bounded static call-chain audit of retail `osViSwapBuffer`
predecessors `0x8001BE24` and `0x80019B14`, tracing each body and its direct
callees toward the title/hangar VI-mode writer. The oracle reached both target
phases but found no new predecessor, so do not build or add port
instrumentation unless this audit identifies a new boundary.

## Competing hypotheses

- H-DirectModeWrapper: one surviving predecessor or its direct callee owns the
  mode/descriptor decision used by title and hangar.
- H-SharedSwapPath: both predecessors are generic buffer-swap wrappers and the
  mode writer is an upstream shared caller, outside these bodies.
- H-OverlayAlias: the address is reached through an overlay-aliased generated
  entry, so companion identity and overlay registration disagree with the
  static call chain.

## Discriminating measurement

For each predecessor, record the exact generated body, direct callsites,
callee identities, companion-map identity, and any static path to
`osViSetMode` or the mode descriptor fields. A unique mode-writer path selects
H-DirectModeWrapper; only generic swap operations plus an upstream writer
selects H-SharedSwapPath; disagreement between generated registration and the
companion identity selects H-OverlayAlias. If neither body/callee chain can
reach the decision, leave the route unresolved and document the boundary.

## Exact commands

1. `rg -n "8001BE24|80019B14|80035500|osViSetMode|80128E" RecompiledFuncs src lib`
2. Use bounded `sed` windows around every hit, then inspect the companion map,
   generated header/registration, and project TOML for both predecessor
   addresses.
3. Save the call-chain table and selected hypothesis under
   `scratch/agent/s3105_external_retail_wrapper_chain/`.
