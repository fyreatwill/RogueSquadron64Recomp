# NEXT work unit (enumerate reachable VI mode callers)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s802 selector trace proved that the generated `selectAndApplyViMode`
caller and function are not reached in the tested 0→320→640 recipe, while
other `osViSetMode` calls are live. The next unit is a read-only source audit,
not another selector run: enumerate every generated `osViSetMode_recomp` call,
its guest address/function, mode pointer expression, and whether its mode is
320/640/1024. Then select one reachable 640→1024 gate for the next batched
trace.

## Competing hypotheses

- H-direct-caller: a reachable direct caller selects the 640 mode and owns the
  missing transition. Prediction: the post-640 call sites are outside
  `selectAndApplyViMode` and one has a concrete 1024-capable mode pointer.
- H-overlay-dispatch: the intended selector call is emitted but dispatch or
  overlay registration routes around it. Prediction: static call is reachable
  from the active state path, but runtime callsite control remains absent while
  another overlay implementation owns the live calls.
- H-recipe-state: no reachable caller has a 1024 mode in this recipe.
  Prediction: all live mode pointers decode to 320/640, and the missing 1024
  request is game-state/input dependent.

## Discriminating measurement

The exhaustive caller-to-mode table is the discriminator: one reachable
1024-capable caller that is never invoked selects H-direct-caller or
H-overlay-dispatch depending on dispatch ownership; an exhaustive 320/640-only
set selects H-recipe-state. Do not build until every callsite is classified.

## Exact commands

```sh
rg -n -S "osViSetMode_recomp|selectAndApplyViMode|0x8001BB6C|jal.*800352D0" \
  ../N64Recomp/RecompiledFuncs src lib
rg -n -S "RECOMP_FUNC void .*\(" ../N64Recomp/RecompiledFuncs/funcs_*.c | \
  rg "osViSetMode|selectAndApplyViMode"
```

If the audit identifies a concrete reachable gate, the following unit must
batch its callsite marker with the existing `[osViSetMode]` logger and retain
the oracle `--watch-write 0x0:0x800000 --vi-trace` positive control. Use
`PROBE_PHASE_WIDTH=640 PROBE_LEAVE_OK=1`, never a stopwatch.
