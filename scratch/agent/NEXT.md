# NEXT work unit — enumerate the retail PCM producer’s external dispatch sites

HYPOTHESIS-ID: m5-retail-producer-dispatch

Session 3405 passed all controls but found only self-reentry at
`0x800078EC`: 9,699 hits, all `exec-prev=0x800078EC`; `0x80033300`,
`0x800078E8`, `0x8002BEE8`, and `0x8002BEEC` were zero. The earlier
`0x8002BEEC` attribution is stale or route-dependent and must be reconciled
before port instrumentation.

Competing hypotheses:

- `H-StaticCallsite`: a statically enumerated JAL/callsite in the retail
  `0x800078EC` body or its immediate caller chain is the external dispatch
  site and will execute in the completion-safe route.
- `H-IndirectDispatch`: no direct JAL identifies the edge; a function-pointer
  or overlay dispatch site must be watched instead.
- `H-RouteMismatch`: the earlier `0x8002BEEC` edge belongs to a different
  route, so neither static candidate set executes during this route.

Discriminator: perform one bounded disassembly/callsite enumeration of the
retail `0x800078EC` function and its immediate callers, producing one complete
candidate table. Then run one completion-safe oracle census watching every
candidate plus `0x800078EC`, with whole-RDRAM, `0x1935E0`, title/hangar, and
phase-histogram controls. A candidate with nonzero count and an `exec-prev`
relation to the producer selects the static edge; only indirect candidates
firing selects indirect dispatch; no external candidate firing with controls
live selects route mismatch.

Commands:

    rg -n "0x800078EC|800078ec|func_800078EC" /Users/williambuckley/Documents/Tools/rogue_squadron64
    # Read bounded windows around the identified body/callsites, then substitute
    # the complete candidate list in the oracle command.
    env tools/oracle/build/rs64_oracle ...

The oracle run must retain the whole-RDRAM positive control and be SIGKILL-safe.
Do not add port instrumentation until the retail external dispatch site is
named.
