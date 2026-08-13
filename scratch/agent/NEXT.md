# NEXT work unit (trace initVideoSubsystem argument-state population)

HYPOTHESIS-ID: m3-vi1024-argument-state

Run one bounded source-to-callsite audit of every reachable call to
`initVideoSubsystem`, identifying the argument structure and each writer of
the bytes at offsets `0x1EF`, `0x1F3`, and `0x1FF` that become the selector
stack bytes. Then run one phase-gated capture with a batched entry marker at
the reachable caller and the existing `[vi-gate]`, host VI/mode, E9, writer,
and phase-relative key controls. Do not change mode data or add a mitigation.

## Competing hypotheses

- H-argument-state-intended: the caller supplies a legitimate 1024-capable
  argument state; source and capture agree on the three input bytes and the
  later `stack15f=0`, `stack17f=0`, `fp_nonzero=1` predicate.
- H-argument-state-miswritten: a reachable writer corrupts or overwrites one
  of those bytes before the later call; source identifies the writer and the
  capture orders its value against the 1024 call.
- H-argument-state-unresolved: the callsite or writer is not reachable in the
  tested recipe; the positive controls fire but no attributable argument
  record precedes the 1024 call.

## Discriminating measurement

The complete caller/writer inventory joined to the same-run argument values,
writer ordering, and the 1024 `[vi-gate]` record splits the hypotheses. A
marker proving only that `initVideoSubsystem` ran is insufficient.

## Exact commands

```sh
rg -n -C 35 'initVideoSubsystem\(rdram|0x8001A098|0x8001B720' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'MEM_[BWH].*0X1EF|MEM_[BWH].*0X1F3|MEM_[BWH].*0X1FF|0X1EF|0X1F3|0X1FF' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'initVideoSubsystem|vi-gate|video-state-update' ../N64Recomp/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Use the s808 fixed phase-gated recipe from `scratch/agent/last_s808_fixed_out`
as the capture baseline, with `ROGUESQ_LOG_VI_CALLERS=1`,
`ROGUESQ_LOG_VI_WRITERS=1`, E9 provenance controls, and SIGKILL watchdog.
Expected outcomes: matching writer/value ordering advances
H-argument-state-intended; a concrete pre-call overwrite advances
H-argument-state-miswritten; no attributable record with all controls live
advances H-argument-state-unresolved. No skip, guard, restore, or other
mitigation is authorized.
