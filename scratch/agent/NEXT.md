# NEXT work unit (s1093)

HYPOTHESIS-ID: oracle-delay-slot-callback-semantics

Perform one bounded ground-truth source audit of the debugger execution
callback path for the retail oracle. Read the callback registration and
dispatch implementation in `/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core`, then inspect the oracle's `--watch-pc` callback and
hit attribution. Do not run a new ROM capture unless the source audit exposes
a concrete callback ambiguity that requires one controlled confirmation.

Competing hypotheses and discriminator:

* H-delay-callback-omits: the core invokes execution callbacks only for
  non-delay-slot or instruction-boundary PCs, so zero hits at 9B8/9BC and odd
  loop PCs are callback coverage, not absent retail execution.
* H-retail-skips: the retail branch reaches 0x8006D980 but the observed zero
  PCs are genuinely not executed because of the branch/delay control flow.
* H-watch-attribution: the callback fires but the oracle's inclusive range or
  PC normalization misattributes the missing addresses.

Discriminating measurement: source-level control-flow evidence must identify
whether the debugger callback is invoked for MIPS delay slots and whether the
oracle maps a single-PC watch to exactly that PC. A concrete callback contract
selects H-delay-callback-omits or H-watch-attribution; absence of such a rule
leaves H-retail-skips open and requires a new positive-control capture next.

Exact commands:

```sh
rg -n "DebugSetCallbacks|DebugCallback|EXEC|breakpoint|delay|pc" \
  /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src \
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/rs64_oracle.c
sed -n '1,220p' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger.c
```

Record the callback contract and update the ledger. Keep the current oracle
capacity increase; it is required by the established discriminator.
