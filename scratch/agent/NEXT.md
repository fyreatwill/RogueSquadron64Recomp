# NEXT work unit (instrument the VI-mode selector gate)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s801 audit found that the live consumer is faithful, while the game-side
selector at `0x8001BB70–0x8001BBC0` chooses only 640-wide modes in the tested
recipe. Run one phase-gated capture logging selector bytes at `0x8012A865–867`,
the selected mode pointer/width, and every `osViSetMode` call. Keep existing
parser positive controls and phase-relative keys; do not alter runtime
behavior.

## Competing hypotheses

- H-selector-state: selector inputs stay on the 640 branch. Prediction:
  selector-byte changes and selected mode pointers explain every 640 call, with
  no 1024 request.
- H-selector-dispatch: selector reaches a 1024-capable branch but a call or
  overlay dispatch loses it. Prediction: selector state indicates 1024 while
  the mode log remains 640.
- H-recipe-state: the port game state never requests the retail 1024 phase.
  Prediction: selector inputs remain 640-only; the independent oracle still
  shows retail 1024 under its driven schedule.

## Discriminating measurement

One same-run selector trace splits the hypotheses: a 1024-capable selected mode
with a 640 `osViSetMode` call selects H-selector-dispatch; only 640 selector
inputs selects H-selector-state/H-recipe-state. Retain the oracle whole-RDRAM
positive control and VI trace; retail's existing 17.3s driven 1024 transition
is the independent control, not the port log.

## Exact commands

```sh
rg -n -S "vi_width|VI width|update_screen|origin|PROBE_PHASE_WIDTH|640|1024" \
  src lib tools ../N64Recomp/RecompiledFuncs docs
rg -n -S "VI_STATUS|VI_ORIGIN|VI_WIDTH|0x044000|0x0440000[4-9]" \
  src lib ../N64Recomp/RecompiledFuncs
rg -n -S "selectAndApplyViMode|8012A865|osViSetMode_recomp" \
  src ../N64Recomp/RecompiledFuncs
```

After the instrumented build, run the existing phase-gated recipe once. If a
new retail arm is needed, use `--watch-write 0x0:0x800000 --vi-trace` so the
whole-RDRAM positive control remains present.
