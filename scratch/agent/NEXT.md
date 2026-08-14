# NEXT work unit (s1149)

HYPOTHESIS-ID: vi-post640-state-path

Audit the missing state-path edge before the game-side VI mode selector after
the final 640 producer call. Do not add a runtime guard or repeat the NPC
boundary test.

Competing hypotheses and discriminator before the work unit:

- H1/state predecessor: a known state-machine predecessor runs after the last
  640 producer call but its transition condition prevents the selector edge.
- H2/edge absent: no reachable predecessor invokes the selector in the active
  post-640 loop; slot/host/audio activity is a separate path.
- H3/target reached: a new bounded marker reaches the selector and the run
  reaches VI-1024 with positive task-control E9.

Discriminating measurement: enumerate every static predecessor of the sole
`selectAndApplyViMode` caller and add one phase-scoped marker at the highest
reachable predecessor, retaining the producer, selector-positive, slot,
host/audio, E9, and VI controls. A live predecessor with no selector call
selects H1; continued controls with no predecessor marker selects H2; selector
call plus VI-1024 and task-control E9 selects H3.

```sh
rg -n 'selectAndApplyViMode|0x8001BB6C|0x800186C0|osViSetMode_recomp|setViModeType' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src tools
rg -n 'state|mode|video|VI|selector' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_5.c | head -240
```

Expected outcomes:

- PREDECESSOR ACTIVE/H1: the state predecessor fires post-640 but the
  selector does not; audit its condition and state inputs.
- PREDECESSOR ABSENT/H2: controls continue but no predecessor marker fires;
  identify the active loop's separate owner.
- TARGET REACHED/H3: selector call, VI-1024, and positive task-control E9 all
  appear; then run the corrected-boundary crash comparison.
