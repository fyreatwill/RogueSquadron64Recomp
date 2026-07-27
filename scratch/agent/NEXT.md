# NEXT work unit — M3: contain evalCubicSplineAtTime NaN Abort

s82: sane-width last-drawn gate **kept** (G1). Hangar-flight content returns,
but process dies ~hold+6s on:

```
Assertion failed: (ctx->f28.fl == ctx->f28.fl), function evalCubicSplineAtTime,
file funcs_4.c, line 25117
```

via `buildPositionAndCallTransformHelper` → menu overlay path. Blocks HOLD_S=60.

## Competing hypotheses

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| N1 | NaN f28 is rare bad input; soft-return is safe | log fires; process survives hold_30+; hangar content continues |
| N2 | Soft-return corrupts transform state | survives assert but geometry explodes / new SIGBUS / freeze earlier |
| N3 | Assert is not on hangar-flight critical path once gated | soft-return; content identical to s82 freeze pattern (S1 only) |
| N4 | Death is not this assert (race / secondary) | no `[spline-nan]` log before Abort; different stack |

## Discriminating measurement (ONE build)

Locate `evalCubicSplineAtTime` assert in `RecompiledFuncs/funcs_4.c` (or via
fixup if regen-safe). Replace assert with rate-limited log + early return
(preserve prior outputs / skip update). Prefer `tools/fixup_game_funcs.py`
so regen keeps it.

```bash
# find site
rg -n 'evalCubicSplineAtTime|f28\.fl == ctx->f28' RecompiledFuncs/funcs_4.c | head
# after soft-return (+ fixup if needed):
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cmake --build build -j8
env PROBE_MODE=start_only HOLD_S=30 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh spline1 0 12
# offline: grep -c spline-nan run.log; process alive hold_30?; black% hold_*;
# compare hold freeze pattern to ldgate1
```

### Outcomes
- **N1/N3:** proceed HOLD_S=60 craft stick (M3 DoD).
- **N2:** narrower skip (only when isnan) or quarantine the caller.
- **N4:** re-capture stack; different site.

## Do not
- Re-litigate G1–G4 / rebuild the last-drawn gate.
- Treat frozen hangar content as M3 DoD (need craft response + 60s).
- Chase S1 FULL_SYNC until soak can survive past hold_30.
