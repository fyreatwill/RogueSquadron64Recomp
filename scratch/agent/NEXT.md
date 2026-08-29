# NEXT work unit — audit the retail VI handoff callers

HYPOTHESIS-ID: m5-audio-route-upstream-retail-boundary

## Single work unit

Perform a bounded static caller/data-flow audit around
`freeRenderSubsystemResources` (`0x80018650`) and its call into
`selectAndApplyViMode`. Enumerate every caller and classify whether it can
run during the retail 640-to-1024 transition. Select exactly one new
transition-capable instruction for a later oracle capture; do not add a port
probe or change behavior in this unit.

## Competing hypotheses

- H-AlreadyEnumerated: all callers of the cleanup/wrapper chain are known
  boot-only or pre-title; the missing handoff is outside this chain.
- H-NewStaticCaller: a caller in the chain is transition-capable and supplies
  one new PC for the next retail oracle boundary capture.
- H-StaticInsufficient: the available generated/decomp caller evidence cannot
  distinguish lifecycle or callsite identity; no oracle candidate is selected.

## Discriminating measurement

The complete caller census must include every generated/decomp reference to
`freeRenderSubsystemResources`, `selectAndApplyViMode`, and the containing
functions, with each caller classified from its surrounding control flow and
known phase markers. A transition-capable caller yields H-NewStaticCaller and
one exact PC; all callers proven pre-title yields H-AlreadyEnumerated; missing
or contradictory caller identity yields H-StaticInsufficient.

## Exact commands

```
rg -n 'freeRenderSubsystemResources|selectAndApplyViMode|80018650|8001BB6C' /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp --glob '!PORTING-STATE.md' --glob '!scratch/agent/soak_results/**'
rg -n 'freeRenderSubsystemResources|selectAndApplyViMode|80018650|8001BB6C' /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/syms --glob '*.c' --glob '*.h' --glob '*.toml'
```

Record the complete caller list and the selected classification in a new
`scratch/agent/s3132_m5_vi_caller_audit.md`. If H-NewStaticCaller is selected,
the following iteration must run one oracle watch for that exact PC with the
same whole-RDRAM, title, and hangar controls.
