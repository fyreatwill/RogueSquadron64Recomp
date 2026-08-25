# NEXT work unit (s2339) — M5 scheduler/callback source reachability

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of the next source edges
above the s2338 parent nulls:
`tickAllAudioChannels` entry `0x8008C9AC` and its static edge to
`tickAudioChannel` at `0x8008CA14`; and the VI callback dispatch `jalr` at
`0x80019B74`, including the selected callback target identity for the
registered `serviceVoicePoolFrame` target `0x8009B5A8`. Retain all s2338 parent
and child markers, target-phase route/task/DMA/guest-receive/PCM/filter
controls, and the retail callback-registration control. Do not add a store,
remap, callback, slot value, guard, default, consumer, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: retail source PCs or callback registration, both port
  arms, target phases, or any retained positive control are absent.
- H-PortSchedulerParentInactive: `tickAllAudioChannels` entry and its exact
  pre-call marker are both zero in both arms, while its retail entry/edge and
  the route controls are positive.
- H-PortCallbackDispatchInactive: the callback dispatcher marker/target row is
  zero in both arms while the retail dispatcher and callback-registration
  controls are positive.
- H-PortCallbackTargetMismatch: the port callback dispatcher is positive but
  its target identity never equals `0x8009B5A8`, despite positive registration;
  a target row equal to `0x8009B5A8` followed by the retained service-entry
  null selects H-PortServiceEntryBoundary instead.

The discriminator is one table keyed by
`(arm, phase, width, origin, ordinal, row, event, source, edge, target)` with
retail execution counts for `0x8008C9AC`, `0x8008CA14`, `0x80019B74`,
`0x80007910`, and `0x8009B5A8`, plus port scheduler entry/pre-call,
callback-dispatch/target, all s2338 parent and child rows, render/key-on,
task/DMA, guest-receive, PCM, filter, and host-control rows. Require positive
retail whole-RDRAM/target-window/mode/gate/status/title/hangar controls and
positive target-phase host controls in both arms before reading a port zero.
Select H-PortSchedulerParentInactive only when both scheduler rows are zero;
select H-PortCallbackDispatchInactive only when callback dispatch/target rows
are zero with registration positive; select H-PortCallbackTargetMismatch only
when dispatch is positive but no target is `0x8009B5A8`. Otherwise report
H-Unresolved rather than changing behavior.

## Exact commands

The retail preflight must arm whole-RDRAM and physical target-window watches,
title/hangar origins, mode/gate/status watches, callback-table registration
(`0x0011A8A4:0x0011A8B4`), and `--watch-pc` for the scheduler entry/edge,
callback dispatcher/registration, service target, and all retained s2338
child/descriptor/key-on/decode/filter/service controls.

    python3 ../rogue_squadron64/tools/make_elf.py
    (cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
    (cd ../N64Recomp && python3 fixup_game_funcs.py)
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2339_m5_scheduler_callback_source.sh
    zsh scratch/agent/run_s2339_m5_scheduler_callback_source.sh s2339_m5_scheduler_callback_source
