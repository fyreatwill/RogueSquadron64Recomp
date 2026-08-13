# NEXT work unit (audit the VI-width transition writer)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s800 capture verified the 640 gate and phase-relative keys, then stayed at
VI 640 for 90 frames with no parser controls. Before another run, enumerate the
writer and consumer of the VI width/origin transition in the port and identify
one concrete gate that can explain why 1024 is never published. Do not build or
instrument until the audit names the candidate and its independent ground-truth
control.

## Competing hypotheses

- H-width-writer: one port-side VI writer or its source state prevents the
  1024 publication. Prediction: source audit finds a concrete writer/gate and
  its input has a ground-truth analogue in the retail watch data.
- H-renderer-consumer: VI 1024 is published but presentation/measurement reads
  stale 640 state. Prediction: writer and consumer are distinct, and a direct
  VI-state trace shows 1024 before the phase observer sees it.
- H-game-state: the game never requests the 1024 mode under this recipe.
  Prediction: no port-side suppression exists and the oracle/watch point shows
  no corresponding retail write in the same phase.

## Discriminating measurement

The discriminating result is the audit’s writer/gate map plus an independent
retail watch or existing oracle trace for the same state. A concrete port
suppression with a retail counterpart selects H-width-writer; a 1024 write
before the observer selects H-renderer-consumer; absence in both selects
H-game-state. If the audit cannot produce this split, do not instrument.

## Exact commands

```sh
rg -n -S "vi_width|VI width|update_screen|origin|PROBE_PHASE_WIDTH|640|1024" \
  src lib tools ../N64Recomp/RecompiledFuncs docs
rg -n -S "VI_STATUS|VI_ORIGIN|VI_WIDTH|0x044000|0x0440000[4-9]" \
  src lib ../N64Recomp/RecompiledFuncs
rg -n -S "watch|physical|VI" tools/oracle docs/F5-UCODE-REFERENCE.md
```
