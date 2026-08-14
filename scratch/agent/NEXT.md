# NEXT work unit (s996)

HYPOTHESIS-ID: m4-zero-shade-destination-source-join

## One work unit

Join generated ordinary-store value/destination records to the F5
VTXCOLOR source/payload records by phase and physical address. Determine
whether a generated store writes the exact source bytes later consumed by the
zero-shade path, or whether the source remains untouched and shade becomes
zero downstream. Do not add a mitigation or hand-edit generated files.

Competing hypotheses and discriminating measurement:

- H-same-source: a generated store writes the exact VTXCOLOR source bytes.
- H-nearby-owner: generated stores touch the surrounding allocation but not
  the consumed source.
- H-downstream: the source is untouched and shade becomes zero after decode.

The discriminating measurement is an exact-address, phase-matched join of
generated-store rows and `[f5-state-payload]` rows, with the all-store, F5,
shade-DMA, write-fault, and zero-shade positive controls in the same run.
Complete coverage of the 98 target records and visible controls is required.

## Exact commands

Run the fixup static candidate-count check. Then use the documented
`make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake` order, with
`RS64_FIXUP_S992_GENERATED_WRITES=1`; the corrected target branch compares
physical addresses (`s992_phys`). Launch from `build/` with the existing
phase-gated LLE recipe:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s996_vtx_source_join_20260813 180 3`

Extract phase-4/phase-6 generated rows and F5 payload rows, join exact
physical addresses, and report whether the value changes before consumption.
Exact-source writes select H-same-source; only nearby writes select
H-nearby-owner; no generated writes at nonzero source addresses with controls
passing selects H-downstream. Any missing control or incomplete target/source
coverage is invalid.
