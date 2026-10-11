# Resolve pointer-backed records in the retail alternate source table
HYPOTHESIS-ID: m5-audio-destub

The s4608 oracle run passed the whole-RDRAM control (10,000 threshold), reached
the VI-512 hangar gate, and saw 76 target-span writes. The phase-gated execution
watch at `0x80007640` fired 2,079 times; caller `0x80022B44` repeatedly passed
`$a1=0x80165D9C`. The 256-byte phase snapshot at physical `0x165D9C` had 137
nonzero bytes, began with `d/proj_SND/`, and contained pointers/metadata rather
than five contiguous name records. H-flat-table is refuted; H-derived-records
versus H-other-shared-table remains.

Competing hypotheses:

- H-derived-records: the stable table base's pointer/metadata fields lead to the five records.
- H-other-shared-table: the base is staging metadata and the five records come from another RDRAM table or copy step.

Discriminating measurement: decode the pointer-sized fields in the s4608 snapshot,
then add phase-gated snapshots/watches for the first five plausible RDRAM pointer
targets. Retain `$a1`, `$a0`, and `prev_pc` rows at `0x80007640`, the whole-RDRAM
positive control, and target-span writer watch in the same run. A pointer target
containing the five records selects H-derived-records; unchanged pointer targets
with records only in a separate watched table selects H-other-shared-table. The
positive control, VI-512 phase, execution-hit count, and 76 target writes must
all be present. Do not add a mitigation.

Exact preparation/run:

1. Add bounded pointer-target snapshot/watch support to the oracle, then rebuild
   with `tools/oracle/build.sh`.
2. Run one 90-second capture with the same whole-RDRAM, target-span, and
   `0x80007640` controls, plus phase snapshots for the selected pointer targets.
   Write to `scratch/agent/s4609_retail_pointer_targets.log` using the s4608
   command line as the base.
