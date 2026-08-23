# NEXT work unit (s2205) — validate opt-in VI field alternation across later phases

HYPOTHESIS-ID: m5-a1-vi-field-toggle-stability

## Work unit

Run one same-build concurrent A/B with the qualified silent-audio route:
control uses `ROGUESQ_VI_ALTERNATE_FIELDS=0` and the alternate arm uses
`ROGUESQ_VI_ALTERNATE_FIELDS=1`. Common variables are
`ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_LOG_PHASE=1`, and
`ROGUESQ_LOG_VI_CONTEXT_PORT=1`. Create and run a self-contained
`scratch/agent/run_s2205_vi_toggle_stability_ab.sh` from the repository root.
It must launch both game instances from `build/`, gate each arm on a target
640 commit row (`framebuffer=0x00695C00`), then collect until that arm reaches
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, exits, or its 180s
watchdog expires. Kill only with SIGKILL. Report target rows, both later phase
transitions, `[CRASH]`/`[ABORT]` markers, and each arm's exit/watchdog result.

The alternation knob stays opt-in during this validation. Do not make it
default-on, add a port guard, rewrite a task, or change the audio dispatch.

## Competing hypotheses and discriminator

- H-ViToggleStable: the explained field-selector difference is isolated to
  the target 640 transition; the alternate arm reaches the second target
  origin and both arms retain title 1024 and hangar 512 without a new crash
  family.
- H-ViToggleRouteRegression: alternation reaches the target origin but changes
  the later 1024 or 512 route, or increases crash markers versus control.
- H-ViToggleNonTargetDamage: alternation changes the 320/early-640 state
  enough that it never reaches the target window, even though the current
  target-scoped table matches the retail frame/mode tuple.

The discriminator is one same-build phase table with positive target rows,
target-origin counts, title and hangar phase counts, crash markers, and exit
status for both arms. H-ViToggleStable is selected only if the alternate arm
gets target rows plus both later phases and does not add a crash marker or
lose the control arm's later phases. H-ViToggleRouteRegression is selected by
a target-reaching alternate arm with a later-phase loss or new crash marker.
H-ViToggleNonTargetDamage is selected if the alternate arm's all-width control
fires but its target rows are absent while the control reaches the target.
A null is invalid without the per-arm positive-control prefix and target
phase control in that same log.

## Exact commands

```sh
cmake --build build -j8
zsh scratch/agent/run_s2205_vi_toggle_stability_ab.sh
rg -n "vi-context-port|\[phase\] vi_width=(640|1024|512)|\[CRASH\]|\[ABORT\]|s2205-summary" \
  scratch/agent/s2205_vi_toggle_stability_ab/*.log
```
