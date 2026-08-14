# NEXT work unit (s995)

HYPOTHESIS-ID: m4-zero-shade-writer-values

## One work unit

Extend the regeneration-owned ordinary generated-store census to capture the
assigned RHS value along with phase, guest PC, width, and effective physical
address. Regenerate, build, and run one phase-gated capture with the existing
all-store, shade, and all-DMA positive controls. Do not hand-edit generated
files or add a mitigation.

Competing hypotheses and discriminating measurement:

- H-bounded-value: target RHS values are coherent for their named record
  fields.
- H-wild-value: a target RHS is an out-of-domain pointer/index/state value.
- H-wrong-owner: values are locally coherent but the destination object is not
  the expected VTXCOLOR owner.

The discriminating measurement is a phase-gated value/destination table with
positive controls, covering target records from all 97 classified PCs. A run
without visible controls or complete target coverage is invalid.

## Exact commands

Run the fixup script's static match-count/dry-run check first. Then follow the
documented regeneration order: `make_elf.py -> N64Recomp ->
fixup_game_funcs.py -> cmake`. Launch the existing phase-gated probe recipe
from `build/` with `ROGUESQ_LOG_VTX_GENERATED_WRITES=1`, retaining its four
provenance controls and all-DMA control. Extract phase-4/phase-6 target rows
and classify RHS values by the eight s994 function groups.

Expected outcomes: bounded coherent values select H-bounded-value; an
out-of-domain value selects H-wild-value and requires identifying its writer
before any mitigation; coherent values paired with an unexpected destination
select H-wrong-owner. If the classified PC set is not covered, select no value
hypothesis and document the omission.
