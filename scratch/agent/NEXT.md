# NEXT work unit (s2340) — M5 scheduler caller reachability

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of the source immediately
above the s2339 `tickAllAudioChannels` null: `tickAudioSequencerFrame` entry
`0x8008D960` and its three static callsites at `0x800914A4`, `0x80091564`, and
`0x80091618`. Retain the s2338 parent/child rows, s2339 scheduler rows and VI
dispatcher target identity, target-phase route/task/DMA/guest-receive/PCM/
filter/render/key-on controls, and both stub/image arms. Add no gate, callback,
slot, state, store, default, guard, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the retail source PCs, callback registration, target
  phases, both port arms, or a retained positive control fail in this capture.
- H-PortSeqCallerInactive: all three port callsite markers and the
  `tickAudioSequencerFrame` entry marker are zero despite positive retail
  source PCs and live route/task controls.
- H-PortSeqPartialCallsite: only a subset of the three static callsites fires;
  per-callsite rows identify which gate/source remains reachable.
- H-PortSeqEntryActive: at least one callsite and the function entry fire in
  the target phase, while the retained `tickAllAudioChannels` entry remains
  zero; this selects an internal gate or branch inside the sequencer frame.
- H-PortSeqDispatchMismatch: a callsite marker fires but the direct callee
  entry stays zero in the same arm and phase; this would make the generated
  direct-call boundary, not a guest gate, the next audit target.

The discriminator is one table keyed by
`(arm, phase, width, origin, ordinal, row, event, source, edge, callsite,
target)`, with retail execution counts for `0x8008D960`, all three callsites,
the retained `0x8008C9AC`/`0x8008CA14` rows, VI dispatcher/registration and
`0x8009B5A8` target identity, all s2338 parent/child rows, and the positive
task/DMA/guest-receive/PCM/filter/render/key-on/host/callback controls. Require
positive retail whole-RDRAM/target-window/mode/gate/status/title/hangar
controls and `port_controls=1` in both arms before interpreting a port zero.
Select H-PortSeqCallerInactive only when every callsite and the entry are zero;
select H-PortSeqPartialCallsite when the callsite set is incomplete; select
H-PortSeqEntryActive when an entry is positive but the retained scheduler
entry remains zero; select H-PortSeqDispatchMismatch only for a callsite/entry
split. Otherwise report H-Unresolved without changing behavior.

## Exact commands

The retail preflight must arm whole-RDRAM and physical target-window watches,
title/hangar origins, mode/gate/status watches, callback registration
(`0x0011A8A4:0x0011A8B4`), and `--watch-pc` for `0x8008D960`,
`0x800914A4`, `0x80091564`, `0x80091618`, the retained s2338/s2339 source
PCs, and the descriptor/key-on/decode/filter/service controls.

    python3 ../rogue_squadron64/tools/make_elf.py
    (cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
    (cd ../N64Recomp && python3 fixup_game_funcs.py)
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2340_m5_scheduler_caller_reachability.sh
    zsh scratch/agent/run_s2340_m5_scheduler_caller_reachability.sh s2340_m5_scheduler_caller_reachability
