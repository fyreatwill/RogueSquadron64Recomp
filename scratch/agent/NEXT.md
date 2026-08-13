# NEXT work unit (make the VI argument probe non-invasive, then capture)

HYPOTHESIS-ID: m3-vi1024-boot-crash-pivot

Perform one bounded change: update the regeneration-safe `[vi-arg]` probe in
`../N64Recomp/fixup_game_funcs.py` so it logs `ctx->r5` and `ra` only, with no
`MEM_BU` dereferences. Regenerate/fix up, build, and run one phase-gated
capture using the existing s813 recipe and all its positive controls. Do not
add a game-logic guard or infer caller-state legitimacy from the old probe.

## Competing hypotheses

- H-probe-only: removing the probe dereferences lets the run pass the old
  pre-gate crash and yields argument-pointer records; the prior crash was
  instrumentation-only.
- H-underlying-state: the probe was only exposing a bad caller pointer; after
  removal, the game/runtime still crashes at the same phase or a corresponding
  legitimate access fails.
- H-independent: the old PC/operand mapping was stale or non-unique; the
  probe-safe run reaches 1024 with no corresponding caller-pointer failure,
  leaving the earlier crash unrelated to argument state.

## Discriminating measurement

The same-run split is: probe-safe capture outcome plus `[vi-arg]` pointer
records and positive controls. Passing the pre-gate point with records
advances H-probe-only; the same pre-gate crash without probe dereferences
advances H-underlying-state; reaching the 1024 gate with no pointer failure
advances H-independent. A null is invalid unless host-VI, phase, and E9
positive controls all fire.

## Exact commands

```sh
python3 ../N64Recomp/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env zsh scratch/agent/s790_postsec2_reachability.sh
```

The capture script launches the game from `build/`, gates on VI 1024, carries
the host-VI/E9 positive controls, and kills the game on completion; preserve
its generated directory under `scratch/agent/soak_results/`.

The probe edit must be made in the fixup script, not in generated
`RecompiledFuncs/funcs_4.c`.
