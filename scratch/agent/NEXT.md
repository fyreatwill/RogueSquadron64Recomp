# NEXT work unit (s997)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Join each F5 VTXCOLOR source/payload record to the zero-shade replacement and
raw-shade records in one phase-gated capture. The s996 exact join was mixed:
two phase-6 sources had exact generated writes, while the other sampled
sources—including nonzero `0x737EA0`—had no generated-store overlap. Do not add
a mitigation or hand-edit generated files.

Competing hypotheses and discriminating measurement:

- H-exact-zero-source: a zero-shade draw consumes one of the two exact source
  writes.
- H-untouched-zero-source: zero-shade draws consume untouched nonzero sources.
- H-mixed: both source populations occur, and the exact writes are unrelated
  to the zero-shade records.

The discriminating measurement is a phase-matched source-to-zero-shade join
using `[f5-state-payload]`, `[shade-raw]`, and `[fix-zero-shade]` records. The
generated-store, F5, shade-DMA, write-fault, and zero-shade controls must all
fire in the same run; missing controls or source/raw-shade rows invalidate the
result.

## Exact commands

Run the fixup static candidate-count check, then use the documented
`make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake` order with
`RS64_FIXUP_S992_GENERATED_WRITES=1`. Launch from `build/` with the existing
phase-gated LLE recipe, adding `ROGUESQ_LOG_SHADE_RAW=1`:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s997_vtx_zero_source_join_20260813 180 3`

Extract phase-4/phase-6 payload, raw-shade, zero-shade, and generated-store
rows. Join by phase and nearest F5 task/frame sequence, then check whether the
zero-shade records consume either exact source address `0x732A10` or
`0x732F38`, or only untouched nonzero sources. A zero-shade record tied to an
exact source selects H-exact-zero-source; untouched nonzero sources select
H-untouched-zero-source; both select H-mixed. If controls or source/raw-shade
coverage fail, make no causal selection.
