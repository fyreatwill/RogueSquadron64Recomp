# NEXT work unit (s2190) — phase-gated port writer-parity census

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Use the s2189 retail phase matrix as ground truth and add one batched,
phase-gated port diagnostic for all six physical target words. The generated
writer path must report `(target, guest writer PC, VI width, VI origin)` for
each target write at the two 640 origins. Route the diagnostic through
`../N64Recomp/fixup_game_funcs.py`; do not hand-edit generated output. This is
an attribution probe only: no guard, skip, task rewrite, or audio-default
change is permitted.

Before building, enumerate the existing generated sites and the fixup hook:

```sh
rg -n '80018F5C|80018F60|800078EC|800A8144|80057100|25A580|0CA748|0C7B0C|165E40|0CDB58|2231EC' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c ../N64Recomp/fixup_game_funcs.py
```

Add one rate-limited `ROGUESQ_LOG_M5_WRITER_PARITY=1` table through the fixup
path, then regenerate/build once:

```sh
python3 ../N64Recomp/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run one qualified route from the repository root. The existing phase and
title/hangar controls stay enabled in the same run:

```sh
export GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1 ROGUESQ_LOG_M5_WRITER_PARITY=1'
env GAME_EXTRA_ENV="$GAME_EXTRA_ENV" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2190_m5_writer_parity 30 12 \
  > scratch/agent/s2190_m5_writer_parity_driver.log 2>&1
```

Parse the positive 640 phase control, title `1024` and hangar `512` controls,
and one complete `target × origin × guest-PC` table into
`scratch/agent/s2190_m5_writer_parity.txt`. A phase row without any writer
rows is not a null result until the existing phase control and all six target
watch paths are visibly active.

## Competing hypotheses and discriminator

- H-PortRetailParity: for sparse targets 1/2/3/5/6, the port's writer-PC set
  at each origin matches the s2189 retail set; target 4 is broad in both.
- H-PortOriginMismatch: at least one target is written by a different PC or
  under the opposite origin bucket in the port.
- H-PortNoTargetWrites: the 640 phase control fires but the batched target
  table has no rows, locating the port/runtime boundary without authorizing a
  skip.
- H-PortCoverageFailure: the 640 or title/hangar controls do not fire, so the
  run cannot discriminate writer parity.

The discriminator is one same-run table of controls and all six target/origin
writer sets. It selects parity, an origin-specific mismatch, an active-path
boundary, or invalid coverage.
