# NEXT work unit (s2337) — M5 descriptor source/caller reachability

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of the two enclosing
callers of `musyxInitVoiceFromSample`: `soundMacroOpPlaySampleKeymap` at
`0x8008A38C` / callsite `0x8008A564`, and `startStreamedSampleVoice` at
`0x80097FE8` / callsite `0x800980EC`. Add durable entry probes and
phase/ordinal-keyed markers immediately before both exact `jal` edges. Retain
the s2336 callsite and callee-entry/store probes as downstream controls. Keep
the qualified Factor 5 image arm, silent control, eleven-Start route,
`ROGUESQ_DRAIN_INLOOP_TICK=1`, host-positive filter/voice control, and all
task/DMA/guest-receive/PCM controls. Do not add a store, remap, slot value,
guard, default, consumer, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the retail caller/callsite controls, both port arms,
  target render/key-on rows, or target-phase host controls are absent.
- H-PortCallerInactive: both port caller-entry probes are zero in the target
  phases, matching the zero direct-callsite probes; the route never reaches
  either enclosing caller.
- H-PortBranchBypassed: a port caller-entry probe is positive, but its
  immediately-pre-call marker is zero; the caller is live and its branch or
  selection logic bypasses the `musyxInitVoiceFromSample` edge.
- H-PortCallsiteInstrumentationFault: a pre-call marker is positive while its
  direct-callsite hook is zero (or the callsite is positive while the callee
  entry is zero); the remaining mismatch is in generated dispatch/probe
  placement rather than caller reachability.

The discriminator is one table keyed by
`(arm, phase, width, origin, ordinal, row, event, caller)` containing retail
PC counts for `0x8008A38C`, `0x8008A564`, `0x80097FE8`, and `0x800980EC`, plus
port caller-entry, pre-call, direct-callsite, callee-entry/store, render,
key-on, task/DMA, PCM, filter, and host-control rows. Require positive retail
whole-RDRAM/target/status/title/hangar controls and positive target-phase host
controls in both arms before reading a port zero. Select H-PortCallerInactive
only when both caller entries and both pre-call markers are zero. Select
H-PortBranchBypassed only with a positive caller entry and zero marker on the
same arm/phase. Select H-PortCallsiteInstrumentationFault only with a
positive same-key pre-call marker and a zero direct hook or callee entry. Any
missing control selects H-CoverageInvalid.

## Exact commands

Create `scratch/agent/run_s2337_m5_descriptor_source_reachability.sh` with the
same clean-output, SIGKILL, sequential stub/image harness shape as s2336.
Its retail preflight must arm whole-RDRAM and physical target-window controls,
title/hangar origins, mode/gate/status controls, and `--watch-pc` for the four
caller/callsite PCs above plus the existing entry/store/key-on/decode/filter/
service controls. The port table must include both caller entries and both
pre-call markers in the same target-phase key as the retained s2336 probes.

    python3 ../rogue_squadron64/tools/make_elf.py
    ../N64Recomp/build/N64Recomp rogue_squadron.toml
    python3 ../N64Recomp/fixup_game_funcs.py
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2337_m5_descriptor_source_reachability.sh
    zsh scratch/agent/run_s2337_m5_descriptor_source_reachability.sh s2337_m5_descriptor_source_reachability
