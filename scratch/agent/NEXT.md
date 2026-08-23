# NEXT work unit (s2206) — isolate the post-target VI logger boundary

HYPOTHESIS-ID: m5-a1-vi-toggle-logger-isolation

## Work unit

Run one same-build concurrent four-arm table with the qualified silent-audio
route:

- `logged-control`: `ROGUESQ_VI_ALTERNATE_FIELDS=0` and
  `ROGUESQ_LOG_VI_CONTEXT_PORT=1`;
- `logged-alternate`: `ROGUESQ_VI_ALTERNATE_FIELDS=1` and
  `ROGUESQ_LOG_VI_CONTEXT_PORT=1`;
- `quiet-control`: `ROGUESQ_VI_ALTERNATE_FIELDS=0` without the context logger;
- `quiet-alternate`: `ROGUESQ_VI_ALTERNATE_FIELDS=1` without the context logger.

All four arms use `ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, and `ROGUESQ_LOG_PHASE=1`.
Create and run a self-contained
`scratch/agent/run_s2206_vi_toggle_logger_isolation.sh` from the repository
root. The runner must launch all four instances from `build/`, require an
early `640 @ 0x0066A500` phase control in every arm, require a target
`640 @ 0x00696100` phase in every quiet arm, and require a target committed
row with `framebuffer=0x00695C00` in every logged arm. Continue each arm until
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, exit, or its 180s
watchdog expires. Kill only with SIGKILL. Report logged target commit origins,
quiet target phase origins, later phases, `[CRASH]`/`[ABORT]` markers, and each
arm's terminal result.

Do not change the VI default, add a port guard, rewrite a task, or change audio
dispatch. This is a logger-isolation measurement, not a mitigation.

## Competing hypotheses and discriminator

- H-ContextLoggerStarvesPostTarget: the capped context logger changes
  cooperative scheduling or VI publication; quiet arms reach title and hangar
  while logged arms stall after target 640, with the field toggle still
  determining the logged commit origin.
- H-ViToggleLaterEffect: the logger is not the boundary; within each logger
  state the alternate arm reaches the target but loses a later phase or adds a
  crash relative to its same-state control.
- H-PostTargetConsumer: removing the logger does not restore title/hangar;
  alternate arms can show the sibling target commit/phase, but all arms stop
  before the later phases, locating the unresolved boundary after VI state
  selection.
- H-NonTargetRouteDamage: one or more quiet arms fail the early positive or
  target phase while its same-build logged counterpart passes, so the current
  target result is not stable outside the diagnostic path.

The discriminator is one four-arm table keyed by logger state and field
selector, with per-arm early/target positive controls, target-origin rows or
phase origins, title/hangar counts, crash markers, and terminal status.
H-ContextLoggerStarvesPostTarget requires both quiet arms to reach the later
phases while both logged arms do not. H-ViToggleLaterEffect requires a
within-logger-state alternate/control later-phase or crash difference with
positive controls in both arms. H-PostTargetConsumer requires later-phase loss
in both logger states despite the alternate target evidence. H-NonTargetRouteDamage
requires a quiet arm's missing control/target result with its logged counterpart
positive. A null is invalid without the per-arm controls in that same run.

## Exact commands

```sh
cmake --build build -j8
zsh scratch/agent/run_s2206_vi_toggle_logger_isolation.sh
rg -n "vi-context-port|\[phase\] vi_width=(640|1024|512)|\[CRASH\]|\[ABORT\]|s2206-summary" \
  scratch/agent/s2206_vi_toggle_logger_isolation/*.log
```
