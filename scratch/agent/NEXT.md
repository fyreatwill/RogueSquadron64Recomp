# NEXT work unit (s2341) — M5 musyxSynthFrame parent/gate reachability

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of the source immediately
above the s2340 `tickAudioSequencerFrame` null: `musyxSynthFrame` entry
`0x8009123C` and the three countdown/gate edges immediately before its static
callsites at `0x80091484`, `0x80091544`, and `0x800915F8`. Retain callsites
`0x800914A4`, `0x80091564`, and `0x80091618`, all s2338–s2340 rows, the live
callback helper control, target-phase route/task/DMA/guest-receive/PCM/filter/
render/key-on controls, and both stub/image arms. Add no gate, callback, slot,
state, store, default, guard, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the retail parent/gate PCs, callback registration, target
  phases, both port arms, or a retained positive control fail in this capture.
- H-PortSynthInactive: `musyxSynthFrame` entry is zero despite positive retail
  `0x8009123C`, live callback-target rows, and the same-helper port control.
- H-PortSynthGateBypassed: the parent entry is positive, but all three gate
  edge rows and all three retained sequencer callsite rows are zero.
- H-PortSynthPartialGate: the parent entry is positive and only a subset of
  the three gate/callsite pairs fires; the per-site rows identify the remaining
  gate/source.
- H-PortSynthDispatchMismatch: a gate or callsite row fires while the direct
  `musyxSynthFrame` entry remains zero in the same arm and target phase; this
  selects the generated direct-call boundary for the next audit.

The discriminator is one table keyed by
`(arm, phase, width, origin, ordinal, row, event, source, edge, gate, callsite,
target)`, with retail execution counts for `0x8009123C`, all three gate PCs,
all three callsites, retained `0x8008C9AC`/`0x8008CA14`, callback
`0x80019B74`/target identity, all s2338–s2340 rows, and positive controls.
Require retail whole-RDRAM/target-window/mode/gate/status/title/hangar controls,
live callback registration, the same-helper port control, and
`port_controls=1` in both arms before interpreting a port zero. Select
H-PortSynthInactive only when the parent entry is zero in both arms. Select
H-PortSynthGateBypassed only when the entry is positive in both arms while all
three gate/callsite pairs remain zero. Select H-PortSynthPartialGate when the
entry is positive and the gate/callsite set is incomplete. Select
H-PortSynthDispatchMismatch only for a gate/callsite-to-entry split.
Otherwise report H-Unresolved without changing behavior.

## Exact commands

The retail preflight must arm whole-RDRAM and physical target-window watches,
title/hangar origins, mode/gate/status watches, callback registration
(`0x0011A8A4:0x0011A8B4`), and `--watch-pc` for `0x8009123C`,
`0x80091484`, `0x80091544`, `0x800915F8`, `0x800914A4`, `0x80091564`,
`0x80091618`, all retained source PCs, and the descriptor/key-on/decode/filter/
service controls.

    python3 ../rogue_squadron64/tools/make_elf.py
    (cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
    (cd ../N64Recomp && python3 fixup_game_funcs.py)
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2341_m5_synth_parent_gate_census.sh
    zsh scratch/agent/run_s2341_m5_synth_parent_gate_census.sh s2341_m5_synth_parent_gate_census
