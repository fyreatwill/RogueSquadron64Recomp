# NEXT work unit (s2342) — M5 musyxSynthFrame pre-gate branch census

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of the three branches
between the s2341 `musyxSynthFrame` entry and its first countdown gate:
`0x8009142C`, `0x80091454`, and `0x80091468`. Retain the s2341 parent/gate
rows, s2338–s2340 rows, the live callback-helper positive control, target-phase
route/task/DMA/guest-receive/PCM/filter/render/key-on controls, and both
stub/image arms. Add no gate, callback, slot, state, store, default, guard, or
audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the retail whole-RDRAM/target/mode-gate-status/title/
  hangar controls, requested-zero PC, callback registration, both port arms,
  or a retained same-run positive control fail.
- H-PortPreGateOuterReject: `musyxSynthFrame` entry is positive, but the
  branch at `0x8009142C` takes the outer-loop rejection path in both arms and
  neither later pre-gate branch fires.
- H-PortPreGateInnerReject: `0x8009142C` falls through, but the branch at
  `0x80091454` takes the per-iteration rejection path and `0x80091468` stays
  absent in both arms.
- H-PortPreGateB40Reject: `0x80091454` reaches its fall-through path, but the
  branch at `0x80091468` takes the B40/audio-gate bypass path before gate 1 in
  both arms.
- H-PortPreGateProbeMismatch: a pre-gate row demonstrates the fall-through
  path that reaches the first countdown gate, while the retained gate-1 row
  remains zero in the same arm and target phase.

The discriminator is one table keyed by `(arm, phase, width, origin, ordinal,
row, event, source, edge, taken, lhs, rhs, target)`, with branch rows for all
three sites, s2341 parent/gate rows, s2340 sequencer rows, s2338–s2339 rows,
retail execution counts for the three pre-gate PCs plus all retained source
PCs, and all positive controls. For each branch, `taken=1` must mean the
generated MIPS branch condition selected its skip/rejection target; record the
actual compared operands so a zero count cannot be mistaken for a classifier
failure. Require retail whole-RDRAM/target-window/mode/gate/status/title/hangar
controls, callback registration, the same-helper port control, and
`port_controls=1` in both arms before interpreting a port zero. Select
H-PortPreGateOuterReject, H-PortPreGateInnerReject, or H-PortPreGateB40Reject
only when the corresponding earlier fall-through and later branch rows split
the table in both arms. Select H-PortPreGateProbeMismatch only for a
fall-through-to-gate-1 split. Otherwise report H-Unresolved without changing
behavior.

## Exact commands

The retail preflight must arm whole-RDRAM and physical target-window watches,
title/hangar origins, mode/gate/status watches, callback registration
(`0x0011A8A4:0x0011A8B4`), and `--watch-pc` for `0x8009123C`,
`0x8009142C`, `0x80091454`, `0x80091468`, `0x80091484`, `0x80091544`,
`0x800915F8`, `0x800914A4`, `0x80091564`, `0x80091618`, all s2338–s2341
source PCs, and descriptor/key-on/decode/filter/service controls.

    python3 ../rogue_squadron64/tools/make_elf.py
    (cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
    (cd ../N64Recomp && python3 fixup_game_funcs.py)
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2342_m5_synth_pre_gate_census.sh
    zsh scratch/agent/run_s2342_m5_synth_pre_gate_census.sh s2342_m5_synth_pre_gate_census
