# NEXT work unit (s1140)

HYPOTHESIS-ID: m3-runtime-frame-contract

Perform one whole-class source audit of generated indirect-call frame
contracts for the recurring `slotDispatcherIter+872` SIGBUS. Do not build or
run the game. Enumerate every `LOOKUP_FUNC` site in the generated tree that
can reach `slotDispatcherIter` or its callback chain, then classify the caller
frame setup/teardown, saved return register, and host `get_function` wrapper:

```sh
rg -n 'LOOKUP_FUNC|slotDispatcherIter' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/lib/N64ModernRuntime/librecomp/src
rg -n 'slotDispatcherIter|0x8003E8DC' /Users/williambuckley/Documents/Tools/N64Recomp /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/docs --glob '!PORTING-STATE.md'
```

Competing hypotheses and the discriminating measurement:

- H-static-unbalanced: at least one reachable indirect caller has a missing
  frame restore, wrong saved-`ra` handling, or an incompatible host wrapper;
  identify the exact site and contract defect.
- H-static-balanced-runtime: every reachable site has balanced generated
  frames and the wrapper preserves the recomp context contract; static frame
  shape is ruled out and runtime-side corruption remains open.
- H-wrong-target: a call resolves to an unintended overlay/function target;
  the target map shows a concrete mismatch even though each local frame is
  balanced.

The discriminating table is one row per reachable call site, including target
resolution evidence and entry/exit stack deltas. A partial grep or a counter
is not a result. If all sites balance, do not add a mitigation; choose the
next runtime-origin probe.
