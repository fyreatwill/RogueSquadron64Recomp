# NEXT work unit (capture initVideoSubsystem argument-state values)

HYPOTHESIS-ID: m3-vi1024-argument-state

Run one bounded phase-gated capture using the fixed `[vi-arg]` probe at both
reachable `initVideoSubsystem` callers. The source audit is complete: callers
are `advanceVideoFrame` sites `0x80018378` and `0x80018564`, and no generated
store targets argument offsets `0x1EF`, `0x1F3`, or `0x1FF`. Four fixed-recipe
attempts died before the 1024 gate in the same boot crash family, so this unit
must obtain a 1024-gated record before interpreting argument state. Do not
change mode data or add a mitigation.

## Competing hypotheses

- H-argument-state-intended: a reachable caller supplies a legitimate
  1024-capable argument state; `[vi-arg]` values precede the 1024
  `initVideoSubsystem` call and agree with its derived predicate.
- H-argument-state-miswritten: a reachable writer corrupts or overwrites one
  of those bytes before the call; source and `[vi-arg]` ordering identify it.
- H-argument-state-unresolved: the recipe reaches 1024 only intermittently or
  the caller record is absent while host-VI and E9 controls are positive.

## Discriminating measurement

Require all of: `[phase] vi_width=1024`, host VI/mode control, and an E9 record
with `emit=1 raw=1 dispatch=1 match=1`. Then compare `[vi-arg]` values and
callsite ordering against the 1024 `[vi-gate]` record. Matching values advance
H-intended; a concrete pre-call overwrite advances H-miswritten; no argument
record with all controls live advances H-unresolved. A boot crash or width-320
null is unevaluable and must not be classified.

## Exact command

```sh
OUT="scratch/agent/soak_results/s812_vi1024_argument_state_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 \
  ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 \
  ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_DL_SYNC=1 \
  ROGUESQ_LOG_DL_SYNC2=1 ROGUESQ_LOG_FL_ZERO_WATCH=1 \
  ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 \
  ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_VI_CALLERS=1 \
  ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_VI_ARGS=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
  zsh tools/probe.sh "$OUT" 300 2
```
