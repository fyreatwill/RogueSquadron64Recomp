# NEXT work unit (s2338) — M5 parent caller reachability

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of the two parent edges
that feed the child callers found absent in s2337:
`tickAudioChannel` entry `0x8008BC10` and its static edge to
`soundMacroOpPlaySampleKeymap` at `0x8008C454`; and `serviceVoicePoolFrame`
entry `0x8009B5A8` and its static edge to `startStreamedSampleVoice` at
`0x8009B784`. Add durable target-phase/ordinal-keyed parent-entry and
immediately-pre-call markers. Retain the s2337 child-entry/pre-call markers,
s2336 direct-callsite/callee-entry/store probes, and all route/task/DMA/
guest-receive/PCM/filter controls. Do not add a store, remap, slot value,
guard, default, consumer, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: retail parent PCs, both port arms, target render/key-on
  work, or target-phase host controls are absent.
- H-PortParentInactive: both parent entries are zero in both arms during the
  target phases, matching the s2337 child-caller nulls.
- H-PortParentBranchBypassed: a parent entry is positive, but its exact
  pre-call marker is zero on the same arm/phase; parent logic bypasses the
  child edge.
- H-PortParentDispatchFault: a parent pre-call marker is positive, but the
  child entry or retained direct-callsite/callee-entry row is zero on the same
  arm/phase; the cross-function dispatch/edge is the remaining boundary.

The discriminator is one table keyed by
`(arm, phase, width, origin, ordinal, row, event, caller, edge)` containing
retail PC counts for `0x8008BC10`, `0x8008C454`, `0x8009B5A8`, and
`0x8009B784`, plus parent entry/pre-call, retained child entry/pre-call,
direct-callsite, callee-entry/store, render, key-on, task/DMA,
guest-receive, PCM, filter, and host-control rows. Require positive retail
whole-RDRAM/target/status/title/hangar controls and positive target-phase host
controls in both arms before reading a port zero. Select H-PortParentInactive
only when both parent entries and both parent pre-call markers are zero.
Select H-PortParentBranchBypassed only with a positive same-key parent entry
and zero parent pre-call marker. Select H-PortParentDispatchFault only with a
positive same-key parent pre-call marker and a zero child entry, direct
callsite, or callee-entry row. Any missing control selects H-CoverageInvalid;
otherwise report H-Unresolved rather than changing behavior.

## Exact commands

The retail preflight in the new driver must arm whole-RDRAM and physical
target-window controls, title/hangar origins, mode/gate/status controls, and
`--watch-pc` for the four parent PCs plus the retained child/descriptor,
key-on/decode/filter/service controls.

    mv ../N64Recomp/RecompiledFuncs ../N64Recomp/RecompiledFuncs.s2338-before
    python3 ../rogue_squadron64/tools/make_elf.py
    (cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
    (cd ../N64Recomp && python3 fixup_game_funcs.py)
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2338_m5_parent_caller_reachability.sh
    zsh scratch/agent/run_s2338_m5_parent_caller_reachability.sh s2338_m5_parent_caller_reachability
