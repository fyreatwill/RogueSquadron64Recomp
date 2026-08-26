# NEXT work unit (s2477) — design and implement the host-local continuation bridge

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

s2476 exhaustively classified the only variable-register indirect tail in the
generated tree. `convertMat3x4ToN64Mtx` dispatches through the guest `$ra`, and
the legitimate `0x800155EC` value is the caller's local `after_4` continuation,
not a registered function-map entry. The next unit is one bounded bridge change
with a validation build/run.

## Competing hypotheses

- H-BridgeGenerated: the fixup can lower this edge as a special continuation
  bridge that invokes the converter and then resumes the caller's existing
  `after_4` path without `get_function`.
- H-BridgeRuntime: a reusable runtime continuation API is required; one bridge
  registration/dispatch mechanism can represent the guest continuation while
  preserving the shared context.
- H-TailContractStillWrong: even with the known PC+8 link, the converter's
  `jr $t9` is not intended to return to the generated caller path, so either
  the generated caller or the tail lowering must be corrected differently.

## Discriminating measurement

Implement one bridge arm selected from the static audit, build once, and run
the qualified route. A run that passes `0x800155EC` without a
`Failed to find function`/`get_function(0)` and reaches the next existing
`after_4` work selects H-BridgeGenerated or H-BridgeRuntime according to the
bridge layer. A repeat failure at `0x800155EC` proves the bridge did not replace
the map lookup. A clean return followed by a different, immediate converter
contract failure selects H-TailContractStillWrong. Preserve the same-run
indirect resolver positive control and phase gate any later M5 interpretation.

## Ground-truth and safety gate

Before any new runtime instrument, verify the retail oracle whole-RDRAM
positive control and driven-VI control are available. No mitigation or NULL
stub is authorized; the legitimate writer remains the JAL at `0x800155E4`, and
the legitimate value remains `0x800155EC`.

## Commands

```sh
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
rg -n 'convertMat3x4ToN64Mtx|after_4|LOOKUP_FUNC\(ctx->r25\)' ../N64Recomp/RecompiledFuncs/funcs_4.c tools/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from `build/` with the ROM present, use the qualified LLE route, capture
the log to a non-dot final path, and kill the process with SIGKILL. Record the
bridge source and result in `scratch/agent/s2477_m5_continuation_bridge/`.
